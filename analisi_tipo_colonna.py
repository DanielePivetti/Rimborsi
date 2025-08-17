"""
Script per esaminare in dettaglio la colonna tipo nella tabella spese
"""
import sqlite3
import os

# Percorso del database SQLite
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tipo_colonna_log.txt')

# Crea un file di log
with open(log_path, 'w') as log_file:
    log_file.write(f"Analisi dettagliata della colonna 'tipo' nella tabella 'spese'\n")
    log_file.write(f"======================================================\n\n")

    # Connessione al database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Ottieni i dettagli della colonna 'tipo'
        cursor.execute("PRAGMA table_info(spese)")
        columns = cursor.fetchall()
        tipo_column = next((col for col in columns if col[1] == 'tipo'), None)
        
        if tipo_column:
            log_file.write(f"Definizione della colonna 'tipo':\n")
            log_file.write(f"  Nome: {tipo_column[1]}\n")
            log_file.write(f"  Tipo di dati: {tipo_column[2]}\n")
            log_file.write(f"  NotNull: {tipo_column[3]}\n")
            log_file.write(f"  Default: {tipo_column[4]}\n")
            log_file.write(f"  PK: {tipo_column[5]}\n\n")
        
        # Ottieni tutti i valori distinti dalla colonna 'tipo'
        cursor.execute("SELECT tipo, COUNT(*) FROM spese GROUP BY tipo")
        tipo_values = cursor.fetchall()
        
        log_file.write(f"Valori distinti nella colonna 'tipo':\n")
        for value, count in tipo_values:
            log_file.write(f"  Valore: '{value}', Occorrenze: {count}\n")
        
        # Estrai alcuni esempi di record con ciascun tipo
        log_file.write(f"\nEsempi di record per ciascun tipo di spesa:\n")
        for value, _ in tipo_values:
            cursor.execute(f"SELECT id, richiesta_id, tipo, data_spesa, importo_richiesto FROM spese WHERE tipo = ? LIMIT 2", (value,))
            examples = cursor.fetchall()
            
            log_file.write(f"\n  Tipo: '{value}':\n")
            for ex in examples:
                log_file.write(f"    ID: {ex[0]}, Richiesta: {ex[1]}, Data: {ex[2]}, Importo: {ex[3]}\n")
                
        # Verifica se ci sono tabelle specifiche per tipo
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'spese_%'")
        related_tables = cursor.fetchall()
        
        log_file.write(f"\nTabelle correlate per i tipi di spesa:\n")
        for table in related_tables:
            log_file.write(f"  {table[0]}\n")
            
            # Ottieni la struttura della tabella
            cursor.execute(f"PRAGMA table_info({table[0]})")
            table_columns = cursor.fetchall()
            
            log_file.write(f"    Colonne:\n")
            for col in table_columns:
                log_file.write(f"      {col[1]} ({col[2]})\n")
            
            # Ottieni il numero di record nella tabella
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            log_file.write(f"    Numero di record: {count}\n\n")
            
    except Exception as e:
        log_file.write(f"Errore durante l'analisi del database: {e}\n")
    finally:
        # Chiudi la connessione
        conn.close()
        
print(f"Log dell'analisi scritto in: {log_path}")
