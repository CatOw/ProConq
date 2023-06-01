from pathlib import Path


class ServerConstants:
    HOST = '0.0.0.0'
    PORT = 50000


class Paths:
    PROJECT_DIR = Path(__file__).resolve().parent.parent
    LOGGING: Path = PROJECT_DIR / 'logs'
    DATABASE: Path = PROJECT_DIR / 'src' / 'database' / 'user_database.db'
