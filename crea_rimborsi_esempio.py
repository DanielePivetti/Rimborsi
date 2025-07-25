import os
import sys
import random
from datetime import datetime, timedelta

# Aggiungi la directory corrente al path per importare i moduli
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.rimborso import Rimborso

app = create_app()

def crea_rimborsi_esempio():
    with app.app_context():
        # Ottieni gli utenti
        pinna = User.query.filter_by(username="Pinna_v").first()
        pivetti = User.query.filter_by(username="Pivetti_d").first()
        
        if not pinna or not pivetti:
            print("Utenti non trovati nel database!")
            return
        
        # Categorie e descrizioni
        categorie = ['trasporto', 'alloggio', 'pasti', 'formazione', 'materiali', 'altro']
        
        descrizioni_trasporto = [
            "Biglietto treno Roma-Milano A/R",
            "Taxi dall'aeroporto all'hotel",
            "Biglietto aereo per missione",
            "Pedaggio autostradale viaggio lavoro",
            "Carburante trasferta Firenze"
        ]
        
        descrizioni_alloggio = [
            "Pernottamento Hotel Roma Palace",
            "Alloggio per corso formazione Bologna",
            "Sistemazione B&B durante fiera Milano",
            "Hotel per convegno nazionale"
        ]
        
        descrizioni_pasti = [
            "Pranzo durante trasferta Napoli",
            "Cena con clienti istituzionali",
            "Pranzo di lavoro con partner",
            "Rimborso spese cena durante fiera"
        ]
        
        descrizioni_formazione = [
            "Corso formazione su fondi PNRR",
            "Seminario nuove normative PA",
            "Workshop digitalizzazione documenti",
            "Corso aggiornamento professionale"
        ]
        
        descrizioni_materiali = [
            "Acquisto cancelleria per ufficio",
            "Materiale per presentazione progetto",
            "Acquisto pubblicazioni specialistiche",
            "Toner per stampante ufficio"
        ]
        
        descrizioni_altro = [
            "Spese di rappresentanza evento istituzionale",
            "Servizio di traduzione documenti",
            "Quota partecipazione convegno",
            "Abbonamento rivista specializzata"
        ]
        
        descrizioni_per_categoria = {
            'trasporto': descrizioni_trasporto,
            'alloggio': descrizioni_alloggio,
            'pasti': descrizioni_pasti,
            'formazione': descrizioni_formazione,
            'materiali': descrizioni_materiali,
            'altro': descrizioni_altro
        }
        
        # Stati possibili
        stati = ['in_attesa', 'approvato', 'rifiutato']
        
        # Crea rimborsi per Pivetti_d (utente normale)
        rimborsi_pivetti = []
        for i in range(5):
            categoria = random.choice(categorie)
            descrizioni = descrizioni_per_categoria[categoria]
            
            # Per creare alcuni rimborsi in attesa e altri già approvati/rifiutati
            stato = 'in_attesa' if i < 3 else random.choice(stati)
            
            # Genera una data casuale negli ultimi 30 giorni per la richiesta
            data_richiesta = datetime.now() - timedelta(days=random.randint(0, 30))
            
            # Genera una data casuale per la spesa (precedente alla richiesta)
            data_spesa = data_richiesta - timedelta(days=random.randint(1, 10))
            
            importo = round(random.uniform(20, 500), 2)
            
            rimborso = Rimborso(
                user_id=pivetti.id,
                categoria=categoria,
                descrizione=random.choice(descrizioni),
                importo=importo,
                data_richiesta=data_richiesta,
                data_spesa=data_spesa,  # Aggiungiamo la data della spesa
                stato=stato,
                note=f"Rimborso {i+1} di test per l'utente {pivetti.username}"
            )
            
            # Se è stato approvato o rifiutato, aggiungi l'istruttore
            if stato in ['approvato', 'rifiutato']:
                # Usiamo pinna come istruttore
                rimborso.approvato_da = pinna.id
                rimborso.data_approvazione = data_richiesta + timedelta(days=random.randint(1, 5))
                
                if stato == 'rifiutato':
                    rimborso.note_approvazione = "Documentazione insufficiente o non conforme"
            
            rimborsi_pivetti.append(rimborso)
        
        # Crea rimborsi per Pinna_v (approvatore, ma può anche richiedere rimborsi)
        rimborsi_pinna = []
        for i in range(3):
            categoria = random.choice(categorie)
            descrizioni = descrizioni_per_categoria[categoria]
            
            # Per Pinna, creiamo solo rimborsi approvati o in attesa (non rifiutati)
            stato = 'in_attesa' if i < 2 else 'approvato'
            
            # Genera una data casuale negli ultimi 30 giorni per la richiesta
            data_richiesta = datetime.now() - timedelta(days=random.randint(0, 30))
            
            # Genera una data casuale per la spesa (precedente alla richiesta)
            data_spesa = data_richiesta - timedelta(days=random.randint(1, 10))
            
            importo = round(random.uniform(20, 500), 2)
            
            rimborso = Rimborso(
                user_id=pinna.id,
                categoria=categoria,
                descrizione=random.choice(descrizioni),
                importo=importo,
                data_richiesta=data_richiesta,
                data_spesa=data_spesa,  # Aggiungiamo la data della spesa
                stato=stato,
                note=f"Rimborso {i+1} di test per l'utente {pinna.username}"
            )
            
            # Se è stato approvato, aggiungiamo un altro utente come approvatore
            if stato == 'approvato':
                # Utilizziamo l'utente admin come approvatore per i rimborsi di Pinna
                admin = User.query.filter_by(username="admin").first()
                if admin:
                    rimborso.approvato_da = admin.id
                    rimborso.data_approvazione = data_richiesta + timedelta(days=random.randint(1, 5))
            
            rimborsi_pinna.append(rimborso)
        
        # Aggiungi tutti i rimborsi al database
        db.session.add_all(rimborsi_pivetti + rimborsi_pinna)
        db.session.commit()
        
        print(f"Creati {len(rimborsi_pivetti)} rimborsi per l'utente {pivetti.username}")
        print(f"Creati {len(rimborsi_pinna)} rimborsi per l'utente {pinna.username}")
        
        # Stampa un riepilogo dei rimborsi creati
        print("\nRiepilogo rimborsi per Pivetti_d:")
        for idx, r in enumerate(rimborsi_pivetti):
            print(f"{idx+1}. {r.descrizione} - €{r.importo:.2f} - Stato: {r.stato} - Data spesa: {r.data_spesa.strftime('%d/%m/%Y')}")
        
        print("\nRiepilogo rimborsi per Pinna_v:")
        for idx, r in enumerate(rimborsi_pinna):
            print(f"{idx+1}. {r.descrizione} - €{r.importo:.2f} - Stato: {r.stato} - Data spesa: {r.data_spesa.strftime('%d/%m/%Y')}")
        
        # Stampa un riepilogo dei rimborsi in attesa (quelli che vedrà Pinna come approvatore)
        rimborsi_in_attesa = Rimborso.query.filter_by(stato='in_attesa').all()
        print(f"\nTotale rimborsi in attesa di approvazione: {len(rimborsi_in_attesa)}")
        for idx, r in enumerate(rimborsi_in_attesa):
            user = User.query.get(r.user_id)
            print(f"{idx+1}. Richiesto da: {user.username} - {r.descrizione} - €{r.importo:.2f} - Data spesa: {r.data_spesa.strftime('%d/%m/%Y')}")

if __name__ == "__main__":
    crea_rimborsi_esempio()
