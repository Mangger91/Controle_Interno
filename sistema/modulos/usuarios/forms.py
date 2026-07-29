import secrets

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from sistema.models import PapelAcesso, PerfilUsuario


FORM_CONTROL = {"class": "form-control"}


class LoginEmailForm(AuthenticationForm):
    username = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                **FORM_CONTROL,
                "placeholder": "voce@empresa.com.br",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                **FORM_CONTROL,
                "placeholder": "Digite sua senha",
            }
        ),
    )


class MinhaContaForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={**FORM_CONTROL, "placeholder": "Nome"}),
            "last_name": forms.TextInput(attrs={**FORM_CONTROL, "placeholder": "Sobrenome"}),
            "email": forms.EmailInput(attrs={**FORM_CONTROL, "placeholder": "email@empresa.com"}),
        }

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ja existe outro usuario cadastrado com este e-mail.")
        return email


class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ["cargo", "receber_email_notificacao"]
        widgets = {
            "cargo": forms.TextInput(attrs={**FORM_CONTROL, "placeholder": "Cargo ou area"}),
            "receber_email_notificacao": forms.CheckboxInput(attrs={"class": "checkbox-control"}),
        }


class UsuarioSistemaForm(forms.ModelForm):
    nivel_perfil = forms.ChoiceField(
        label="Nivel de perfil",
        choices=PerfilUsuario.NivelPerfil.choices,
        widget=forms.Select(attrs=FORM_CONTROL),
    )
    setor = forms.ChoiceField(
        label="Setor",
        choices=[("", "Selecione")] + list(PerfilUsuario.Setor.choices),
        widget=forms.Select(attrs=FORM_CONTROL),
    )
    funcao = forms.ChoiceField(
        label="Funcao",
        choices=[("", "Selecione")] + list(PerfilUsuario.Funcao.choices),
        widget=forms.Select(attrs=FORM_CONTROL),
    )
    cargo = forms.CharField(
        label="Cargo",
        required=False,
        widget=forms.TextInput(attrs={**FORM_CONTROL, "placeholder": "Cargo ou area"}),
    )
    receber_email_notificacao = forms.BooleanField(
        label="Receber e-mails de notificacao",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "checkbox-control"}),
    )
    papel_usuarios = forms.ChoiceField(
        label="Permissao no modulo Usuarios",
        choices=PapelAcesso.choices,
        widget=forms.Select(attrs=FORM_CONTROL),
    )
    papel_agenda = forms.ChoiceField(
        label="Permissao no modulo Agenda de Reunioes",
        choices=PapelAcesso.choices,
        widget=forms.Select(attrs=FORM_CONTROL),
    )
    papel_rota_motoboy = forms.ChoiceField(
        label="Permissao no modulo Rota do MotoBoy",
        choices=PapelAcesso.choices,
        widget=forms.Select(attrs=FORM_CONTROL),
    )
    papel_chamados_ti = forms.ChoiceField(
        label="Permissao no modulo Abrir Chamado",
        choices=PapelAcesso.choices,
        widget=forms.Select(attrs=FORM_CONTROL),
    )
    papel_estoque_adm = forms.ChoiceField(
        label="Permissao no modulo Estoque ADM",
        choices=PapelAcesso.choices,
        widget=forms.Select(attrs=FORM_CONTROL),
    )
    papel_estoque_ti = forms.ChoiceField(
        label="Permissao no modulo Estoque TI",
        choices=PapelAcesso.choices,
        widget=forms.Select(attrs=FORM_CONTROL),
    )
    papel_estoque_expediente = forms.ChoiceField(
        label="Permissao no modulo Estoque Expediente",
        choices=PapelAcesso.choices,
        widget=forms.Select(attrs=FORM_CONTROL),
    )
    papel_avaliacao = forms.ChoiceField(
        label="Permissao no modulo Avaliacao de Colaboradores",
        choices=PapelAcesso.choices,
        widget=forms.Select(attrs=FORM_CONTROL),
    )
    enviar_convite = forms.BooleanField(
        label="Enviar convite de acesso por e-mail",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "checkbox-control"}),
    )
    redefinir_senha = forms.BooleanField(
        label="Enviar e-mail para redefinir senha",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "checkbox-control"}),
    )

    CAMPOS_PERFIL = (
        "nivel_perfil",
        "setor",
        "funcao",
        "cargo",
        "receber_email_notificacao",
        "papel_usuarios",
        "papel_agenda",
        "papel_rota_motoboy",
        "papel_chamados_ti",
        "papel_estoque_adm",
        "papel_estoque_ti",
        "papel_estoque_expediente",
        "papel_avaliacao",
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "is_active"]
        widgets = {
            "first_name": forms.TextInput(attrs={**FORM_CONTROL, "placeholder": "Nome"}),
            "last_name": forms.TextInput(attrs={**FORM_CONTROL, "placeholder": "Sobrenome"}),
            "email": forms.EmailInput(attrs={**FORM_CONTROL, "placeholder": "email@empresa.com"}),
            "is_active": forms.CheckboxInput(attrs={"class": "checkbox-control"}),
        }
        labels = {"is_active": "Usuario ativo"}

    def __init__(self, *args, perfil=None, criacao=False, **kwargs):
        self.perfil = perfil
        self.criacao = criacao
        super().__init__(*args, **kwargs)

        if self.criacao:
            self.fields.pop("redefinir_senha")
        else:
            self.fields.pop("enviar_convite")

        perfil = self.perfil
        if perfil is None and self.instance and self.instance.pk:
            perfil = getattr(self.instance, "perfil", None)

        if perfil:
            for campo in self.CAMPOS_PERFIL:
                self.fields[campo].initial = getattr(perfil, campo)

        setor_selecionado = self._setor_selecionado(perfil)
        self._atualizar_funcoes_do_setor(setor_selecionado)

    def _setor_selecionado(self, perfil):
        if self.is_bound:
            return self.data.get(self.add_prefix("setor"), "")
        if perfil:
            return perfil.setor
        return ""

    def _atualizar_funcoes_do_setor(self, setor):
        escolhas = [("", "Selecione")]
        if setor:
            escolhas += PerfilUsuario.funcoes_choices_por_setor(setor)
        self.fields["funcao"].choices = escolhas

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ja existe outro usuario cadastrado com este e-mail.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        nivel = cleaned_data.get("nivel_perfil")
        papel_usuarios = cleaned_data.get("papel_usuarios")
        setor = cleaned_data.get("setor")
        funcao = cleaned_data.get("funcao")

        if nivel == PerfilUsuario.NivelPerfil.ADMINISTRADOR and papel_usuarios != PapelAcesso.ADMINISTRADOR:
            self.add_error(
                "papel_usuarios",
                "Para nivel Administrador, defina permissao Administrador no modulo Usuarios.",
            )
        if setor and funcao and funcao not in PerfilUsuario.funcoes_por_setor(setor):
            self.add_error(
                "funcao",
                "A funcao selecionada nao pertence ao modelo deste setor.",
            )
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data["email"]
        usuario.username = self.cleaned_data["email"]
        if self.criacao and not usuario.has_usable_password():
            usuario.set_password(secrets.token_urlsafe(24))

        if commit:
            usuario.save()

        perfil, _ = PerfilUsuario.objects.get_or_create(usuario=usuario)
        for campo in self.CAMPOS_PERFIL:
            setattr(perfil, campo, self.cleaned_data[campo])
        if commit:
            perfil.save()
        self.perfil = perfil
        return usuario
