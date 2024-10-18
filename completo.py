from flask import Flask, request, render_template, redirect, url_for, flash
import psycopg2
import os
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Configuração do caminho para salvar os arquivos
UPLOAD_FOLDER = os.path.join('supp360inovacao', 'pasta_EDU', 'anexos')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

class AppFlask:
    def __init__(self):
        # Configura a pasta de templates como 'templates', onde deve estar o SAC.html
        self.app = Flask(__name__)
        self.app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        self.app.secret_key = os.urandom(24)
        self.setup_routes()

    # Configuração do banco de dados PostgreSQL
    def get_db_connection(self):
        try:
            # Adiciona a codificação UTF-8 para evitar problemas de caracteres especiais
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="demo",  # Nome do banco de dados
                user="postgres",  # Usuário do PostgreSQL
                password="root",  # Senha do PostgreSQL
                options='-c client_encoding=UTF8'  # Garante que a codificação seja UTF-8
            )
            return conn
        except psycopg2.OperationalError as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None

    # Função para verificar se a extensão do arquivo é permitida
    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # Função para enviar o email com anexo
    def enviar_email(self, destinatario, conteudo, anexo_path):
        smtp_server = "smtp.office365.com"
        smtp_port = 587
        smtp_usuario = "gatilhos@supplog.com"
        smtp_senha = "Supplog@2024"
        assunto = request.form['assunto']

        msg = MIMEMultipart()
        msg['From'] = smtp_usuario
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(conteudo, 'plain'))

        if anexo_path:
            with open(anexo_path, 'rb') as file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(anexo_path)}')
                msg.attach(part)

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_usuario, smtp_senha)
            server.sendmail(smtp_usuario, destinatario, msg.as_string())
            server.quit()
            print(f"Email enviado para {destinatario}")
        except Exception as e:
            print(f"Falha no envio de email: {e}")

    # Rota para servir o arquivo HTML
    def sac_form(self):
        return render_template('SAC.html')

    # Rota para processar o formulário
    def submit_form(self):
        try:
            # Captura dos dados enviados pelo formulário
            nome = request.form['nome']
            email_corporativo = request.form['email_corporativo']
            ddd_telefone = request.form['ddd_telefone']
            razao_social = request.form['razao_social']
            numero_nf = request.form.get('numero_nf', None)
            assunto = request.form['assunto']
            descricao_reclamacao = request.form['descricao_reclamacao']

            file_path = None

            # Verificar se um arquivo foi enviado
            if 'file' in request.files:
                file = request.files['file']
                if file and self.allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)

            # Conectar ao banco de dados
            conn = self.get_db_connection()
            if conn is None:
                flash('Erro ao conectar ao banco de dados.')
                return redirect(url_for('sac_form'))

            # Inserir os dados no banco de dados
            cur = conn.cursor()
            query = """
            INSERT INTO reclamacoes (nome, email_corporativo, ddd_telefone, razao_social_empresas, numero_nf, assunto, descricao, file_path, email_enviado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, false)
            RETURNING id
            """
            cur.execute(query, (nome, email_corporativo, ddd_telefone, razao_social, numero_nf, assunto, descricao_reclamacao, file_path))
            conn.commit()
            id_reclamacao = cur.fetchone()[0]

            cur.close()
            conn.close()

            # Enviar o e-mail com os detalhes da reclamação
            conteudo_email = f"""
            Uma nova reclamacao foi registrada.
            
            Nome: {nome}
            Empresa: {razao_social}
            Telefone: {ddd_telefone}
            Email Corporativo: {email_corporativo}

            Número da NF: {numero_nf}
            Descrição: {descricao_reclamacao}

            Atenciosamente,
            """
            self.enviar_email('edu.ferreira@supplog.com', conteudo_email, file_path)

            # Atualizar o banco de dados marcando como email enviado
            conn = self.get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE reclamacoes SET email_enviado = true WHERE id = %s", (id_reclamacao,))
            conn.commit()
            cur.close()
            conn.close()

            flash('Dados e arquivos enviados com sucesso!')
            return redirect(url_for('sac_form'))

        except Exception as e:
            print(f"Erro ao inserir dados no banco de dados: {e}")
            if conn:
                conn.rollback()
            flash(f"Erro ao inserir dados no banco de dados: {str(e)}")
            return redirect(url_for('sac_form'))

    def setup_routes(self):
        self.app.add_url_rule('/', 'sac_form', self.sac_form)
        self.app.add_url_rule('/submit', 'submit_form', self.submit_form, methods=['POST'])

    def run(self):
        self.app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == '__main__':
    app_flask = AppFlask()
    app_flask.run()
