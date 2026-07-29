from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from sistema.models import ItemEstoque, ModuloSistema, Notificacao, Reuniao
from sistema.permissions import MODULOS_SISTEMA

from ..agenda.services import obter_reunioes_do_usuario
from ..common import renderizar_modulo_sem_permissao


@login_required
def dashboard(request):
    reunioes = obter_reunioes_do_usuario(request.user)
    itens_estoque = ItemEstoque.objects.filter(ativo=True)
    context = {
        "modulos": MODULOS_SISTEMA,
        "total_reunioes": reunioes.count(),
        "proximas_reunioes": reunioes.filter(
            data__gte=date.today(),
            status=Reuniao.Status.AGENDADA,
        ).count(),
        "itens_estoque_baixo": itens_estoque.filter(quantidade_atual__lte=0).count()
        + sum(1 for item in itens_estoque if item.estoque_baixo and item.quantidade_atual > 0),
        "notificacoes_recentes": request.user.notificacoes.all()[:5],
    }
    return render(request, "sistema/dashboard.html", context)


@login_required
def central_notificacoes(request):
    notificacoes = request.user.notificacoes.all()
    return render(
        request,
        "sistema/notificacoes.html",
        {
            "notificacoes": notificacoes,
            "modulo_titulo": "Notificacoes",
            "modulo_descricao": "Avisos internos sobre agenda e operacoes do sistema.",
        },
    )


@login_required
def abrir_notificacao(request, pk):
    notificacao = get_object_or_404(Notificacao, pk=pk, destinatario=request.user)
    if not notificacao.lida:
        notificacao.lida = True
        notificacao.lida_em = timezone.now()
        notificacao.save(update_fields=["lida", "lida_em"])
    if notificacao.url_destino:
        return redirect(notificacao.url_destino)
    return redirect("central_notificacoes")


@login_required
def modulo_placeholder(request, modulo, titulo, descricao):
    return renderizar_modulo_sem_permissao(
        request,
        modulo,
        titulo,
        descricao,
        "sistema/modulo_placeholder.html",
    )


@login_required
def avaliacao_colaboradores(request):
    return modulo_placeholder(
        request,
        ModuloSistema.AVALIACAO,
        "Avaliacao de Colaboradores",
        "Base pronta para evoluirmos ciclos, metas, feedbacks e historico por colaborador.",
    )


@login_required
def chamados_ti(request):
    return modulo_placeholder(
        request,
        ModuloSistema.CHAMADOS_TI,
        "Chamados - TI",
        "Espaco inicial para fila de chamados, prioridades e acompanhamento de resolucao.",
    )
