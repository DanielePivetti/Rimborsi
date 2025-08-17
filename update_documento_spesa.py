"""
Script per aggiornare il campo file_path nella tabella documenti_spesa e renderlo opzionale
"""
import sys
import os
import sqlite3

# Percorso del database SQLite
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documento_spesa_update_log.txt')

# Crea un file di log
with open(log_path, 'w') as log_file:
    log_file.write(f"Inizio migrazione per rendere file_path opzionale in documenti_spesa\n")
    log_file.write(f"Database: {db_path}\n\n")

    # Connessione al database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Controlla se la tabella documenti_spesa esiste
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documenti_spesa'")
        if not cursor.fetchone():
            log_file.write("La tabella documenti_spesa non esiste nel database.\n")
            log_file.write("Migrazione annullata.\n")
            conn.close()
            sys.exit(1)
        
        # Backup dei dati esistenti
        log_file.write("Backup dei dati esistenti...\n")
        cursor.execute("SELECT * FROM documenti_spesa")
        records = cursor.fetchall()
        log_file.write(f"Trovati {len(records)} record da migrare.\n")
        
        # Crea una tabella temporanea
        log_file.write("Creazione tabella temporanea...\n")
        cursor.execute("""
        CREATE TABLE documenti_spesa_temp (
            id INTEGER PRIMARY KEY,
            spesa_id INTEGER NOT NULL,
            tipo VARCHAR(20) NOT NULL,
            numero VARCHAR(100),
            data DATE NOT NULL,
            descrizione TEXT,
            file_path VARCHAR(255),
            data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_modifica DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(spesa_id) REFERENCES spese(id)
        )
        """)
        
        # Copia i dati nella tabella temporanea
        log_file.write("Copia dei dati nella tabella temporanea...\n")
        cursor.execute("""
        INSERT INTO documenti_spesa_temp 
        SELECT id, spesa_id, tipo, numero, data, descrizione, file_path, 
               data_creazione, data_modifica
        FROM documenti_spesa
        """)
        
        # Elimina la tabella originale
        log_file.write("Eliminazione della tabella originale...\n")
        cursor.execute("DROP TABLE documenti_spesa")
        
        # Rinomina la tabella temporanea
        log_file.write("Rinomina della tabella temporanea in documenti_spesa...\n")
        cursor.execute("ALTER TABLE documenti_spesa_temp RENAME TO documenti_spesa")
        
        # Aggiorna gli indici se necessario
        # ...
        
        # Conferma le modifiche
        conn.commit()
        log_file.write("\nMigrazione completata con successo!\n")
        
    except Exception as e:
        conn.rollback()
        log_file.write(f"\nErrore durante la migrazione: {str(e)}\n")
        log_file.write("Migrazione annullata, nessuna modifica è stata apportata al database.\n")
    finally:
        conn.close()

print(f"Migrazione completata. Controlla il log in {log_path}")
