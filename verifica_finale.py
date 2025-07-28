"""
Script per verificare lo stato finale del database dopo la migrazione
"""
import sqlite3
import os

# Percorso del database SQLite
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verifica_finale_log.txt')

# Crea un file di log
with open(log_path, 'w') as log_file:
    log_file.write(f"Verifica finale del database dopo la migrazione\n")
    log_file.write(f"==========================================\n\n")

    # Connessione al database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verifica le tabelle esistenti
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'spese%'")
        tables = cursor.fetchall()
        
        log_file.write("Tabelle relative alle spese:\n")
        for table in tables:
            log_file.write(f"- {table[0]}\n")
        
        # Verifica i tipi di spesa presenti
        cursor.execute("SELECT DISTINCT tipo FROM spese")
        tipi_spesa = cursor.fetchall()
        
        log_file.write("\nTipi di spesa presenti nel database:\n")
        for tipo in tipi_spesa:
            log_file.write(f"- {tipo[0]}\n")
        
        # Verifica la presenza della tabella spese_viaggi
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='spese_viaggi'")
        exists_viaggi = cursor.fetchone() is not None
        
        if exists_viaggi:
            log_file.write("\nLa tabella 'spese_viaggi' esiste.\n")
            
            # Verifica la struttura della tabella
            cursor.execute("PRAGMA table_info(spese_viaggi)")
            columns = cursor.fetchall()
            
            log_file.write("Struttura della tabella 'spese_viaggi':\n")
            for col in columns:
                log_file.write(f"- {col[1]} ({col[2]})\n")
        else:
            log_file.write("\nATTENZIONE: La tabella 'spese_viaggi' non esiste!\n")
        
        # Verifica l'assenza della tabella spese_parcheggio
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='spese_parcheggio'")
        exists_parcheggio = cursor.fetchone() is not None
        
        if exists_parcheggio:
            log_file.write("\nATTENZIONE: La tabella 'spese_parcheggio' esiste ancora!\n")
        else:
            log_file.write("\nLa tabella 'spese_parcheggio' è stata eliminata correttamente.\n")
        
        log_file.write("\nVerifica completata.\n")
        
    except Exception as e:
        log_file.write(f"\nErrore durante la verifica: {e}\n")
    finally:
        # Chiudi la connessione
        conn.close()
        
print(f"Log della verifica finale scritto in: {log_path}")
