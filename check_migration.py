"""
Script per verificare lo stato del database dopo la migrazione
"""
import sys
import os

# Aggiungi la directory principale al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app import create_app, db
from app.models.spesa import Spesa, TipoSpesa, SpesaViaggi

app = create_app()

with app.app_context():
    # Verifica se ci sono ancora spese di tipo PARCHEGGIO
    spese_parcheggio = Spesa.query.filter_by(tipo='05').all()
    print(f"Spese di tipo PARCHEGGIO (dovrebbero essere 0): {len(spese_parcheggio)}")
    
    # Verifica se ci sono spese di tipo VIAGGI
    spese_viaggi = Spesa.query.filter_by(tipo='07').all()
    print(f"Spese di tipo VIAGGI: {len(spese_viaggi)}")
    
    # Verifica le spese con discriminator_type specifico
    viaggi_objects = SpesaViaggi.query.all()
    print(f"Oggetti SpesaViaggi: {len(viaggi_objects)}")
    
    # Mostra i dettagli delle spese viaggi
    if viaggi_objects:
        print("\nDettagli delle spese di tipo VIAGGI:")
        for v in viaggi_objects:
            print(f"ID: {v.id}, Data: {v.data_spesa}, Importo: {v.importo_richiesto}, Viaggio: {v.viaggio}")
