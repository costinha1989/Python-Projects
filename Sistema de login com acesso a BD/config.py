import os

class Config:
    # Chave secreta para proteger as sessões e dados de formulário
    SECRET_KEY = os.environ.get("SECRET_KEY", "chave_secreta_super_segura")

    # Configurações do banco de dados MariaDB
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "207509SQLF0rm")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "main_db")

    # Conexão com MariaDB (usando pymysql)
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações do Flask-Mail para enviar emails via Mailtrap
    MAIL_SERVER = 'sandbox.smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME = 'ef8df689f9493a'
    MAIL_PASSWORD = 'c59f7a02d9fb5f'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
