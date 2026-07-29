from .models import ModuloSistema
from .permissions import montar_menu, obter_perfil, usuario_tem_acesso


def layout_context(request):
    if not request.user.is_authenticated:
        return {"menu_sistema": [], "perfil_usuario": None, "notificacoes_nao_lidas": 0}

    perfil = obter_perfil(request.user)
    return {
        "menu_sistema": montar_menu(request.user),
        "perfil_usuario": perfil,
        "notificacoes_nao_lidas": request.user.notificacoes.filter(lida=False).count(),
        "pode_acessar_usuarios": usuario_tem_acesso(request.user, ModuloSistema.USUARIOS),
    }
