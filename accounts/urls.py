from django.urls import path
from .views import VisualizacaoRegistroUsuario, VisualizacaoLogout, VisualizacaoLoginUsuario

app_name = 'contas'

urlpatterns = [
    path(
        "entrar/", VisualizacaoLoginUsuario.as_view(),
        name="login_usuario"
    ),
    path(
        "sair/", VisualizacaoLogout.as_view(),
        name="logout_usuario"
    ),
    path(
        "registrar/", VisualizacaoRegistroUsuario.as_view(),
        name="registro_usuario"
    ),
]
