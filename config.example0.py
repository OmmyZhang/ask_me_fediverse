class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ask.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False

    ENABLE_DIRECT = False
    ENABLE_OAUTH = False

    BOT_NAME = '@useless_bot'
    MAST_DOMAIN = 'your.domain'
    MAST_URL = 'https://' + MAST_DOMAIN

    WORK_URL = 'http://127.0.0.1:5000'
