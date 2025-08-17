import os
import sys
from datetime import datetime, date, timedelta
import random

# Aggiungi la directory corrente al path per importare i moduli
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.user import User

app = create_app()

def reset_db():
    """Resetta il database, eliminando tutti i dati esistenti e ricreando le tabelle."""    
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database resettato.")

def create_users():
    """Crea utenti di esempio."""
    with app.app_context():
        # Crea un amministratore
        admin = User(
            username="admin",
            email="admin@example.com",
            nome="Amministratore",
            cognome="Sistema",
            ruolo="amministratore"
        )
        admin.set_password("admin123")
        
        # Crea un istruttore
        istruttore = User(
            username="istruttore",
            email="istruttore@example.com",
            nome="Paolo",
            cognome="Verdi",
            ruolo="istruttore"
        )
        istruttore.set_password("istruttore123")
        
        # Crea utenti normali
        utente1 = User(
            username="mario",
            email="mario.rossi@example.com",
            nome="Mario",
            cognome="Rossi",
            ruolo="utente"
        )
        utente1.set_password("mario123")
        
        utente2 = User(
            username="giulia",
            email="giulia.bianchi@example.com",
            nome="Giulia",
            cognome="Bianchi",
            ruolo="utente"
        )
        utente2.set_password("giulia123")
        
        # Crea l'utente compilatore Pivetti_d
        compilatore = User(
            username="Pivetti_d",
            email="pivetti.d@example.com",
            nome="Daniele",
            cognome="Pivetti",
            ruolo="utente"
        )
        compilatore.set_password("Banana")
        
        db.session.add_all([admin, istruttore, utente1, utente2, compilatore])
        db.session.commit()
        
        print("Utenti creati:")
        print(f"Amministratore: admin@example.com (admin123)")
        print(f"Istruttore: istruttore@example.com (istruttore123)")
        print(f"Utente: mario.rossi@example.com (mario123)")
        print(f"Utente: giulia.bianchi@example.com (giulia123)")

if __name__ == '__main__':
    print("Inizializzazione del database...")
    reset_db()
    create_users()
    print("Inizializzazione completata!")
