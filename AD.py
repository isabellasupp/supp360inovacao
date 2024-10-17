from flask import Flask, request, redirect, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from ldap3 import Server, Connection, AUTO_BIND_NO_TLS, SUBTREE, ALL
from ldap3.core.exceptions import LDAPException

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Informações do Active Directory
AD_SERVER = 'ldap://189.112.5.177:389'  # IP e porta do AD da empresa
AD_USER_DN = 'DC=suaempresa,DC=com'     # Distinguished Name da sua empresa (substitua pelo DN correto)
AD_BIND_USER = 'cn=administrador,dc=suaempresa,dc=com'  # Usuário de bind no AD (com permissões)
AD_BIND_PASSWORD = 'sua_senha_secreta'  # Senha do usuário de bind no AD

# Classe User que representa um usuário autenticado
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Função user_loader para carregar o usuário baseado no ID
@login_manager.user_loader
def load_user(user_id):
    # Simplesmente retornamos um usuário com o ID (em um app real, buscaria no banco de dados)
    return User(user_id)

# Função para autenticar no Active Directory via LDAP
def ldap_login(username, password):
    try:
        # Conectar ao servidor LDAP
        server = Server(AD_SERVER, get_info=ALL)
        conn = Connection(
            server,
            user=f'CN={username},{AD_USER_DN}',  # Formato do usuário AD (substitua conforme necessário)
            password=password,
            auto_bind=True
        )
        
        # Se a conexão for bem-sucedida, significa que a autenticação foi realizada
        if conn.bind():
            print("Usuário autenticado no Active Directory")
            return True
        else:
            print("Falha na autenticação no Active Directory")
            return False
    except LDAPException as e:
        print(f'Erro ao se conectar ao AD: {e}')
        return False

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar login no Active Directory
        if ldap_login(username, password):
            # Supondo que o ID do usuário seja o username no AD (substitua por ID real se necessário)
            user = User(id=username)
            login_user(user)
            return redirect('/dashboard')
        else:
            return "Falha na autenticação com o AD"

    return render_template('login.html')

# Página de dashboard (apenas usuários logados)
@app.route('/dashboard')
@login_required
def dashboard():
    return 'Bem-vindo ao seu dashboard, você está autenticado no Active Directory!'

# Inicializar o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
