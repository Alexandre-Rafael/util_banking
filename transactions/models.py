from django.db import models
from accounts.models import ContaBancariaUsuario
from transactions.constants import DEPOSITO, SAQUE, TRANSFERENCIA, TIPOS_TRANSACAO_CHOICES


class Transacao(models.Model):
    conta = models.ForeignKey(
        ContaBancariaUsuario,
        related_name='transacoes',
        on_delete=models.CASCADE,
    )
    conta_recebedora = models.ForeignKey(
        ContaBancariaUsuario,
        related_name='transacoes_recebidas',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    quantia = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    saldo_apos_transacao = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    tipo_transacao = models.PositiveSmallIntegerField(
        choices=TIPOS_TRANSACAO_CHOICES
    )
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_transacao_display()} de {self.quantia} da conta {self.conta} para a conta {self.conta_recebedora if self.conta_recebedora else 'N/A'}"

    def get_transaction_description(self):
        if self.tipo_transacao == DEPOSITO:
            return 'Depósito'
        elif self.tipo_transacao == SAQUE:
            return 'Saque'
        elif self.tipo_transacao == TRANSFERENCIA:
            if self.conta_recebedora and self.conta != self.conta_recebedora:
                return 'Transação Enviada'
            else:
                return 'Transação Recebida'
        return 'Transação'

    def is_transferencia_recebida(self):
        return self.tipo_transacao == TRANSFERENCIA and self.conta_recebedora == self.conta

    def is_transferencia_enviada(self):
        return self.tipo_transacao == TRANSFERENCIA and self.conta_recebedora != self.conta

    class Meta:
        ordering = ['data_hora']
