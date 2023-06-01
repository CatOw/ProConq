import sqlite3
import bcrypt

from proconq_chat.setup_logging import setup_logging


class UserDatabase:
    def __init__(self, db_name: str):
        self.logger = setup_logging(__name__)
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_table()

    def create_table(self) -> None:
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            name TEXT PRIMARY KEY,
            salt TEXT,
            password TEXT
        )
        '''
        self.conn.execute(create_table_query)
        self.conn.commit()

    def register_user(self, name: str, password: str) -> bool:
        if name == 'GUEST':
            return False

        # Check if the user already exists
        if self.user_exists(name):
            return False

        # Generate salt and hash the password
        salt = bcrypt.gensalt().decode('utf-8')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8')).decode('utf-8')

        # Insert the user into the database
        insert_query = '''
        INSERT INTO users (name, salt, password)
        VALUES (?, ?, ?)
        '''
        self.conn.execute(insert_query, (name, salt, hashed_password))
        self.conn.commit()
        self.logger.info(f"Registered user: {name}")
        return True

    def user_exists(self, name: str) -> bool:
        select_query = '''
        SELECT name FROM users WHERE name = ?
        '''
        result = self.conn.execute(select_query, (name,))
        return result.fetchone() is not None

    def verify_login(self, name: str, password: str) -> bool:
        if name == 'GUEST':
            return False

        select_query = '''
        SELECT salt, password FROM users WHERE name = ?
        '''
        result = self.conn.execute(select_query, (name,))
        row = result.fetchone()
        if row:
            salt: str = row[0]
            hashed_password: str = row[1]
            encoded_password = password.encode('utf-8')
            encoded_salt = salt.encode('utf-8')
            if bcrypt.checkpw(encoded_password, hashed_password.encode('utf-8')):
                self.logger.info(f"Login successful: {name}")
                return True
        self.logger.warning(f"Login failed: {name}")
        return False

    def get_all_user_credentials(self) -> dict[str, str]:
        select_query = '''
        SELECT name, password FROM users
        '''
        result = self.conn.execute(select_query)
        credentials = {name: password for name, password in result}
        return credentials

    def delete_user(self, name: str) -> bool:
        delete_query = '''
        DELETE FROM users WHERE name = ?
        '''
        self.conn.execute(delete_query, (name,))
        self.conn.commit()
        rows_deleted = self.conn.total_changes
        return rows_deleted > 0
    