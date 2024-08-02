from django.contrib.auth.base_user import BaseUserManager

class GerenciadorUsuarios(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, cpf, password, **extra_fields):
        """
        Cria e salva um usuário com o e-mail, CPF e senha fornecidos.
        """
        if not email:
            raise ValueError('O e-mail deve ser fornecido')
        if not cpf:
            raise ValueError('O CPF deve ser fornecido')
        
        email = self.normalize_email(email)
        user = self.model(email=email, cpf=cpf, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, cpf=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, cpf, password, **extra_fields)

    def create_superuser(self, email, cpf=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('O superusuário deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('O superusuário deve ter is_superuser=True.')

        return self._create_user(email, cpf, password, **extra_fields)
