from django.test import TestCase
from accounts.models import ContaBancariaUsuario, Usuario
from django.db.utils import IntegrityError

class TesteBloqueioOtimista(TestCase):

    def setUp(self):
        # Configure uma conta bancária de exemplo para os testes
        self.usuario = Usuario.objetos.create_user(
            email='teste@example.com',
            cpf='12345678901',
            password='senha'
        )
        self.conta = ContaBancariaUsuario.objects.create(
            usuario=self.usuario, 
            saldo=1000, 
            versao=1
        )

    def test_concorrencia_atualizacao_sucesso(self):
        # Simular a leitura inicial em duas transações diferentes
        conta1 = ContaBancariaUsuario.objects.get(pk=self.conta.pk)
        conta2 = ContaBancariaUsuario.objects.get(pk=self.conta.pk)

        # Atualizar em uma transação
        conta1.saldo += 100
        conta1.save()  # Isso deve funcionar normalmente

        # Tentar atualizar na outra transação
        conta2.saldo += 200
        with self.assertRaises(IntegrityError):
            conta2.save()

        # Recarregar do banco de dados e verificar o saldo correto
        conta_atualizada = ContaBancariaUsuario.objects.get(pk=self.conta.pk)
        self.assertEqual(conta_atualizada.saldo, 1100)
