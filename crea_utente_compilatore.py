"""
Script per creare un utente compilatore con username Pivetti_d e password Banana
"""
import sys
import os

# Aggiungi la directory principale al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app import create_app, db
from app.models.user import User

app = create_app()

def crea_utente_compilatore():
    with app.app_context():
        # Verifica se l'utente esiste già
        utente_esistente = User.query.filter_by(username="Pivetti_d").first()
        
        if utente_esistente:
            print(f"L'utente {utente_esistente.username} esiste già nel database.")
            # Aggiorna la password se necessario
            utente_esistente.set_password("Banana")
            db.session.commit()
            print(f"Password aggiornata per l'utente {utente_esistente.username}.")
            return
        
        # Crea il nuovo utente compilatore
        nuovo_utente = User(
            username="Pivetti_d",
            email="pivetti.d@example.com",
            nome="Daniele",
            cognome="Pivetti",
            ruolo="utente"  # utente standard (compilatore)
        )
        
        # Imposta la password
        nuovo_utente.set_password("Banana")
        
        # Aggiungi l'utente al database
        db.session.add(nuovo_utente)
        db.session.commit()
        
        print(f"Utente compilatore {nuovo_utente.username} creato con successo.")

if __name__ == "__main__":
    crea_utente_compilatore()
