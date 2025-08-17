"""
Script per aggiornare il tipo di spesa da PARCHEGGIO a VIAGGI
"""
import sqlite3
import os

# Percorso del database SQLite
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'update_tipo_spesa_log.txt')

# Crea un file di log
with open(log_path, 'w') as log_file:
    log_file.write(f"Connessione al database: {db_path}\n\n")

    # Connessione al database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verifica valori esistenti per la colonna 'tipo'
        cursor.execute("SELECT DISTINCT tipo FROM spese")
        tipi_spesa = [row[0] for row in cursor.fetchall()]
        log_file.write(f"Tipi di spesa esistenti: {tipi_spesa}\n")
        
        # Aggiorna i record con tipo PARCHEGGIO a VIAGGI
        cursor.execute("UPDATE spese SET tipo = 'VIAGGI' WHERE tipo = 'PARCHEGGIO'")
        rows_updated = cursor.rowcount
        log_file.write(f"Aggiornati {rows_updated} record da PARCHEGGIO a VIAGGI\n")
        
        # Verifica se ci sono ancora record con tipo PARCHEGGIO
        cursor.execute("SELECT COUNT(*) FROM spese WHERE tipo = 'PARCHEGGIO'")
        count_parcheggio = cursor.fetchone()[0]
        log_file.write(f"Record rimasti con tipo PARCHEGGIO (dovrebbe essere 0): {count_parcheggio}\n")
        
        # Verifica quanti record hanno ora il tipo VIAGGI
        cursor.execute("SELECT COUNT(*) FROM spese WHERE tipo = 'VIAGGI'")
        count_viaggi = cursor.fetchone()[0]
        log_file.write(f"Record con tipo VIAGGI: {count_viaggi}\n")
        
        # Commit delle modifiche
        conn.commit()
        log_file.write("\nModifiche applicate con successo al database.\n")
        
        # Verifica i tipi di spesa dopo l'aggiornamento
        cursor.execute("SELECT DISTINCT tipo FROM spese")
        tipi_spesa_dopo = [row[0] for row in cursor.fetchall()]
        log_file.write(f"\nTipi di spesa dopo l'aggiornamento: {tipi_spesa_dopo}\n")
        
    except Exception as e:
        # Rollback in caso di errore
        conn.rollback()
        log_file.write(f"Errore durante l'aggiornamento del database: {e}\n")
    finally:
        # Chiudi la connessione
        conn.close()
        
print(f"Log dell'aggiornamento scritto in: {log_path}")
