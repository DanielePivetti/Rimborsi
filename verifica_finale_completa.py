"""
Script finale per verificare la coerenza del database dopo la migrazione
"""
import sqlite3
import os

# Percorso del database SQLite
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verifica_finale_completa_log.txt')

# Crea un file di log
with open(log_path, 'w') as log_file:
    log_file.write(f"Verifica finale completa del database dopo la migrazione\n")
    log_file.write(f"================================================\n\n")

    # Connessione al database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Verifica le tabelle relative alle spese
        log_file.write("1. Verifica delle tabelle relative alle spese:\n")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'spese%'")
        tables = cursor.fetchall()
        for table in tables:
            log_file.write(f"- {table[0]}\n")
        
        # 2. Verifica della struttura di ogni tabella
        log_file.write("\n2. Verifica della struttura delle tabelle:\n")
        for table in tables:
            table_name = table[0]
            log_file.write(f"\nTabella: {table_name}\n")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                log_file.write(f"  - {col[1]} ({col[2]})\n")
            
            # Conteggio dei record
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            log_file.write(f"  Numero di record: {count}\n")
        
        # 3. Verifica dei tipi di spesa presenti
        log_file.write("\n3. Verifica dei tipi di spesa presenti nel database:\n")
        cursor.execute("SELECT DISTINCT tipo FROM spese")
        tipi_spesa = cursor.fetchall()
        for tipo in tipi_spesa:
            log_file.write(f"- {tipo[0]}\n")
            # Conteggio per ogni tipo
            cursor.execute(f"SELECT COUNT(*) FROM spese WHERE tipo = ?", (tipo[0],))
            count = cursor.fetchone()[0]
            log_file.write(f"  Numero di record: {count}\n")
        
        # 4. Verifica dell'integrità referenziale
        log_file.write("\n4. Verifica dell'integrità referenziale:\n")
        
        # Verifica che ogni spesa specifica abbia una corrispondente spesa principale
        for table_name in ['spese_carburante', 'spese_vitto', 'spese_pedaggi', 'spese_ripristino', 'spese_viaggi', 'spese_altro']:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE id NOT IN (SELECT id FROM spese)")
            count = cursor.fetchone()[0]
            log_file.write(f"- {table_name}: {count} record orfani (dovrebbe essere 0)\n")
        
        # 5. Verifica dell'assenza della tabella spese_parcheggio
        log_file.write("\n5. Verifica dell'assenza della tabella spese_parcheggio:\n")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='spese_parcheggio'")
        exists_parcheggio = cursor.fetchone() is not None
        if exists_parcheggio:
            log_file.write("ATTENZIONE: La tabella 'spese_parcheggio' esiste ancora!\n")
        else:
            log_file.write("OK: La tabella 'spese_parcheggio' è stata eliminata correttamente.\n")
        
        # 6. Verifica che non ci siano più riferimenti a 'PARCHEGGIO' nel database
        log_file.write("\n6. Verifica dell'assenza di riferimenti a 'PARCHEGGIO' nel database:\n")
        cursor.execute("SELECT COUNT(*) FROM spese WHERE tipo = 'PARCHEGGIO'")
        count = cursor.fetchone()[0]
        log_file.write(f"- Spese con tipo='PARCHEGGIO': {count} (dovrebbe essere 0)\n")
        
        # 7. Verifica della presenza delle spese di tipo VIAGGI
        log_file.write("\n7. Verifica della presenza di spese di tipo VIAGGI:\n")
        cursor.execute("SELECT COUNT(*) FROM spese WHERE tipo = 'VIAGGI'")
        count = cursor.fetchone()[0]
        log_file.write(f"- Spese con tipo='VIAGGI': {count}\n")
        
        log_file.write("\nVerifica completata.\n")
        
    except Exception as e:
        log_file.write(f"\nErrore durante la verifica: {e}\n")
    finally:
        # Chiudi la connessione
        conn.close()
        
print(f"Log della verifica finale completa scritto in: {log_path}")
