import logging
import pandas as pd
from app.repositories.database import PostgresConnection
from datetime import datetime
import bcrypt  # Biblioteca para criptografar senhas

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def generate_hashed_password(password: str) -> str:
        """
        Gera uma senha criptografada usando bcrypt.
        """
        # Gera um salt e usa o bcrypt para criar a senha criptografada
        salt = bcrypt.gensalt()  # Gera um salt para adicionar aleatoriedade à criptografia
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    @staticmethod
    def insert_users_from_dataframe(data: pd.DataFrame):
        # Define o SQL de inserção
        sql = """
        INSERT INTO "user" (username, password, email, cnpj, consent_status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        # Iniciar a conexão com o banco de dados
        with PostgresConnection() as db:
            for _, row in data.iterrows():
                # Mapeia os dados do DataFrame para os campos da tabela
                username = row['name']
                cnpj = row['document_number']
                consent_status = False  # Valor padrão
                created_at = datetime.now()
                updated_at = datetime.now()

                # Gerar email e senha padrão (modifique conforme necessário)
                email = f"{username.replace(' ', '_').lower()}@example.com"

                # Gerar uma senha padrão e criptografá-la
                default_password = 'default_password'  # Senha padrão
                hashed_password = UserService.generate_hashed_password(default_password)

                values = (username, hashed_password, email, cnpj, consent_status, created_at, updated_at)

                try:
                    db.execute_query(sql, values)
                    logger.info(f"Successfully inserted user: {username}")
                except Exception as e:
                    logger.error(f"Error inserting user {username}: {e}")
