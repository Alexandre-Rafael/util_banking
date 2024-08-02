from django.contrib import admin
from django.urls import include, path

from core.views import VisualizacaoInicio

urlpatterns = [
    path('', VisualizacaoInicio.as_view(), name='inicio'),
    path('contas/', include('accounts.urls', namespace='contas')),
    path('admin/', admin.site.urls),
    path('transacoes/', include('transactions.urls', namespace='transactions')),
]
