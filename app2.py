from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
import os

app = Flask(__name__)

# Configuração da chave secreta para a sessão
app.config["SECRET_KEY"] = os.urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Definindo um nome de usuário e senha fictícios para o exemplo
USERNAME = "Pedro"
PASSWORD = "12345"

@app.route('/')
def home():
    return redirect(url_for('login'))

# Rota para exibir a página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['senha']
        
        # Verificando se o usuário e senha estão corretos
        if username == USERNAME and password == PASSWORD:
            session['user'] = username  # Salvando o nome de usuário na sessão
            return redirect(url_for('teste'))
        else:
            flash("Usuário ou senha incorretos. Tente novamente.")
            return render_template('login.html')

    return render_template('login.html')

# Rota para a página "teste.html" (após login bem-sucedido)
@app.route('/teste')
def teste():
    # Verificando se o usuário está logado
    if 'user' in session:
        return render_template('teste.html', user=session['user'])
    else:
        flash("Você precisa fazer login para acessar esta página.")
        return redirect(url_for('login'))

# Rota para logout
@app.route('/logout')
def logout():
    session.pop('user', None)  # Removendo o usuário da sessão
    flash("Você foi desconectado.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Configuração para rodar localmente na porta 5000
    app.run(debug=True, host="0.0.0.0", port=5000)
