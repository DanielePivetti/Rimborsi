"""
Script per verificare la struttura della tabella spese
"""
import sqlite3
import os

# Percorso del database SQLite
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'table_structure_log.txt')

# Crea un file di log
with open(log_path, 'w') as log_file:
    log_file.write(f"Connessione al database: {db_path}\n\n")

    # Connessione al database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Ottieni informazioni sulla struttura della tabella spese
        cursor.execute("PRAGMA table_info(spese)")
        columns = cursor.fetchall()
        
        log_file.write("Struttura della tabella 'spese':\n")
        log_file.write("-----------------------------\n")
        for col in columns:
            log_file.write(f"Colonna: {col[1]}, Tipo: {col[2]}, NotNull: {col[3]}, Default: {col[4]}, PK: {col[5]}\n")
        
        # Verifica se esiste una colonna type o simile per il polimorfismo
        has_type_column = any(col[1] == 'type' for col in columns)
        log_file.write(f"\nColonna 'type' per polimorfismo: {'Presente' if has_type_column else 'Assente'}\n")
        
        # Ottieni alcuni record di esempio dalla tabella spese
        cursor.execute("SELECT * FROM spese LIMIT 5")
        records = cursor.fetchall()
        
        log_file.write("\nEsempio di record nella tabella 'spese':\n")
        log_file.write("-------------------------------------\n")
        
        if records:
            # Ottieni i nomi delle colonne
            column_names = [col[1] for col in columns]
            
            for i, record in enumerate(records):
                log_file.write(f"Record {i+1}:\n")
                for j, value in enumerate(record):
                    if j < len(column_names):
                        log_file.write(f"  {column_names[j]}: {value}\n")
                log_file.write("\n")
        else:
            log_file.write("Nessun record trovato nella tabella 'spese'.\n")
        
        # Verifica la presenza di una colonna per il tipo di spesa
        log_file.write("\nRicerca di colonne relative al tipo di spesa:\n")
        log_file.write("-----------------------------------------\n")
        for col in columns:
            if 'tipo' in col[1].lower() or 'type' in col[1].lower():
                log_file.write(f"Possibile colonna per il tipo di spesa: {col[1]}\n")
                
                # Se troviamo una colonna tipo, mostra i valori distinti
                cursor.execute(f"SELECT DISTINCT {col[1]} FROM spese")
                distinct_values = cursor.fetchall()
                log_file.write(f"Valori distinti per {col[1]}: {distinct_values}\n")

    except Exception as e:
        log_file.write(f"Errore durante l'analisi del database: {e}\n")
    finally:
        # Chiudi la connessione
        conn.close()
        
print(f"Log della struttura della tabella scritto in: {log_path}")
