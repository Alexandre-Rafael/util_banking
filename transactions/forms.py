import datetime
from django import forms
from django.conf import settings
from .models import Transacao
from accounts.models import ContaBancariaUsuario

class FormularioTransacao(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = [
            'quantia',
            'tipo_transacao'
        ]

    def __init__(self, *args, **kwargs):
        self.conta = kwargs.pop('conta', None)
        super().__init__(*args, **kwargs)

        if self.conta is not None:
            self.fields['tipo_transacao'].initial = self.initial.get('tipo_transacao', None)
            self.fields['tipo_transacao'].disabled = True
            self.fields['tipo_transacao'].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.conta = self.conta
        self.instance.saldo_apos_transacao = self.conta.saldo
        return super().save(commit=commit)

class FormularioDeposito(FormularioTransacao):
    def clean_quantia(self):
        quantia_minima_deposito = settings.MINIMUM_DEPOSIT_AMOUNT
        quantia = self.cleaned_data.get('quantia')

        if quantia < quantia_minima_deposito:
            raise forms.ValidationError(
                f'Você precisa depositar pelo menos {quantia_minima_deposito} R$'
            )

        return quantia

class FormularioSaque(FormularioTransacao):
    def clean_quantia(self):
        quantia_minima_saque = settings.MINIMUM_WITHDRAWAL_AMOUNT
        saldo = self.conta.saldo

        quantia = self.cleaned_data.get('quantia')

        if quantia < quantia_minima_saque:
            raise forms.ValidationError(
                f'Você pode sacar pelo menos {quantia_minima_saque} R$'
            )

        if quantia > saldo:
            raise forms.ValidationError(
                f'Você tem {saldo} R$ na sua conta. '
                'Você não pode sacar mais do que o saldo da sua conta'
            )

        return quantia

class FormularioTransferencia(forms.Form):
    cpf_recebedor = forms.CharField(max_length=11, label="CPF do Recebedor")
    quantia = forms.DecimalField(decimal_places=2, max_digits=12, label="Quantia")

    def __init__(self, *args, **kwargs):
        self.conta = kwargs.pop('conta', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        dados_limpos = super().clean()
        quantia = dados_limpos.get('quantia')
        cpf_recebedor = dados_limpos.get('cpf_recebedor')

        if self.conta:
            if quantia and quantia <= 0:
                self.add_error('quantia', 'A quantia deve ser positiva.')
            if cpf_recebedor and self.conta.usuario.cpf == cpf_recebedor:
                self.add_error('cpf_recebedor', 'Não é possível transferir para a mesma conta.')

        if cpf_recebedor:
            try:
                # Usando usuario__cpf para buscar o CPF do usuário relacionado
                conta_recebedora = ContaBancariaUsuario.objects.get(usuario__cpf=cpf_recebedor)
            except ContaBancariaUsuario.DoesNotExist:
                self.add_error('cpf_recebedor', 'A conta do recebedor não existe.')

        return dados_limpos

class FormularioIntervaloDatasTransacao(forms.Form):
    intervalo_datas = forms.CharField(required=False)

    def clean_intervalo_datas(self):
        intervalo_datas = self.cleaned_data.get("intervalo_datas")

        try:
            intervalo_datas = intervalo_datas.split(' - ')
            if len(intervalo_datas) == 2:
                for date in intervalo_datas:
                    datetime.datetime.strptime(date, '%Y-%m-%d')
                return intervalo_datas
            else:
                raise forms.ValidationError("Por favor, selecione um intervalo de datas.")
        except (ValueError, AttributeError):
            raise forms.ValidationError("Intervalo de datas inválido")
