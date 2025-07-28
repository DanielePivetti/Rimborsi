"""
Script per verificare lo stato del database dopo la migrazione e scrivere i risultati in un file
"""
import sys
import os

# Aggiungi la directory principale al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app import create_app, db
from app.models.spesa import Spesa, TipoSpesa, SpesaViaggi

# File di output con percorso assoluto
output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migration_results.txt')

app = create_app()

with app.app_context():
    # Apri il file per scrivere i risultati
    with open(output_file, 'w') as f:
        f.write("Risultati della verifica della migrazione\n")
        f.write("========================================\n\n")
        
        # Verifica se ci sono ancora spese di tipo PARCHEGGIO
        try:
            spese_parcheggio = Spesa.query.filter_by(tipo='05').all()
            f.write(f"Spese di tipo PARCHEGGIO (dovrebbero essere 0): {len(spese_parcheggio)}\n")
        except Exception as e:
            f.write(f"Errore nel conteggio delle spese PARCHEGGIO: {str(e)}\n")
        
        # Verifica se ci sono spese di tipo VIAGGI
        try:
            spese_viaggi = Spesa.query.filter_by(tipo='07').all()
            f.write(f"Spese di tipo VIAGGI: {len(spese_viaggi)}\n")
        except Exception as e:
            f.write(f"Errore nel conteggio delle spese VIAGGI: {str(e)}\n")
        
        # Verifica le spese con discriminator_type specifico
        try:
            viaggi_objects = SpesaViaggi.query.all()
            f.write(f"Oggetti SpesaViaggi: {len(viaggi_objects)}\n")
            
            # Mostra i dettagli delle spese viaggi
            if viaggi_objects:
                f.write("\nDettagli delle spese di tipo VIAGGI:\n")
                for v in viaggi_objects:
                    f.write(f"ID: {v.id}, Data: {v.data_spesa}, Importo: {v.importo_richiesto}, Viaggio: {v.viaggio}\n")
        except Exception as e:
            f.write(f"Errore nell'accesso agli oggetti SpesaViaggi: {str(e)}\n")
        
        # Verifica anche la migration history
        try:
            from flask_migrate import current
            migration_version = current()
            f.write(f"\nVersione attuale della migrazione: {migration_version}\n")
        except Exception as e:
            f.write(f"Errore nell'ottenere la versione della migrazione: {str(e)}\n")
        
        f.write("\nVerifica completata.\n")

print(f"Risultati scritti nel file: {output_file}")
