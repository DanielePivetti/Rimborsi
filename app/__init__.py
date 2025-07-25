import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Inizializzazione delle estensioni
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Effettua il login per accedere a questa pagina.'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    
    # Inizializza le estensioni
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Assicurati che la directory instance esista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Registra i blueprint
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.evento import evento_bp
    from app.blueprints.odv import odv_bp
    from app.blueprints.mezzo import mezzo_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(evento_bp, url_prefix='/admin')
    app.register_blueprint(odv_bp, url_prefix='/admin/odv')
    app.register_blueprint(mezzo_bp, url_prefix='/admin/mezzi')
    
    return app

# Importa i modelli per renderli disponibili a Flask-Migrate
from app.models import user, rimborso, evento, odv, mezzo
