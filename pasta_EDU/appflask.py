from flask import Flask, request, render_template, redirect, url_for, flash
import psycopg2
import os
from werkzeug.utils import secure_filename

# Configuração do caminho para salvar os arquivos
UPLOAD_FOLDER = r'C:\Users\edu.ferreira\Desktop\projeto\Supporte\anexos'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(24)

# Configuração do banco de dados PostgreSQL
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="demo",  # Nome do banco de dados
            user="postgres",  # Usuário do PostgreSQL
            password="root"   # Senha do PostgreSQL
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para verificar se a extensão do arquivo é permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rota para servir o arquivo HTML
@app.route('/')
def sac_form():
    return render_template('SAC.html')

# Rota para processar o formulário
@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        # Captura dos dados enviados pelo formulário
        nome = request.form['nome']
        email_corporativo = request.form['email_corporativo']
        ddd_telefone = request.form['ddd_telefone']
        razao_social = request.form['razao_social']
        numero_nf = request.form.get('numero_nf', None)  # Campo opcional
        assunto = request.form['assunto']
        descricao_reclamacao = request.form['descricao_reclamacao']

        # Verificar se um arquivo foi enviado
        if 'file' not in request.files:
            flash('Nenhum arquivo enviado.')
            return redirect(url_for('sac_form'))

        file = request.files['file']

        # Verificar se o arquivo é permitido
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Conectar ao banco de dados
        conn = get_db_connection()
        if conn is None:
            flash('Erro ao conectar ao banco de dados.')
            return redirect(url_for('sac_form'))

        # Inserir os dados no banco de dados
        cur = conn.cursor()
        query = """
        INSERT INTO reclamacoes (nome, email_corporativo, ddd_telefone, razao_social_empresas, numero_nf, assunto, descricao)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (nome, email_corporativo, ddd_telefone, razao_social, numero_nf, assunto, descricao_reclamacao))
        conn.commit()  # Confirma a inserção dos dados
        cur.close()
        conn.close()

        # Exibir uma mensagem de sucesso
        flash('Dados e arquivos enviados com sucesso!')
        return redirect(url_for('sac_form'))

    except Exception as e:
        print(f"Erro ao inserir dados no banco de dados: {e}")
        if conn:
            conn.rollback()
        flash(f"Erro ao inserir dados no banco de dados: {str(e)}")
        return redirect(url_for('sac_form'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
