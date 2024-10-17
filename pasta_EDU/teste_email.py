# Este código conecta a um banco de dados PostgreSQL e realiza o envio de emails para os destinatários com base nas reclamações armazenadas no banco.
# A função processar_banco_de_dados() consulta todas as reclamações que ainda não tiveram um email enviado (identificadas pela coluna email_enviado marcada como false),
# gera um email com os detalhes da reclamação e o envia para um email de teste específico. Após o envio bem-sucedido, a reclamação é marcada como processada,
# definindo a coluna email_enviado como true no banco de dados.

# Este fluxo garante que cada reclamação seja processada e o email seja enviado uma única vez.
# O envio é feito por meio do servidor SMTP do Outlook com criptografia STARTTLS para maior segurança.


import psycopg2  # Importa a biblioteca para conexão com o PostgreSQL
import smtplib  # Importa a biblioteca para envio de emails
from email.mime.text import MIMEText  # Importa a classe para criar emails em formato MIME

# Função para enviar o email
def enviar_email(destinatario, conteudo):
    smtp_server = "smtp.office365.com"  # Servidor SMTP para envio (neste caso, Outlook)
    smtp_port = 587  # Porta utilizada para o protocolo SMTP com STARTTLS
    smtp_usuario = "gatilhos@supplog.com"  # Email que será utilizado para o envio
    smtp_senha = "Supplog@2024"  # Senha do email ou senha de aplicativo

    # Cria o corpo da mensagem
    msg = MIMEText(conteudo)  # Define o conteúdo do email em formato de texto simples
    msg['Subject'] = 'Reclamação'  # Assunto do email
    msg['From'] = smtp_usuario  # Define o remetente
    msg['To'] = destinatario  # Define o destinatário

    try:
        # Inicia a conexão com o servidor SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)  # Conecta ao servidor SMTP
        server.starttls()  # Inicia criptografia STARTTLS para segurança
        server.login(smtp_usuario, smtp_senha)  # Realiza o login com as credenciais fornecidas
        server.sendmail(smtp_usuario, destinatario, msg.as_string())  # Envia o email
        server.quit()  # Encerra a conexão com o servidor SMTP
        print(f"Email enviado para {destinatario}")  # Confirmação de envio no console
    except Exception as e:
        # Tratamento de erro em caso de falha no envio do email
        print(f"Falha no envio de email: {e}")

# Função para acessar o banco de dados e processar as linhas
def processar_banco_de_dados():
    try:
        # Conexão com o banco de dados PostgreSQL
        conn = psycopg2.connect(
            host="localhost",  # Endereço do servidor do banco de dados
            database="demo",  # Nome do banco de dados
            user="postgres",  # Usuário do banco de dados
            password="root"  # Senha do banco de dados
        )
        cur = conn.cursor()  # Cria um cursor para executar comandos SQL

        # Consulta SQL para selecionar linhas ainda não processadas (onde email_enviado é false)
        cur.execute("""
            SELECT id, nome, email_corporativo, ddd_telefone, razao_social_empresas, numero_nf, assunto, descricao
            FROM reclamacoes
            WHERE email_enviado = false
        """)
        linhas = cur.fetchall()  # Busca todas as linhas retornadas pela consulta

        # Itera sobre cada linha retornada pela consulta
        for linha in linhas:
            id, nome, email_corporativo, ddd_telefone, razao_social_empresas, numero_nf, assunto, descricao = linha

            # Corpo do email gerado dinamicamente com os dados da reclamação
            conteudo_email = f"""

            Uma nova reclamacao foi registrada.

            ID: {id}
            Nome: {nome}
            Empresa: {razao_social_empresas}
            Telefone: {ddd_telefone}
            Email Corporativo: {email_corporativo}

            Assunto: {assunto}
            Número da NF: {numero_nf}
            Descrição: {descricao}

            Atenciosamente,
            """

            # Envia o email para o destinatário retirado do banco de dados
            enviar_email('edu.ferreira@supplog.com', conteudo_email)

            # Atualiza o registro no banco de dados para marcar como processado (email enviado)
            cur.execute("UPDATE reclamacoes SET email_enviado = true WHERE id = %s", (id,))
            conn.commit()  # Confirma a alteração no banco de dados

        cur.close()  # Fecha o cursor
        conn.close()  # Fecha a conexão com o banco de dados

    except Exception as e:
        # Tratamento de erro em caso de falha na conexão ou execução da consulta
        print(f"Erro ao acessar o banco de dados: {e}")

# Executa a função de processamento do banco de dados
processar_banco_de_dados()
