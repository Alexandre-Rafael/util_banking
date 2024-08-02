from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import Usuario, ContaBancariaUsuario
from .constants import OPCOES_GENERO
from django.conf import settings

class FormularioRegistroUsuario(UserCreationForm):
    primeiro_nome = forms.CharField(
        max_length=30, 
        required=True, 
        help_text="Digite seu primeiro nome", 
        label="Primeiro Nome"
    )
    sobrenome = forms.CharField(
        max_length=30, 
        required=True, 
        help_text="Digite seu sobrenome", 
        label="Sobrenome"
    )
    cpf = forms.CharField(
        max_length=11, 
        required=True, 
        help_text="Digite seu CPF sem pontos ou traços", 
        label="CPF"
    )
    genero = forms.ChoiceField(
        choices=OPCOES_GENERO, 
        label="Gênero"
    )
    data_nascimento = forms.DateField(
        label="Data de Nascimento"
    )

    class Meta:
        model = Usuario
        fields = [
            'primeiro_nome',  # Adicionando o primeiro nome
            'sobrenome',      # Adicionando o sobrenome
            'cpf',
            'email',
            'password1',
            'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 '
                    'rounded py-3 px-4 leading-tight '
                    'focus:outline-none focus:bg-white '
                    'focus:border-gray-500'
                )
            })

    @transaction.atomic
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password1"])
        usuario.first_name = self.cleaned_data["primeiro_nome"]  # Salvando o primeiro nome
        usuario.last_name = self.cleaned_data["sobrenome"]       # Salvando o sobrenome
        usuario.cpf = self.cleaned_data["cpf"]  # Salvando o CPF
        if commit:
            usuario.save()
            genero = self.cleaned_data.get('genero')
            data_nascimento = self.cleaned_data.get('data_nascimento')

            ContaBancariaUsuario.objects.create(
                usuario=usuario,
                genero=genero,
                data_nascimento=data_nascimento,
                numero_conta=usuario.cpf  # Usando o CPF como número da conta
            )
        return usuario
