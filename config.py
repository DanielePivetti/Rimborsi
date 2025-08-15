import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///rimborsi.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
