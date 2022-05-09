import os
import urllib
from dotenv import load_dotenv
load_dotenv()


class Config:
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    params = urllib.parse.quote_plus('DRIVER={SQL Server};'
                                     'SERVER=.\sqlexpress;'
                                     'DATABASE=coursework; Trusted_Connection=yes;')
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=%s" % params

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
                   ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = '[FootBuy]'
    MAIL_SENDER = 'FootBuy KirKas <foot.buy.kirkas@gmail.com>'
    SECURITY_LOGIN_URL = '/auth/login'

    UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/app/uploads/'
    DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/app/downloads/'

    @staticmethod
    def init_app(app):
        pass
