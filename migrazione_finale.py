"""
Script per completare la migrazione del modello di dati da Parcheggio a Viaggi
"""
import sqlite3
import os

# Percorso del database SQLite
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migrazione_finale_log.txt')

# Crea un file di log
with open(log_path, 'w') as log_file:
    log_file.write(f"Migrazione finale da Parcheggio a Viaggi\n")
    log_file.write(f"====================================\n\n")

    # Connessione al database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verifica se esiste la tabella spese_viaggi
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='spese_viaggi'")
        exists_viaggi = cursor.fetchone() is not None
        
        if exists_viaggi:
            log_file.write("La tabella 'spese_viaggi' esiste già.\n")
        else:
            log_file.write("La tabella 'spese_viaggi' non esiste, creando...\n")
            
            # Crea la tabella spese_viaggi
            cursor.execute("""
            CREATE TABLE spese_viaggi (
                id INTEGER PRIMARY KEY,
                viaggio INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (id) REFERENCES spese (id)
            )
            """)
            log_file.write("Tabella 'spese_viaggi' creata con successo.\n")
        
        # Verifica se esiste la tabella spese_parcheggio
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='spese_parcheggio'")
        exists_parcheggio = cursor.fetchone() is not None
        
        if exists_parcheggio:
            log_file.write("\nLa tabella 'spese_parcheggio' esiste.\n")
            
            # Verifica se ci sono dati nella tabella
            cursor.execute("SELECT COUNT(*) FROM spese_parcheggio")
            count_parcheggio = cursor.fetchone()[0]
            
            if count_parcheggio > 0:
                log_file.write(f"La tabella 'spese_parcheggio' contiene {count_parcheggio} record.\n")
                log_file.write("Migrando i dati a 'spese_viaggi'...\n")
                
                # Ottieni tutti i record da spese_parcheggio
                cursor.execute("SELECT id, indirizzo, durata_ore FROM spese_parcheggio")
                parcheggio_records = cursor.fetchall()
                
                # Per ogni record, crea un record equivalente in spese_viaggi
                for record in parcheggio_records:
                    id_spesa, indirizzo, durata_ore = record
                    cursor.execute("INSERT INTO spese_viaggi (id, viaggio) VALUES (?, 1)", (id_spesa,))
                    
                    # Aggiorna anche il tipo nella tabella spese
                    cursor.execute("UPDATE spese SET tipo = 'VIAGGI' WHERE id = ?", (id_spesa,))
                    
                log_file.write("Migrazione dei dati completata.\n")
            else:
                log_file.write("La tabella 'spese_parcheggio' è vuota.\n")
            
            # Elimina la tabella spese_parcheggio se non è più necessaria
            log_file.write("Eliminando la tabella 'spese_parcheggio'...\n")
            cursor.execute("DROP TABLE spese_parcheggio")
            log_file.write("Tabella 'spese_parcheggio' eliminata.\n")
        else:
            log_file.write("\nLa tabella 'spese_parcheggio' non esiste.\n")
        
        # Commit delle modifiche
        conn.commit()
        log_file.write("\nMigrazione completata con successo.\n")
        
    except Exception as e:
        # Rollback in caso di errore
        conn.rollback()
        log_file.write(f"\nErrore durante la migrazione: {e}\n")
    finally:
        # Chiudi la connessione
        conn.close()
        
print(f"Log della migrazione finale scritto in: {log_path}")
