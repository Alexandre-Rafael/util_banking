from django.contrib import messages
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView
from transactions.constants import DEPOSITO, SAQUE, TRANSFERENCIA
from transactions.forms import FormularioDeposito, FormularioSaque, FormularioTransferencia, FormularioIntervaloDatasTransacao
from transactions.models import Transacao
from accounts.models import ContaBancariaUsuario
from django.db import models, transaction
from django.db.models import Q

class RelatorioTransacoesView(LoginRequiredMixin, ListView):
    template_name = 'transactions/relatorio.html'
    model = Transacao
    dados_formulario = {}

    def get(self, request, *args, **kwargs):
        formulario = FormularioIntervaloDatasTransacao(request.GET or None)
        if formulario.is_valid():
            self.dados_formulario = formulario.cleaned_data

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            Q(conta=self.request.user.conta) |
            Q(conta_recebedora=self.request.user.conta)
        )

        intervalo_datas = self.dados_formulario.get("intervalo_datas")

        if intervalo_datas:
            queryset = queryset.filter(data_hora__date__range=intervalo_datas)

        queryset = queryset.order_by('data_hora')

        return queryset

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update({
            'conta': self.request.user.conta,
            'formulario': FormularioIntervaloDatasTransacao(self.request.GET or None)
        })

        # Adiciona lógica para identificar quem enviou ou recebeu a transação
        for transacao in contexto['object_list']:
            transacao.tipo_transacao_display = transacao.get_transaction_description()

        return contexto

class CriarTransacaoMixin(LoginRequiredMixin, CreateView):
    model = Transacao
    titulo = ''
    success_url = reverse_lazy('transacoes:relatorio_transacoes')  # Define a URL de sucesso

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'conta': self.request.user.conta
        })
        return kwargs

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update({
            'titulo': self.titulo,
            'usuario': self.request.user,
            'saldo': self.request.user.conta.saldo,
        })

        return contexto


class DepositarDinheiroView(CriarTransacaoMixin):
    form_class = FormularioDeposito
    template_name = 'transactions/formulario_deposito.html'
    titulo = 'Depositar Dinheiro na Sua Conta'

    def get_initial(self):
        inicial = {'tipo_transacao': DEPOSITO}
        return inicial

    @transaction.atomic
    def form_valid(self, form):
        quantia = form.cleaned_data.get('quantia')
        conta = self.request.user.conta

        # Verifica a versão antes de atualizar
        versao_atual = conta.versao
        rows_updated = ContaBancariaUsuario.objects.filter(
            pk=conta.pk,
            versao=versao_atual
        ).update(
            saldo=models.F('saldo') + quantia,
            versao=models.F('versao') + 1
        )

        if rows_updated == 0:
            # Se nenhuma linha foi atualizada, significa que houve um conflito de versão
            messages.error(self.request, 'Conflito de versão detectado. Por favor, tente novamente.')
            return self.form_invalid(form)

        # Recarrega a instância da conta com os valores atualizados
        conta.refresh_from_db()

        # Cria a transação para o depósito
        Transacao.objects.create(
            conta=conta,
            quantia=quantia,
            saldo_apos_transacao=conta.saldo,  # Usando o saldo atualizado
            tipo_transacao=DEPOSITO,
            data_hora=timezone.now()
        )

        messages.success(
            self.request,
            f'R$ {quantia} foi depositado na sua conta com sucesso'
        )

        return self.render_to_response(self.get_context_data(form=form))


class SacarDinheiroView(CriarTransacaoMixin):
    form_class = FormularioSaque
    template_name = 'transactions/formulario_saque.html'
    titulo = 'Sacar Dinheiro da Sua Conta'

    def get_initial(self):
        inicial = {'tipo_transacao': SAQUE}
        return inicial

    @transaction.atomic
    def form_valid(self, form):
        quantia = form.cleaned_data.get('quantia')
        conta = self.request.user.conta

        if conta.saldo < quantia:
            messages.error(self.request, 'Fundos insuficientes')
            return self.form_invalid(form)

        # Verifica a versão antes de atualizar
        versao_atual = conta.versao
        rows_updated = ContaBancariaUsuario.objects.filter(
            pk=conta.pk,
            versao=versao_atual
        ).update(
            saldo=models.F('saldo') - quantia,
            versao=models.F('versao') + 1
        )

        if rows_updated == 0:
            # Se nenhuma linha foi atualizada, significa que houve um conflito de versão
            messages.error(self.request, 'Conflito de versão detectado. Por favor, tente novamente.')
            return self.form_invalid(form)

        # Recarrega a instância da conta com os valores atualizados
        conta.refresh_from_db()

        # Criar a transação
        Transacao.objects.create(
            conta=conta,
            quantia=-quantia,
            saldo_apos_transacao=conta.saldo,  # Usando o saldo atualizado
            tipo_transacao=SAQUE,
            data_hora=timezone.now()
        )

        messages.success(
            self.request,
            f'R$ {quantia} foi sacado da sua conta com sucesso'
        )

        return self.render_to_response(self.get_context_data(form=form))



class TransferirDinheiroView(LoginRequiredMixin, FormView):
    form_class = FormularioTransferencia
    template_name = 'transactions/formulario_transferencia.html'
    titulo = 'Transferir Dinheiro'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['conta'] = self.request.user.conta  # Passa a conta do usuário atual
        return kwargs

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = self.titulo
        contexto.update({
            'usuario': self.request.user,
            'saldo': self.request.user.conta.saldo,
        })
        return contexto

    @transaction.atomic
    def form_valid(self, form):
        quantia = form.cleaned_data.get('quantia')
        cpf_recebedor = form.cleaned_data.get('cpf_recebedor')
        conta_origem = self.request.user.conta

        try:
            conta_recebedora = ContaBancariaUsuario.objects.get(numero_conta=cpf_recebedor)
        except ContaBancariaUsuario.DoesNotExist:
            messages.error(self.request, 'A conta do recebedor não existe.')
            return self.form_invalid(form)

        if quantia > conta_origem.saldo:
            messages.error(self.request, 'Fundos insuficientes.')
            return self.form_invalid(form)

        # Processar a transferência com verificação de versão para ambas as contas
        versao_origem = conta_origem.versao
        versao_recebedora = conta_recebedora.versao

        rows_updated_origem = ContaBancariaUsuario.objects.filter(
            pk=conta_origem.pk,
            versao=versao_origem
        ).update(
            saldo=models.F('saldo') - quantia,
            versao=models.F('versao') + 1
        )

        rows_updated_recebedora = ContaBancariaUsuario.objects.filter(
            pk=conta_recebedora.pk,
            versao=versao_recebedora
        ).update(
            saldo=models.F('saldo') + quantia,
            versao=models.F('versao') + 1
        )

        if rows_updated_origem == 0 or rows_updated_recebedora == 0:
            messages.error(self.request, 'Conflito de versão detectado. Por favor, tente novamente.')
            return self.form_invalid(form)

        # Recarrega as instâncias das contas com os valores atualizados
        conta_origem.refresh_from_db()
        conta_recebedora.refresh_from_db()

        # Criar a transação de envio (para a conta origem)
        Transacao.objects.create(
            conta=conta_origem,
            conta_recebedora=conta_recebedora,
            quantia=-quantia,
            saldo_apos_transacao=conta_origem.saldo,
            tipo_transacao=TRANSFERENCIA,
            data_hora=timezone.now()
        )
        # Criar a transação de recebimento (para a conta recebedora)
        Transacao.objects.create(
            conta=conta_recebedora,
            quantia=quantia,
            saldo_apos_transacao=conta_recebedora.saldo,
            tipo_transacao=TRANSFERENCIA,
            data_hora=timezone.now()
        )

        messages.success(self.request, f'R$ {quantia} foi transferido com sucesso para o CPF {cpf_recebedor}')

        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, 'Houve um erro ao processar sua transferência.')
        return super().form_invalid(form)
