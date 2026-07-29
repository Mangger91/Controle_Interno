from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from sistema.models import ModuloSistema, PerfilUsuario
from sistema.permissions import obter_perfil, usuario_eh_admin

from ..common import contexto_modulo
from .forms import MinhaContaForm, PerfilUsuarioForm, UsuarioSistemaForm


User = get_user_model()


def contexto_funcoes_por_setor():
    return {"funcoes_por_setor": PerfilUsuario.funcoes_por_setor_para_json()}


def enviar_convite_acesso(request, email):
    form = PasswordResetForm(data={"email": email})
    if not form.is_valid():
        return False

    usuarios = list(form.get_users(email))
    if not usuarios:
        return False

    form.save(
        request=request,
        use_https=request.is_secure(),
        from_email=None,
        email_template_name="registration/novo_usuario_email.txt",
        subject_template_name="registration/novo_usuario_assunto.txt",
    )
    return True


@login_required
def minha_conta(request):
    perfil = obter_perfil(request.user)
    if request.method == "POST":
        usuario_form = MinhaContaForm(request.POST, instance=request.user)
        perfil_form = PerfilUsuarioForm(request.POST, instance=perfil)
        if usuario_form.is_valid() and perfil_form.is_valid():
            usuario_form.save()
            perfil_form.save()
            messages.success(request, "Seus dados foram atualizados com sucesso.")
            return redirect("minha_conta")
    else:
        usuario_form = MinhaContaForm(instance=request.user)
        perfil_form = PerfilUsuarioForm(instance=perfil)

    return render(
        request,
        "sistema/minha_conta.html",
        {
            "usuario_form": usuario_form,
            "perfil_form": perfil_form,
            "modulo_titulo": "Minha Conta",
            "modulo_descricao": "Atualize seus dados pessoais e preferencia de notificacoes.",
        },
    )


@login_required
def usuarios_lista(request):
    context = contexto_modulo(
        request,
        ModuloSistema.USUARIOS,
        "Usuarios",
        "Cadastre usuarios, niveis de perfil e permissoes por modulo.",
    )
    if context["acesso_negado"]:
        return render(request, "sistema/usuarios_lista.html", context)

    for usuario_sem_perfil in User.objects.filter(perfil__isnull=True):
        obter_perfil(usuario_sem_perfil)

    busca = request.GET.get("q", "").strip()
    setor = request.GET.get("setor", "").strip()
    funcao = request.GET.get("funcao", "").strip()
    nivel = request.GET.get("nivel", "").strip()
    status = request.GET.get("status", "").strip()

    usuarios_qs = User.objects.all().select_related("perfil")
    if busca:
        usuarios_qs = usuarios_qs.filter(
            Q(first_name__icontains=busca)
            | Q(last_name__icontains=busca)
            | Q(email__icontains=busca)
            | Q(perfil__cargo__icontains=busca)
        )
    if setor in PerfilUsuario.Setor.values:
        usuarios_qs = usuarios_qs.filter(perfil__setor=setor)
    else:
        setor = ""
    if funcao in PerfilUsuario.Funcao.values:
        usuarios_qs = usuarios_qs.filter(perfil__funcao=funcao)
    else:
        funcao = ""
    if nivel in PerfilUsuario.NivelPerfil.values:
        usuarios_qs = usuarios_qs.filter(perfil__nivel_perfil=nivel)
    else:
        nivel = ""
    if status == "ativo":
        usuarios_qs = usuarios_qs.filter(is_active=True)
    elif status == "inativo":
        usuarios_qs = usuarios_qs.filter(is_active=False)
    else:
        status = ""

    usuarios = list(usuarios_qs.order_by("first_name", "last_name", "email"))
    for usuario in usuarios:
        if not hasattr(usuario, "perfil"):
            obter_perfil(usuario)
    context["usuarios"] = usuarios
    context["filtros"] = {
        "q": busca,
        "setor": setor,
        "funcao": funcao,
        "nivel": nivel,
        "status": status,
    }
    context["setores"] = PerfilUsuario.Setor.choices
    context["funcoes"] = PerfilUsuario.Funcao.choices
    context["niveis"] = PerfilUsuario.NivelPerfil.choices
    context["total_usuarios"] = len(usuarios)
    return render(request, "sistema/usuarios_lista.html", context)


@login_required
def usuario_novo(request):
    context = contexto_modulo(
        request,
        ModuloSistema.USUARIOS,
        "Novo Usuario",
        "Somente administradores podem cadastrar novos usuarios no sistema.",
    )
    if context["acesso_negado"]:
        return render(
            request,
            "sistema/usuario_form.html",
            {**context, "form": UsuarioSistemaForm(criacao=True), **contexto_funcoes_por_setor()},
        )
    if not usuario_eh_admin(request.user, ModuloSistema.USUARIOS):
        messages.error(request, "Somente administradores podem cadastrar usuarios.")
        return redirect("usuarios_lista")

    if request.method == "POST":
        form = UsuarioSistemaForm(request.POST, criacao=True)
        if form.is_valid():
            usuario = form.save()
            if form.cleaned_data.get("enviar_convite"):
                enviado = enviar_convite_acesso(request, usuario.email)
                if enviado:
                    messages.success(request, "Usuario cadastrado e convite enviado por e-mail.")
                else:
                    messages.warning(
                        request,
                        "Usuario cadastrado, mas nao foi possivel enviar o convite por e-mail.",
                    )
            else:
                messages.success(request, "Usuario cadastrado com sucesso.")
            return redirect("usuarios_lista")
    else:
        form = UsuarioSistemaForm(criacao=True)

    return render(
        request,
        "sistema/usuario_form.html",
        {**context, "form": form, "criacao": True, **contexto_funcoes_por_setor()},
    )


@login_required
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    context = contexto_modulo(
        request,
        ModuloSistema.USUARIOS,
        "Editar Usuario",
        "Atualize dados e permissoes individuais do usuario.",
        extra={"usuario_alvo": usuario},
    )
    if context["acesso_negado"]:
        return render(
            request,
            "sistema/usuario_form.html",
            {
                **context,
                "form": UsuarioSistemaForm(instance=usuario, perfil=getattr(usuario, "perfil", None)),
                **contexto_funcoes_por_setor(),
            },
        )
    if not usuario_eh_admin(request.user, ModuloSistema.USUARIOS):
        messages.error(request, "Somente administradores podem editar usuarios.")
        return redirect("usuarios_lista")

    if request.method == "POST":
        form = UsuarioSistemaForm(
            request.POST,
            instance=usuario,
            perfil=getattr(usuario, "perfil", None),
        )
        if form.is_valid():
            usuario = form.save()
            if form.cleaned_data.get("redefinir_senha"):
                enviado = enviar_convite_acesso(request, usuario.email)
                if enviado:
                    messages.success(
                        request,
                        "Dados atualizados e e-mail para redefinicao de senha enviado.",
                    )
                else:
                    messages.warning(
                        request,
                        "Dados atualizados, mas nao foi possivel enviar e-mail de redefinicao.",
                    )
            else:
                messages.success(request, "Dados do usuario atualizados com sucesso.")
            return redirect("usuarios_lista")
    else:
        form = UsuarioSistemaForm(instance=usuario, perfil=getattr(usuario, "perfil", None))

    return render(
        request,
        "sistema/usuario_form.html",
        {
            **context,
            "form": form,
            "usuario_alvo": usuario,
            "criacao": False,
            **contexto_funcoes_por_setor(),
        },
    )
