import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from .models import User, db
from flask_login import LoginManager

# Inizializza il database

db = SQLAlchemy()


def create_app():
    
    app = Flask(__name__)
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = '0843fa8fa5f4fb7eba2ce61d89ad6d5a'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(basedir), 'instance', 'rimborsi.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inizializza il database
    
    db.init_app(app)
    
    # Configura Flask Login
    
    # Importa User dopo aver inizializzato db
    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Devi effettuare il login per accedere a questa pagina'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)
    
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
   
   
    from .routes import main
    app.register_blueprint(main)

    # Crea la cartella instance se non esiste
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
