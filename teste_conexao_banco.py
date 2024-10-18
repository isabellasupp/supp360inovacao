import os
from dotenv import load_dotenv
import psycopg2

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'demo'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'root'),
            options="-c client_encoding=UTF8"
        )
        print("Conexão com o banco de dados estabelecida com sucesso.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def execute_query():
    conn = get_db_connection()
    if conn:
        try:
            # Criar um cursor para executar a consulta
            cur = conn.cursor()
            
            # Substitua esta consulta por qualquer consulta que faça sentido no seu banco de dados
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
            cur.execute(query)
            
            # Obter todos os resultados da consulta
            rows = cur.fetchall()
            print("Tabelas no banco de dados:")
            for row in rows:
                print(row[0])
            
            # Fechar o cursor e a conexão
            cur.close()
        except Exception as e:
            print(f"Erro ao executar a consulta: {e}")
        finally:
            conn.close()
            print("Conexão encerrada com sucesso.")
    else:
        print("Não foi possível estabelecer a conexão com o banco de dados.")

if __name__ == '__main__':
    execute_query()
