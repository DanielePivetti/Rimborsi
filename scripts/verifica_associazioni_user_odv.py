"""
Script per visualizzare le associazioni attuali tra utenti compilatori e organizzazioni (ODV).
Questo script mostra tutte le associazioni presenti nella tabella user_odv_association.
"""

import os
import sys
from datetime import datetime

# Aggiungi la directory principale al path per importare l'app
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.odv import Odv
from app.models.user_odv import user_odv_association
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("\n=== ASSOCIAZIONI TRA UTENTI E ORGANIZZAZIONI ===\n")
    
    # Query diretta sulla tabella di associazione
    result = db.session.execute(text("""
        SELECT u.id as user_id, u.username, u.nome, u.cognome, u.ruolo,
               o.id as odv_id, o.nome as odv_nome, o.acronimo,
               ua.data_assegnazione, au.username as assegnato_da_username
        FROM user_odv_association ua
        JOIN user u ON ua.user_id = u.id
        JOIN odv o ON ua.odv_id = o.id
        LEFT JOIN user au ON ua.assegnato_da = au.id
        ORDER BY u.username, o.nome
    """))
    
    rows = result.fetchall()
    
    if not rows:
        print("Nessuna associazione trovata tra utenti e organizzazioni.")
        print("Gli amministratori dovranno creare associazioni tramite l'interfaccia di gestione.")
    else:
        print(f"Trovate {len(rows)} associazioni:")
        print("\n{:<5} {:<15} {:<20} {:<20} {:<15} {:<5} {:<30} {:<15} {:<20} {:<15}".format(
            "UID", "Username", "Nome", "Cognome", "Ruolo", "OID", "Organizzazione", "Acronimo", "Data Assegnazione", "Assegnato Da"
        ))
        print("-" * 150)
        
        for row in rows:
            # Gestione formato data
            data_str = ""
            if row.data_assegnazione:
                try:
                    # Se è già un oggetto datetime
                    if isinstance(row.data_assegnazione, datetime):
                        data_str = row.data_assegnazione.strftime('%d/%m/%Y %H:%M')
                    else:
                        # Se è una stringa
                        data_str = row.data_assegnazione
                except:
                    data_str = str(row.data_assegnazione)
            
            print("{:<5} {:<15} {:<20} {:<20} {:<15} {:<5} {:<30} {:<15} {:<20} {:<15}".format(
                row.user_id, row.username, row.nome or "", row.cognome or "", row.ruolo,
                row.odv_id, row.odv_nome, row.acronimo or "", 
                data_str,
                row.assegnato_da_username or ""
            ))
    
    print("\n=== UTENTI SENZA ORGANIZZAZIONI ASSOCIATE ===\n")
    
    # Trova utenti compilatori che non hanno organizzazioni associate
    compilatori_senza_odv = db.session.execute(text("""
        SELECT u.id, u.username, u.nome, u.cognome
        FROM user u
        WHERE u.ruolo = 'utente'
        AND u.id NOT IN (SELECT user_id FROM user_odv_association)
        ORDER BY u.username
    """))
    
    rows = compilatori_senza_odv.fetchall()
    
    if not rows:
        print("Tutti i compilatori hanno almeno un'organizzazione associata.")
    else:
        print(f"Trovati {len(rows)} compilatori senza organizzazioni associate:")
        print("\n{:<5} {:<15} {:<20} {:<20}".format("ID", "Username", "Nome", "Cognome"))
        print("-" * 60)
        
        for row in rows:
            print("{:<5} {:<15} {:<20} {:<20}".format(
                row.id, row.username, row.nome or "", row.cognome or ""
            ))
            
    print("\n=== ORGANIZZAZIONI SENZA COMPILATORI ASSOCIATI ===\n")
    
    # Trova organizzazioni che non hanno compilatori associati
    odv_senza_compilatori = db.session.execute(text("""
        SELECT o.id, o.nome, o.acronimo
        FROM odv o
        WHERE o.id NOT IN (SELECT odv_id FROM user_odv_association)
        ORDER BY o.nome
    """))
    
    rows = odv_senza_compilatori.fetchall()
    
    if not rows:
        print("Tutte le organizzazioni hanno almeno un compilatore associato.")
    else:
        print(f"Trovate {len(rows)} organizzazioni senza compilatori associati:")
        print("\n{:<5} {:<30} {:<15}".format("ID", "Nome", "Acronimo"))
        print("-" * 50)
        
        for row in rows:
            print("{:<5} {:<30} {:<15}".format(
                row.id, row.nome, row.acronimo or ""
            ))
