from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        identificador = (username or kwargs.get("email") or "").strip()
        if not identificador or not password:
            return None

        usuario = User.objects.filter(email__iexact=identificador).first()

        if usuario and usuario.check_password(password) and self.user_can_authenticate(usuario):
            return usuario
        return None
