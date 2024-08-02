from django.urls import path
from .views import DepositarDinheiroView, SacarDinheiroView, RelatorioTransacoesView, TransferirDinheiroView

app_name = 'transacoes'

urlpatterns = [
    path('deposito/', DepositarDinheiroView.as_view(), name='depositar_dinheiro'),
    path('saque/', SacarDinheiroView.as_view(), name='sacar_dinheiro'),
    path('relatorio/', RelatorioTransacoesView.as_view(), name='relatorio_transacoes'),
    path('transferencia/', TransferirDinheiroView.as_view(), name='transferir_dinheiro'),
]
