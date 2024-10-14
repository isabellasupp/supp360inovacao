from flask import Flask, render_template, url_for, g

app = Flask(__name__)

# Definindo algumas variáveis globais
@app.before_request
def before_request():
    g.SITE_TITULO = "Supporte Logistica"
    g.CRIADO_POR = "Supporte"

# Página de login
@app.route('/')
def login():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)  # Rodando na porta 8080
