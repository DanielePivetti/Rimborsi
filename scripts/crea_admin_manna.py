"""
Script per creare un utente amministratore.
"""
import sys
import os

# Aggiungi la directory principale al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Verifica se l'utente esiste già
    user = User.query.filter_by(username='Manna_t').first()
    
    if user:
        print(f"L'utente {user.username} esiste già.")
        # Aggiorna il ruolo a amministratore se non lo è già
        if not user.is_admin():
            user.ruolo = 'amministratore'
            db.session.commit()
            print(f"L'utente {user.username} è stato aggiornato al ruolo di amministratore.")
        else:
            print(f"L'utente {user.username} è già un amministratore.")
        sys.exit(0)
    
    # Crea il nuovo utente amministratore
    nuovo_utente = User(
        username='Manna_t',
        nome='Tommaso',
        cognome='Manna',
        email='tommaso.manna@example.com',
        ruolo='amministratore'
    )
    
    # Imposta la password
    nuovo_utente.set_password('tramonto')
    
    # Aggiungi l'utente al database
    db.session.add(nuovo_utente)
    db.session.commit()
    
    print(f"Utente {nuovo_utente.username} creato con successo come amministratore.")
    print(f"Nome: {nuovo_utente.nome} {nuovo_utente.cognome}")
    print(f"Email: {nuovo_utente.email}")
    print(f"Ruolo: {nuovo_utente.ruolo}")
