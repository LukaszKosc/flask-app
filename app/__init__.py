import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config

import os


SESSION_TYPE = 'memcache'
fapp = Flask(__name__)
fapp.config.from_object(Config)
login = LoginManager(fapp)
login.login_view = 'login'
db = SQLAlchemy(fapp)
migrate = Migrate(fapp, db)
mail = Mail(fapp)


from app import routes, models, errors


if not fapp.debug:
    if fapp.config['MAIL_SERVER']:

        auth = None
        if fapp.config['MAIL_USERNAME'] or fapp.config['MAIL_PASSWORD']:
            auth = (fapp.config['MAIL_USERNAME'], fapp.config['MAIL_PASSWORD'])
        secure = None
        if fapp.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(fapp.config['MAIL_SERVER'], fapp.config['MAIL_PORT']),
            fromaddr='no-reply@' + fapp.config['MAIL_SERVER'],
            toaddrs=fapp.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        fapp.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    fapp.logger.addHandler(file_handler)

    fapp.logger.setLevel(logging.INFO)
    fapp.logger.info('Microblog startup')
