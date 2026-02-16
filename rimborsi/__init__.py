import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Inizializza il database

db = SQLAlchemy()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = '0843fa8fa5f4fb7eba2ce61d89ad6d5a'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(basedir), 'instance', 'rimborsi.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inizializza il database
    
    db.init_app(app)
    Migrate(app, db)
    csrf.init_app(app)  # Abilita csrf_token() nei template

        # Importa User dopo aver inizializzato db
    
    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Devi effettuare il login per accedere a questa pagina'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)
    
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
   
   # === NUOVA SEZIONE: REGISTRAZIONE DEI BLUEPRINTS ===
    from .main.routes import main
    app.register_blueprint(main)

    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from .istruttoria.routes import istruttoria_bp
    app.register_blueprint(istruttoria_bp)
   
    from .anagrafica.routes import anagrafica_bp
    app.register_blueprint(anagrafica_bp)
    
    from .richiesta.routes import richiesta_bp
    app.register_blueprint(richiesta_bp)

    from .integrazione.routes import integrazione_bp
    app.register_blueprint(integrazione_bp)
    
        
    # Crea la cartella instance se non esiste
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
