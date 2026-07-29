from django.shortcuts import render

from sistema.models import PapelAcesso
from sistema.permissions import (
    papel_do_usuario,
    usuario_pode_editar,
    usuario_pode_excluir,
    usuario_tem_acesso,
)


MESES_PT_BR = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Marco",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


def contexto_modulo(request, modulo, titulo, descricao, extra=None):
    papel = papel_do_usuario(request.user, modulo)
    context = {
        "modulo_codigo": modulo,
        "modulo_titulo": titulo,
        "modulo_descricao": descricao,
        "papel_modulo": papel,
        "papel_modulo_label": PapelAcesso(papel).label if papel in PapelAcesso.values else str(papel),
        "permite_edicao": usuario_pode_editar(request.user, modulo),
        "permite_exclusao": usuario_pode_excluir(request.user, modulo),
        "acesso_negado": not usuario_tem_acesso(request.user, modulo),
    }
    if extra:
        context.update(extra)
    return context


def renderizar_modulo_sem_permissao(request, modulo, titulo, descricao, template, extra=None):
    context = contexto_modulo(request, modulo, titulo, descricao, extra=extra)
    return render(request, template, context)
