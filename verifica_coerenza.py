"""
Script per verificare la coerenza del codice dopo la migrazione
"""
import os
import re

def cerca_riferimenti(directory, pattern, estensioni=None):
    """Cerca ricorrenze di un pattern in tutti i file di una directory"""
    risultati = []
    
    # Filtra solo i file con le estensioni specificate
    if estensioni:
        def filtro(f):
            return any(f.endswith(ext) for ext in estensioni)
    else:
        def filtro(f):
            return True
    
    # Cerca in modo ricorsivo in tutte le sottodirectory
    for root, dirs, files in os.walk(directory):
        for file in files:
            if filtro(file):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        contenuto = f.read()
                        matches = re.findall(pattern, contenuto, re.IGNORECASE)
                        if matches:
                            risultati.append((filepath, matches))
                except Exception as e:
                    print(f"Errore durante la lettura di {filepath}: {e}")
    
    return risultati

# Directory principale del progetto
directory_base = os.path.dirname(os.path.abspath(__file__))

# File di output
output_file = os.path.join(directory_base, 'verifica_coerenza_log.txt')

# Estensioni di file da controllare
estensioni = ['.py', '.html', '.js', '.css']

# Pattern da cercare
pattern_parcheggio = r'parcheggio'

# Cerca riferimenti a "parcheggio"
risultati_parcheggio = cerca_riferimenti(directory_base, pattern_parcheggio, estensioni)

# Scrivi i risultati nel file di log
with open(output_file, 'w', encoding='utf-8') as log:
    log.write("=== Riferimenti a 'parcheggio' ===\n")
    if not risultati_parcheggio:
        log.write("Nessun riferimento trovato.\n")
    else:
        for filepath, matches in risultati_parcheggio:
            log.write(f"{filepath}: {len(matches)} occorrenze\n")
            # Visualizza il contesto delle occorrenze
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if re.search(pattern_parcheggio, line, re.IGNORECASE):
                            log.write(f"  Riga {i+1}: {line.strip()}\n")
            except Exception as e:
                log.write(f"  Errore durante la lettura del file: {e}\n")

    # Verifica anche file di migrazione e backup per coerenza
    log.write("\n=== File di migrazione e backup ===\n")
    for root, dirs, files in os.walk(directory_base):
        for file in files:
            if '.bak' in file or '.old' in file or '.new' in file:
                log.write(f"File di backup: {os.path.join(root, file)}\n")

print(f"Risultati scritti nel file: {output_file}")
