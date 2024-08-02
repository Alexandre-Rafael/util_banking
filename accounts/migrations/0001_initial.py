from django.db import migrations, models
import accounts.managers

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('senha', models.CharField(max_length=128, verbose_name='password')),
                ('ultimo_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('eh_superusuario', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('primeiro_nome', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('ultimo_nome', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('grupos', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('permissoes_usuarios', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'usuario',
                'verbose_name_plural': 'usuarios',
            },
            managers=[
                ('objetos', accounts.managers.GerenciadorUsuarios()),
            ],
        ),
        migrations.CreateModel(
            name='ContaBancariaUsuario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_conta', models.PositiveIntegerField(unique=True)),
                ('genero', models.CharField(choices=[('M', 'Masculino'), ('F', 'Feminino')], max_length=1)),
                ('data_nascimento', models.DateField(blank=True, null=True)),
                ('saldo', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('data_deposito_inicial', models.DateField(blank=True, null=True)),
                ('usuario', models.OneToOneField(on_delete=models.CASCADE, related_name='conta', to='accounts.Usuario')),
            ],
        ),
    ]
