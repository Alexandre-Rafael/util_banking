from django.contrib.auth.models import AbstractUser
from django.db import models
from .constants import OPCOES_GENERO
from .managers import GerenciadorUsuarios

class Usuario(AbstractUser):
    username = None  # Removendo o campo username
    cpf = models.CharField(max_length=11, unique=True, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)

    objetos = GerenciadorUsuarios()

    USERNAME_FIELD = 'email'  # Usando e-mail como campo de login
    REQUIRED_FIELDS = ['cpf']  # CPF é requerido junto com o e-mail

    def __str__(self):
        return self.email


class ContaBancariaUsuario(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        related_name='conta',
        on_delete=models.CASCADE,
    )
    numero_conta = models.CharField(max_length=11, unique=True)  # Mantém o CPF como número da conta
    genero = models.CharField(max_length=1, choices=OPCOES_GENERO)
    data_nascimento = models.DateField(null=True, blank=True)
    saldo = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )
    data_inicio_juros = models.DateField(
        null=True, blank=True,
        help_text='O número do mês que o cálculo de juros começará'
    )
    data_deposito_inicial = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Aqui garantimos que o CPF seja utilizado como número da conta, caso não esteja definido
        if not self.numero_conta:
            self.numero_conta = self.usuario.cpf  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Conta {self.numero_conta} de {self.usuario.email}"
