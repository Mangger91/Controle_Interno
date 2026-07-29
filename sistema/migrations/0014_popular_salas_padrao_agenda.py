from django.db import migrations


SALAS_PADRAO = [
    ("Sala Jefferson", "Sala interna", 12),
    ("Sala Ozeias", "Sala interna", 12),
    ("Online", "Ambiente virtual", 100),
    ("Externo", "Fora da empresa", 100),
]


def popular_salas_padrao(apps, schema_editor):
    Sala = apps.get_model("reunioes", "Sala")

    for nome, localizacao, capacidade in SALAS_PADRAO:
        sala = Sala.objects.filter(nome=nome).first()

        if sala:
            campos = []
            if not sala.localizacao:
                sala.localizacao = localizacao
                campos.append("localizacao")
            if not sala.capacidade:
                sala.capacidade = capacidade
                campos.append("capacidade")
            if not sala.ativa:
                sala.ativa = True
                campos.append("ativa")
            if campos:
                sala.save(update_fields=campos)
            continue

        Sala.objects.create(
            nome=nome,
            localizacao=localizacao,
            capacidade=capacidade,
            ativa=True,
        )


def manter_salas_ao_reverter(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("reunioes", "0013_rotaparada_horario_previsto_and_more"),
    ]

    operations = [
        migrations.RunPython(popular_salas_padrao, manter_salas_ao_reverter),
    ]
