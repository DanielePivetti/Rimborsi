"""
Script per modificare gli utenti e creare associazioni tra utenti e organizzazioni.
Operazioni:
1. Cancellare Mario Rossi
2. Modificare username di Giulia Bianchi in Bianchi_g
3. Associare Bianchi_g alle ODV con ID 1 e 3
4. Associare Pivetti_d all'ODV con ID 2
"""

import os
import sys
from datetime import datetime

# Aggiungi la directory principale al path per importare l'app
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.odv import Odv
from sqlalchemy import text

app = create_app()

def main():
    with app.app_context():
        print("\n=== MODIFICHE AGLI UTENTI E ASSOCIAZIONI ODV ===\n")
        
        # 1. Cancellare Mario Rossi
        mario = db.session.execute(text("SELECT * FROM user WHERE username = 'mario'")).first()
        if mario:
            print(f"Eliminazione utente: {mario.username} ({mario.nome} {mario.cognome})")
            db.session.execute(text(f"DELETE FROM user WHERE id = {mario.id}"))
            db.session.commit()
            print("✓ Utente eliminato con successo.")
        else:
            print("✗ Utente Mario Rossi non trovato.")
        
        # 2. Modificare username di Giulia Bianchi
        giulia = db.session.execute(text("SELECT * FROM user WHERE username = 'giulia'")).first()
        if giulia:
            print(f"Modifica username: {giulia.username} -> Bianchi_g")
            db.session.execute(text(f"UPDATE user SET username = 'Bianchi_g' WHERE id = {giulia.id}"))
            db.session.commit()
            print("✓ Username modificato con successo.")
        else:
            print("✗ Utente Giulia Bianchi non trovato.")
        
        # Ottieni gli ID degli amministratori per registrare chi ha fatto l'associazione
        admin = db.session.execute(text("SELECT * FROM user WHERE ruolo = 'amministratore' LIMIT 1")).first()
        admin_id = admin.id if admin else None
        
        # 3. Associare Bianchi_g alle ODV con ID 1 e 3
        bianchi_g = db.session.execute(text("SELECT * FROM user WHERE username = 'Bianchi_g'")).first()
        if bianchi_g:
            odv1 = db.session.execute(text("SELECT * FROM odv WHERE id = 1")).first()
            odv3 = db.session.execute(text("SELECT * FROM odv WHERE id = 3")).first()
            
            if odv1 and odv3:
                print(f"Associazione: {bianchi_g.username} -> ODV ID 1 ({odv1.nome})")
                print(f"Associazione: {bianchi_g.username} -> ODV ID 3 ({odv3.nome})")
                
                # Inserisci direttamente nella tabella di associazione
                now = datetime.utcnow()
                db.session.execute(text(f"""
                    INSERT INTO user_odv_association (user_id, odv_id, data_assegnazione, assegnato_da)
                    VALUES ({bianchi_g.id}, 1, '{now}', {admin_id if admin_id else 'NULL'})
                """))
                
                db.session.execute(text(f"""
                    INSERT INTO user_odv_association (user_id, odv_id, data_assegnazione, assegnato_da)
                    VALUES ({bianchi_g.id}, 3, '{now}', {admin_id if admin_id else 'NULL'})
                """))
                
                db.session.commit()
                print("✓ Associazioni per Bianchi_g create con successo.")
            else:
                print("✗ Una o più ODV non trovate.")
        else:
            print("✗ Utente Bianchi_g non trovato.")
        
        # 4. Associare Pivetti_d all'ODV con ID 2
        pivetti = db.session.execute(text("SELECT * FROM user WHERE username = 'Pivetti_d'")).first()
        if pivetti:
            odv2 = db.session.execute(text("SELECT * FROM odv WHERE id = 2")).first()
            
            if odv2:
                print(f"Associazione: {pivetti.username} -> ODV ID 2 ({odv2.nome})")
                
                # Inserisci direttamente nella tabella di associazione
                now = datetime.utcnow()
                db.session.execute(text(f"""
                    INSERT INTO user_odv_association (user_id, odv_id, data_assegnazione, assegnato_da)
                    VALUES ({pivetti.id}, 2, '{now}', {admin_id if admin_id else 'NULL'})
                """))
                
                db.session.commit()
                print("✓ Associazione per Pivetti_d creata con successo.")
            else:
                print("✗ ODV con ID 2 non trovata.")
        else:
            print("✗ Utente Pivetti_d non trovato.")
        
        print("\nOperazioni completate.")

if __name__ == "__main__":
    main()
