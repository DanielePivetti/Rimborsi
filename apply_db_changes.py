"""
Script per applicare manualmente le modifiche necessarie al database
"""
import sqlite3
import os

# Percorso del database SQLite
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db_migration_log.txt')

# Crea un file di log
with open(log_path, 'w') as log_file:
    log_file.write(f"Connessione al database: {db_path}\n")

    # Connessione al database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Aggiorna i record esistenti che usano il tipo spesa PARCHEGGIO (05)
        cursor.execute("UPDATE spese SET tipo = '07' WHERE tipo = '05'")
        rows_updated_tipo = cursor.rowcount
        log_file.write(f"Aggiornati {rows_updated_tipo} record con tipo='05' a tipo='07'\n")
        
        # 2. Aggiorna il discriminator_type per le spese di parcheggio
        cursor.execute("UPDATE spese SET discriminator_type = 'spesa_viaggi' WHERE discriminator_type = 'spesa_parcheggio'")
        rows_updated_discriminator = cursor.rowcount
        log_file.write(f"Aggiornati {rows_updated_discriminator} record con discriminator_type='spesa_parcheggio' a discriminator_type='spesa_viaggi'\n")
        
        # 3. Verifica l'aggiornamento
        cursor.execute("SELECT COUNT(*) FROM spese WHERE tipo = '05'")
        count_parcheggio = cursor.fetchone()[0]
        log_file.write(f"Record rimasti con tipo='05' (dovrebbe essere 0): {count_parcheggio}\n")
        
        cursor.execute("SELECT COUNT(*) FROM spese WHERE tipo = '07'")
        count_viaggi = cursor.fetchone()[0]
        log_file.write(f"Record con tipo='07': {count_viaggi}\n")
        
        # Commit delle modifiche
        conn.commit()
        log_file.write("Modifiche applicate con successo al database.\n")

    except Exception as e:
        # Rollback in caso di errore
        conn.rollback()
        log_file.write(f"Errore durante l'aggiornamento del database: {e}\n")
    finally:
        # Chiudi la connessione
        conn.close()
        
print(f"Log della migrazione scritto in: {log_path}")
