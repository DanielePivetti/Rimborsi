from app import db, create_app
from app.models.richiesta import Richiesta
from app.models.spesa import Spesa
import os
from sqlalchemy import text

app = create_app()
with app.app_context():
    # ID della richiesta da eliminare
    richiesta_id = 2
    
    print(f"Eliminazione della richiesta con ID {richiesta_id} e tutti gli elementi associati...")
    
    # Verifica se la richiesta esiste
    richiesta = Richiesta.query.get(richiesta_id)
    if not richiesta:
        print(f"La richiesta con ID {richiesta_id} non esiste.")
        exit()
    
    print(f"Trovata richiesta: ID {richiesta.id}, ODV: {richiesta.odv.nome}")
    
    # Utilizziamo SQL diretto per evitare problemi con gli enum
    try:
        # 1. Elimina i documenti delle spese
        result = db.session.execute(text(f"DELETE FROM documenti_spesa WHERE spesa_id IN (SELECT id FROM spese WHERE richiesta_id = {richiesta_id})"))
        print(f"Eliminati {result.rowcount} documenti spesa.")
        
        # 2. Elimina le spese specifiche (tabelle figlie)
        for table in ['spese_carburante', 'spese_vitto', 'spese_pedaggi', 'spese_ripristino', 'spese_parcheggio', 'spese_altro']:
            result = db.session.execute(text(f"DELETE FROM {table} WHERE id IN (SELECT id FROM spese WHERE richiesta_id = {richiesta_id})"))
            print(f"Eliminati {result.rowcount} record da {table}.")
        
        # 3. Elimina le spese
        result = db.session.execute(text(f"DELETE FROM spese WHERE richiesta_id = {richiesta_id}"))
        print(f"Eliminate {result.rowcount} spese.")
        
        # 4. Elimina gli impieghi mezzi
        result = db.session.execute(text(f"DELETE FROM impiego_mezzo WHERE richiesta_id = {richiesta_id}"))
        print(f"Eliminati {result.rowcount} impieghi mezzo.")
        
        # 5. Elimina la richiesta
        result = db.session.execute(text(f"DELETE FROM richieste WHERE id = {richiesta_id}"))
        print(f"Eliminata richiesta con ID {richiesta_id}.")
        
        # Commit delle modifiche
        db.session.commit()
        print("Commit eseguito con successo!")
        print("Pulizia completata. La richiesta e tutti gli elementi associati sono stati eliminati.")
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante l'eliminazione: {str(e)}")
        print("Rollback eseguito. Nessuna modifica è stata salvata nel database.")
