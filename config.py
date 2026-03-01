import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'mysql+pymysql://root:password@localhost/dianshang_db'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/dianshang_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
