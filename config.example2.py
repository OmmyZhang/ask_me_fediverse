class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ask.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False

    ENABLE_DIRECT = True
    ENABLE_OAUTH = True

    BOT_NAME = '@ask_me_bot'
    CLIENT_ID = 'client_id'
    CLIENT_SEC = 'client_secret'
    TOKEN = 'token'
    MAST_DOMAIN = 'your.domain'
    MAST_URL = 'https://' + MAST_DOMAIN

    WORK_URL = 'http://127.0.0.1:5000'
