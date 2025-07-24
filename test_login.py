import os
import sys

# Aggiungi la directory corrente al path per importare i moduli
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.user import User

app = create_app()

def test_login(username, password):
    """Testa il login con username e password specifici."""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user is None:
            print(f"Utente '{username}' non trovato.")
            return False
        
        if user.check_password(password):
            print(f"Login riuscito per '{username}'!")
            print(f"Dettagli utente: {user.nome} {user.cognome}, ruolo: {user.ruolo}")
            return True
        else:
            print(f"Password non valida per '{username}'.")
            # Per debug: stampa l'hash della password nel database
            print(f"Password hash nel database: {user.password_hash}")
            return False

if __name__ == "__main__":
    print("Test di autenticazione per gli utenti esistenti...")
    test_login("admin", "admin123")
    test_login("approvatore", "approvatore123")
    test_login("mario", "mario123")
    test_login("giulia", "giulia123")
    
    # Proviamo anche una password sbagliata per verificare
    print("\nTest con password errata:")
    test_login("admin", "password_sbagliata")
