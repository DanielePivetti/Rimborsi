"""
Script per verificare e correggere la gestione delle sessioni in Flask
"""
import os
import sys

# Aggiungi la directory corrente al path per importare i moduli
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

app = create_app()

# Modifica la configurazione dell'app per rafforzare la gestione delle sessioni
with app.app_context():
    # Imposta un timeout di sessione più lungo (7 giorni in secondi)
    app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 7
    
    # Imposta una posizione specifica per i file di sessione
    app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
    
    # Utilizza il filesystem per le sessioni
    app.config['SESSION_TYPE'] = 'filesystem'
    
    # Forza il riutilizzo delle sessioni
    app.config['SESSION_USE_SIGNER'] = True
    
    print("Configurazione della sessione modificata:")
    print(f"PERMANENT_SESSION_LIFETIME: {app.config['PERMANENT_SESSION_LIFETIME']}")
    print(f"SESSION_FILE_DIR: {app.config.get('SESSION_FILE_DIR', 'Non impostato')}")
    print(f"SESSION_TYPE: {app.config.get('SESSION_TYPE', 'Non impostato')}")
    print(f"SESSION_USE_SIGNER: {app.config.get('SESSION_USE_SIGNER', 'Non impostato')}")
    
    print("\nPer applicare queste modifiche, aggiungi il seguente codice in app/__init__.py:")
    print("""
    # Nella funzione create_app, dopo app.config.from_object(config_class):
    app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 7  # 7 giorni
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(app.instance_path), 'flask_session')
    app.config['SESSION_USE_SIGNER'] = True
    
    # E installa flask-session con:
    # pip install flask-session
    
    # Quindi importa e inizializza Session:
    from flask_session import Session
    session = Session(app)
    """)
