README - Projeto `util_bank`

Introdução
----------

Este projeto é um sistema bancário simples desenvolvido em Django, que inclui funcionalidades como depósito, saque e transferência entre contas. O projeto foi configurado para suportar balanceamento de carga utilizando NGINX, garantindo escalabilidade e distribuição de tráfego. Além disso, foram implementadas técnicas de atomicidade e bloqueio otimista para garantir a integridade das transações bancárias.

Pré-requisitos
--------------

Certifique-se de ter os seguintes pré-requisitos instalados no seu sistema:

- **Python 3.8 ou superior**
- **Git**
- **NGINX** (Você pode baixar o NGINX em: https://nginx.org/en/download.html)
- **Virtualenv** (para criar ambientes virtuais)

Passos para Configuração
------------------------

1. Clone o Repositório

   Clone o repositório do projeto para o seu diretório local:

git clone https://github.com/Alexandre-Rafael/util_banking.git
cd util_banking


2. Crie um Ambiente Virtual

Dentro do diretório do projeto, crie e ative um ambiente virtual:

Criar o ambiente virtual
python -m venv venv

Ativar o ambiente virtual no Windows
venv\Scripts\activate

Ativar o ambiente virtual no Linux/MacOS
source venv/bin/activate



3. Instale as Dependências

Com o ambiente virtual ativado, instale as dependências do projeto:

pip install -r requirements.txt


4. Configure as Variáveis de Ambiente

Configure as variáveis de ambiente necessárias para o projeto, como a chave secreta do Django e outras configurações de banco de dados. Isso pode ser feito criando um arquivo `.env` na raiz do projeto:

.env
DJANGO_SECRET_KEY=your_secret_key

5. Execute as Migrações

Aplique as migrações para configurar o banco de dados:

python manage.py migrate


6. Crie um Superusuário

Crie um superusuário para acessar a área administrativa do Django:

python manage.py createsuperuser


7. Execute o Servidor de Desenvolvimento

Para garantir que tudo esteja funcionando corretamente, execute o servidor de desenvolvimento do Django:

python manage.py runserver


8. Teste as Funcionalidades

8.1. Criação de Usuário

- Acesse `http://localhost:8000/contas/registrar/` para criar um novo usuário.
- Preencha os campos com seus dados e clique em "Registrar".

8.2. Login

- Acesse `http://localhost:8000/contas/entrar/`.
- Informe suas credenciais para acessar o sistema.

8.3. Depósito

- Acesse `http://localhost:8000/transacoes/deposito/`.
- Informe a quantia que deseja depositar e confirme.

8.4. Saque

- Acesse `http://localhost:8000/transacoes/saque/`.
- Informe a quantia que deseja sacar e confirme.

8.5. Transferência

- Acesse `http://localhost:8000/transacoes/transferencia/`.
- Informe o CPF do recebedor e a quantia que deseja transferir, em seguida confirme.

9. Atomicidade e Bloqueio Otimista

Este projeto implementa técnicas de atomicidade e bloqueio otimista para garantir a integridade das transações:

- **Atomicidade:** Todas as operações de transação são executadas em blocos atômicos, ou seja, se uma operação falhar, todas as alterações feitas são revertidas.
- **Bloqueio Otimista:** Evita que dois processos modifiquem o mesmo dado simultaneamente. Caso um processo detecte que os dados foram alterados por outro processo, ele gera um erro, forçando a repetição da operação.

10. Testes Unitários

Execute os testes unitários para garantir que todas as funcionalidades do projeto estejam funcionando conforme o esperado:

python manage.py test


Os testes garantem que as operações de depósito, saque, e transferência estão funcionando corretamente, inclusive testando cenários de concorrência utilizando o bloqueio otimista.

11. Configuração do NGINX

 11.1. Instalação do NGINX

 Certifique-se de que o NGINX está instalado no seu sistema. No Windows, você pode baixar o NGINX diretamente do [site oficial](https://nginx.org/en/download.html).

 11.2. Configuração do NGINX

 Altere o arquivo de configuração do NGINX (`nginx.conf`) para incluir a configuração do proxy reverso e balanceamento de carga:

 ```
 worker_processes  1;

 events {
     worker_connections  1024;
 }

 http {
     include       mime.types;
     default_type  application/octet-stream;

     sendfile        on;
     keepalive_timeout  65;

     upstream util_bank_app {
         server 127.0.0.1:8001;
         server 127.0.0.1:8002;
     }

     server {
         listen       80;
         server_name  localhost;

         location / {
             proxy_pass http://util_bank_app;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
             proxy_set_header X-Forwarded-Proto $scheme;
         }

         location /static/ {
             alias C:/projects/trabalho distribuidos/Projeto finalizado/util_bank/banking/static;
         }

         location /media/ {
             alias C:/projects/trabalho distribuidos/Projeto finalizado/util_bank/banking/static/images;
         }

         error_page   500 502 503 504  /50x.html;
         location = /50x.html {
             root   html;
         }
     }
 }
 ```

 11.3. Iniciar o NGINX

 Depois de configurar o NGINX, inicie o serviço:

 ```
 nginx -s reload
 ```

12. Configuração de Múltiplos Servidores Django

 Em terminais diferentes, execute o Django em diferentes portas para simular o balanceamento de carga:

 ```
 # Em um terminal
 python manage.py runserver 8001

 # Em outro terminal
 python manage.py runserver 8002
 ```

13. Teste de Balanceamento de Carga

 Acesse `http://localhost` e realize operações no sistema para verificar se o balanceamento de carga está funcionando corretamente. Se um dos servidores cair (pare de rodar o servidor em uma das portas), o outro servidor deverá continuar a atender as solicitações normalmente.



