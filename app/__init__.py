from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录以访问该页面。'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 注册蓝图
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    from app.routes.merchant import bp as merchant_bp
    app.register_blueprint(merchant_bp, url_prefix='/merchant')
    
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app

from app import models
