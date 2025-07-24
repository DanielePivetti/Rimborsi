import os
import sys
from datetime import datetime, date, timedelta
import random

# Aggiungi la directory corrente al path per importare i moduli
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.rimborso import Rimborso

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
        
        # Crea un approvatore
        approvatore = User(
            username="approvatore",
            email="approvatore@example.com",
            nome="Paolo",
            cognome="Verdi",
            ruolo="approvatore"
        )
        approvatore.set_password("approvatore123")
        
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
        
        db.session.add_all([admin, approvatore, utente1, utente2])
        db.session.commit()
        
        print("Utenti creati:")
        print(f"Amministratore: admin@example.com (admin123)")
        print(f"Approvatore: approvatore@example.com (approvatore123)")
        print(f"Utente: mario.rossi@example.com (mario123)")
        print(f"Utente: giulia.bianchi@example.com (giulia123)")

def create_rimborsi():
    """Crea richieste di rimborso di esempio."""
    with app.app_context():
        mario = User.query.filter_by(username="mario").first()
        giulia = User.query.filter_by(username="giulia").first()
        
        # Categorie di esempio
        categorie = ['trasporto', 'alloggio', 'pasti', 'formazione', 'materiali', 'altro']
        
        # Descrizioni di esempio
        descrizioni_trasporto = [
            "Biglietto treno Roma-Milano A/R",
            "Taxi dall'aeroporto all'hotel",
            "Biglietto autobus per fiera",
            "Pedaggio autostradale",
            "Carburante viaggio di lavoro"
        ]
        
        descrizioni_alloggio = [
            "Pernottamento Hotel Stella - Milano",
            "Pernottamento B&B Centro - Roma",
            "Alloggio per corso formazione",
            "Pernottamento per fiera"
        ]
        
        descrizioni_pasti = [
            "Pranzo durante trasferta",
            "Cena con cliente",
            "Colazione in trasferta",
            "Pasto durante conferenza"
        ]
        
        descrizioni_altro = [
            "Materiale per ufficio",
            "Iscrizione corso di formazione",
            "Acquisto libri professionali",
            "Iscrizione conferenza",
            "Riparazione PC aziendale"
        ]
        
        # Stati possibili
        stati = ['in_attesa', 'approvato', 'rifiutato']
        
        # Crea rimborsi per Mario
        for i in range(5):
            categoria = random.choice(categorie)
            
            if categoria == 'trasporto':
                descrizione = random.choice(descrizioni_trasporto)
                importo = round(random.uniform(20, 150), 2)
            elif categoria == 'alloggio':
                descrizione = random.choice(descrizioni_alloggio)
                importo = round(random.uniform(70, 200), 2)
            elif categoria == 'pasti':
                descrizione = random.choice(descrizioni_pasti)
                importo = round(random.uniform(15, 80), 2)
            else:
                descrizione = random.choice(descrizioni_altro)
                importo = round(random.uniform(30, 300), 2)
            
            # Data casuale negli ultimi 30 giorni
            giorni_fa = random.randint(1, 30)
            data_richiesta = datetime.now() - timedelta(days=giorni_fa)
            data_spesa = date.today() - timedelta(days=giorni_fa + random.randint(1, 5))
            
            stato = random.choice(stati)
            
            rimborso = Rimborso(
                descrizione=descrizione,
                importo=importo,
                data_richiesta=data_richiesta,
                data_spesa=data_spesa,
                categoria=categoria,
                stato=stato,
                note="Note di esempio per la richiesta di rimborso." if random.choice([True, False]) else None,
                user_id=mario.id
            )
            
            if stato == 'approvato':
                approvatore = User.query.filter_by(ruolo="approvatore").first()
                rimborso.approvato_da = approvatore.id
                rimborso.data_approvazione = data_richiesta + timedelta(days=random.randint(1, 3))
            
            db.session.add(rimborso)
        
        # Crea rimborsi per Giulia
        for i in range(3):
            categoria = random.choice(categorie)
            
            if categoria == 'trasporto':
                descrizione = random.choice(descrizioni_trasporto)
                importo = round(random.uniform(20, 150), 2)
            elif categoria == 'alloggio':
                descrizione = random.choice(descrizioni_alloggio)
                importo = round(random.uniform(70, 200), 2)
            elif categoria == 'pasti':
                descrizione = random.choice(descrizioni_pasti)
                importo = round(random.uniform(15, 80), 2)
            else:
                descrizione = random.choice(descrizioni_altro)
                importo = round(random.uniform(30, 300), 2)
            
            # Data casuale negli ultimi 30 giorni
            giorni_fa = random.randint(1, 30)
            data_richiesta = datetime.now() - timedelta(days=giorni_fa)
            data_spesa = date.today() - timedelta(days=giorni_fa + random.randint(1, 5))
            
            stato = 'in_attesa'  # La maggior parte sono in attesa
            
            rimborso = Rimborso(
                descrizione=descrizione,
                importo=importo,
                data_richiesta=data_richiesta,
                data_spesa=data_spesa,
                categoria=categoria,
                stato=stato,
                note="Note di esempio per la richiesta di rimborso." if random.choice([True, False]) else None,
                user_id=giulia.id
            )
            
            db.session.add(rimborso)
        
        db.session.commit()
        print("Rimborsi di esempio creati.")

if __name__ == '__main__':
    print("Inizializzazione del database...")
    reset_db()
    create_users()
    create_rimborsi()
    print("Inizializzazione completata!")
