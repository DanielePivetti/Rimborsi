"""
Script per applicare le migrazioni esistenti al database
"""
import sys
import os

# Aggiungi la directory principale al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app import create_app, db

app = create_app()

with app.app_context():
    from flask_migrate import upgrade
    
    print("Avvio dell'applicazione delle migrazioni al database...")
    
    # Applica tutte le migrazioni disponibili
    upgrade()
    
    print("Migrazione completata con successo.")
