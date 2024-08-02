from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView

from .forms import FormularioRegistroUsuario

Usuario = get_user_model()

class VisualizacaoRegistroUsuario(TemplateView):
    model = Usuario
    form_class = FormularioRegistroUsuario
    template_name = 'accounts/cadastro.html'

    def get_success_url(self):
        return reverse_lazy('transactions:deposito')  # Certifique-se de que o nome esteja correto aqui

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(
                reverse_lazy('transactions:relatorio_transacoes')
            )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        formulario_registro = FormularioRegistroUsuario(self.request.POST)

        if formulario_registro.is_valid():
            usuario = formulario_registro.save()

            login(self.request, usuario)
            messages.success(
                self.request,
                (
                    f'Obrigado por criar uma conta bancária. '
                    f'Seu número de conta é {usuario.conta.numero_conta}. '
                )
            )
            return HttpResponseRedirect(
                reverse_lazy('transactions:depositar_dinheiro')
            )

        return self.render_to_response(
            self.get_context_data(
                registration_form=formulario_registro  # Corrigi o nome aqui
            )
        )

    def get_context_data(self, **kwargs):
        if 'registration_form' not in kwargs:  # Corrigi o nome aqui
            kwargs['registration_form'] = FormularioRegistroUsuario()

        return super().get_context_data(**kwargs)

class VisualizacaoLoginUsuario(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

class VisualizacaoLogout(RedirectView):
    pattern_name = 'inicio'

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
        return super().get_redirect_url(*args, **kwargs)
