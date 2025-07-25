"""
Script per resettare la password di un utente.
Questo script reimposta la password dell'utente Bianchi_g.
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Aggiungi la directory principale al path per importare l'app
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from sqlalchemy import text

app = create_app()

def reset_password(username, new_password):
    """
    Reimposta la password dell'utente specificato.
    
    Args:
        username (str): Username dell'utente
        new_password (str): Nuova password da impostare
    
    Returns:
        bool: True se l'operazione è andata a buon fine, False altrimenti
    """
    with app.app_context():
        # Verifica se l'utente esiste
        user = db.session.execute(text(f"SELECT * FROM user WHERE username = '{username}'")).first()
        
        if not user:
            print(f"Utente '{username}' non trovato.")
            return False
        
        # Genera l'hash della nuova password
        password_hash = generate_password_hash(new_password)
        
        # Aggiorna la password nel database
        db.session.execute(text(f"UPDATE user SET password_hash = '{password_hash}' WHERE id = {user.id}"))
        db.session.commit()
        
        print(f"Password di '{username}' reimpostata con successo.")
        return True

if __name__ == "__main__":
    # Resetta la password di Bianchi_g a "Password123!"
    reset_password("Bianchi_g", "Password123!")
