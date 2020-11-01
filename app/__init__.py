from flask import Flask, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config


SESSION_TYPE = 'memcache'
fapp = Flask(__name__)
fapp.config.from_object(Config)
sess = Session()
sess.init_app(fapp)
fapp.debug = True
login = LoginManager(fapp)
login.login_view = 'login'

db = SQLAlchemy(fapp)
migrate = Migrate(fapp, db)
# from app import routes
# from app import databases
from app import routes
from app import models
# from app.databases import DB
