from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def disparar_email_teste():
    assunto = 'Teste de envio - Agenda de Reuniões'
    mensagem_texto = '''
Olá,

Este é um teste de envio de e-mail do sistema Agenda de Reuniões.

Se você recebeu esta mensagem, o SMTP está funcionando corretamente.

Atenciosamente,
Sistema Agenda de Reuniões
'''.strip()

    mensagem_html = '''
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Teste de envio - Agenda de Reuniões</h2>
            <p>Olá,</p>
            <p>Este é um <strong>teste de envio de e-mail</strong> do sistema Agenda de Reuniões.</p>
            <p>Se você recebeu esta mensagem, o SMTP está funcionando corretamente.</p>
            <p>Atenciosamente,<br>Sistema Agenda de Reuniões</p>
        </body>
    </html>
    '''

    email = EmailMultiAlternatives(
        subject=assunto,
        body=mensagem_texto,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=['mangger91@GMAIL.COM'],
    )

    email.attach_alternative(mensagem_html, 'text/html')
    email.send(fail_silently=False)

    print('E-mail enviado com sucesso.')