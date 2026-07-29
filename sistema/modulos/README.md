# Estrutura dos modulos

Este diretorio organiza o sistema por area de negocio. O app Django continua se chamando
`sistema` para preservar banco, migrations e configuracoes existentes.

- `agenda/`: agenda de reunioes, participantes, notificacoes e envio de e-mail de reuniao.
- `estoque/`: regras, formularios e telas dos estoques ADM e TI.
- `rota_motoboy/`: cadastro de rotas e paradas.
- `usuarios/`: autenticacao por e-mail, minha conta e administracao de usuarios/perfis.
- `core/`: dashboard, notificacoes gerais e placeholders de modulos ainda em evolucao.

Arquivos antigos como `sistema/views.py`, `sistema/forms.py` e `sistema/estoque.py`
ficaram como fachadas de compatibilidade. Codigo novo deve ser criado dentro da pasta do
modulo correspondente.
