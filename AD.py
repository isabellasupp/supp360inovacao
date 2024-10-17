from flask import Flask, request, redirect, render_template, flash, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from ldap3 import Server, Connection, AUTO_BIND_NO_TLS, SUBTREE, ALL
from ldap3.core.exceptions import LDAPException

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Substitua pela sua chave secreta gerada

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Informações do Active Directory
AD_SERVER = 'ldap://192.168.102.170:389'  # IP e porta do AD da empresa
AD_USER_DN = 'DC=supportelogistica,DC=com,DC=br'  # Distinguished Name (DN) da sua empresa

# Classe User que representa um usuário autenticado
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Função user_loader para carregar o usuário baseado no ID
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Função para autenticar no Active Directory via LDAP
def ldap_login(username, password):
    try:
        # Conectar ao servidor LDAP
        server = Server(AD_SERVER, get_info=ALL)
        user_dn = username  # Se você está usando o e-mail, use diretamente o 'username'

        # Tenta autenticar o usuário com as credenciais fornecidas
        conn = Connection(
            server,
            user=user_dn,
            password=password,
            auto_bind=True
        )
        
        # Se a conexão for bem-sucedida, a autenticação foi realizada
        if conn.bind():
            print(f"Usuário {username} autenticado no Active Directory")
            return True
        else:
            print(f"Falha na autenticação do usuário {username} no Active Directory")
            return False
    except LDAPException as e:
        print(f'Erro ao se conectar ao AD: {e}')
        return False

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Verificar login no Active Directory
        if ldap_login(username, password):
            user = User(id=username)
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('success'))
        else:
            flash('Falha na autenticação com o AD', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Página de dashboard (apenas usuários logados)
@app.route('/dashboard')
@login_required
def dashboard():
    return 'Bem-vindo ao seu dashboard, você está autenticado no Active Directory!'

# Página de sucesso após o login
@app.route('/teste')
@login_required
def success():
    return render_template('teste.html', message="Login realizado com sucesso!")

# Inicializar o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
