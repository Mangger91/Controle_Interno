# Primeiro deploy

Este projeto ja esta preparado para um primeiro deploy interno controlado em
Windows usando Django, SQLite, WhiteNoise e Waitress.

O ambiente inicial definido e:

```text
http://192.168.100.233:1200
```

## Antes de subir

1. Crie o ambiente virtual: `python -m venv venv`.
2. Copie `.env.production.example` para `.env` no servidor.
3. Gere uma `DJANGO_SECRET_KEY` nova.
4. Confirme `DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,192.168.100.233`.
5. Confirme `DJANGO_CSRF_TRUSTED_ORIGINS=http://192.168.100.233:1200`.
6. Ajuste `DJANGO_SQLITE_PATH` para um caminho persistente fora do codigo.
7. Configure as variaveis de e-mail se o sistema for enviar mensagens.

Para gerar uma chave localmente:

```powershell
.\venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Base zerada

Nao copie `db.sqlite3` para producao. No servidor, rode:

```powershell
.\deploy\primeiro_deploy_windows.ps1
.\venv\Scripts\python.exe manage.py createsuperuser
```

As migrations criam as tabelas e dados padrao previstos pelo sistema.

## Iniciar o servidor

```powershell
.\deploy\start_waitress.ps1
```

Por padrao ele escuta em `0.0.0.0:1200`, permitindo acesso pela rede no IP
`192.168.100.233`.

## HTTPS

Para acesso publico futuro, coloque o Waitress atras de um proxy com HTTPS
(IIS, Nginx, Caddy ou outro proxy da infraestrutura). Mantenha:

```env
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
```

Para este ambiente interno inicial sem HTTPS, esses tres valores ficam `False`.
Com isso, `manage.py check --deploy` pode exibir avisos de HTTPS. Eles sao
esperados neste primeiro acesso interno por HTTP.

## Atualizacoes futuras

No servidor, depois de enviar uma nova versao do codigo:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py collectstatic --noinput
```

Depois reinicie o processo do Waitress.
