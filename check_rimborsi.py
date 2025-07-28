"""
Script di verifica del database per l'applicazione Rimborsi

Questo script verifica la consistenza del database e riporta eventuali problemi.
"""

import os
import sys
from datetime import datetime

# Aggiungi la directory principale al path per importare i moduli dell'app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importa i moduli necessari dall'applicazione
from app import create_app, db
from app.models.utente import Utente
from app.models.richiesta import Richiesta, StatoRichiesta
from app.models.spesa import Spesa, TipoSpesa
from app.models.documento_spesa import DocumentoSpesa, TipoDocumento

# Crea l'applicazione con configurazione di test
app = create_app('test')

def main():
    """Funzione principale di verifica"""
    with app.app_context():
        print("Verifica del database Rimborsi in corso...")
        print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("-" * 50)
        
        # Verifica utenti
        check_utenti()
        
        # Verifica richieste
        check_richieste()
        
        # Verifica spese
        check_spese()
        
        # Verifica documenti
        check_documenti()
        
        print("-" * 50)
        print("Verifica completata.")

def check_utenti():
    """Verifica la tabella utenti"""
    utenti = Utente.query.all()
    print(f"\nUtenti totali: {len(utenti)}")
    
    # Verifica utenti senza email
    utenti_senza_email = Utente.query.filter(Utente.email == None).all()
    if utenti_senza_email:
        print(f"ATTENZIONE: {len(utenti_senza_email)} utenti senza email")
        for u in utenti_senza_email:
            print(f"  - ID: {u.id}, Nome: {u.nome} {u.cognome}")

def check_richieste():
    """Verifica la tabella richieste"""
    richieste = Richiesta.query.all()
    print(f"\nRichieste totali: {len(richieste)}")
    
    # Conteggio per stato
    stati = {}
    for r in richieste:
        stati[r.stato.name] = stati.get(r.stato.name, 0) + 1
    
    for stato, count in stati.items():
        print(f"  - {stato}: {count}")
    
    # Verifica richieste senza spese
    richieste_senza_spese = []
    for r in richieste:
        if len(r.spese) == 0:
            richieste_senza_spese.append(r)
    
    if richieste_senza_spese:
        print(f"ATTENZIONE: {len(richieste_senza_spese)} richieste senza spese")
        for r in richieste_senza_spese:
            print(f"  - ID: {r.id}, Data: {r.data_creazione}, Utente: {r.utente.nome} {r.utente.cognome}")

def check_spese():
    """Verifica la tabella spese"""
    spese = Spesa.query.all()
    print(f"\nSpese totali: {len(spese)}")
    
    # Conteggio per tipo
    tipi = {}
    for s in spese:
        tipi[s.tipo_spesa.name] = tipi.get(s.tipo_spesa.name, 0) + 1
    
    for tipo, count in tipi.items():
        print(f"  - {tipo}: {count}")
    
    # Verifica spese senza documenti
    spese_senza_documenti = []
    for s in spese:
        if len(s.documenti) == 0:
            spese_senza_documenti.append(s)
    
    if spese_senza_documenti:
        print(f"ATTENZIONE: {len(spese_senza_documenti)} spese senza documenti")
        for s in spese_senza_documenti:
            print(f"  - ID: {s.id}, Tipo: {s.tipo_spesa.name}, Importo: {s.importo_richiesto}€")

def check_documenti():
    """Verifica la tabella documenti"""
    documenti = DocumentoSpesa.query.all()
    print(f"\nDocumenti totali: {len(documenti)}")
    
    # Conteggio per tipo
    tipi = {}
    for d in documenti:
        tipi[d.tipo.name] = tipi.get(d.tipo.name, 0) + 1
    
    for tipo, count in tipi.items():
        print(f"  - {tipo}: {count}")
    
    # Verifica documenti con file mancanti
    documenti_file_mancanti = []
    for d in documenti:
        if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], d.percorso_file)):
            documenti_file_mancanti.append(d)
    
    if documenti_file_mancanti:
        print(f"ATTENZIONE: {len(documenti_file_mancanti)} documenti con file mancanti")
        for d in documenti_file_mancanti:
            print(f"  - ID: {d.id}, Tipo: {d.tipo.name}, File: {d.percorso_file}")

if __name__ == "__main__":
    main()