# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager
from flask_mail import Mail
from flask_admin import Admin
from flask_security import Security
from flask_migrate import Migrate

### ДЛЯ ОПЛАТЫ ###
# from cloudipsp import Api, Checkout

# api_pay = Api(merchant_id=1396424, secret_key='test')
# checkout = Checkout(api=api)
###################

db = SQLAlchemy()
migrate = Migrate()

mail = Mail()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

f_admin = Admin(name='FootBuy')
security = Security()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

    mail.init_app(app)
    login_manager.init_app(app)

    # подключение маршрутов и нестандартных страниц с сообщениями об ошибках
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .admin.views import HomeAdminView
    f_admin.init_app(app=app, index_view=HomeAdminView(name='Home'))
    from app.admin.views import user_datastore
    security.init_app(app, user_datastore)

    from app.admin import admin_bp as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    # экзмепляр приложения
    return app
