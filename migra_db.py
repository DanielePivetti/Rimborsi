"""
Script per generare le migrazioni del database
"""
import sys
import os

# Aggiungi la directory principale al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app import create_app, db

app = create_app()

with app.app_context():
    from flask_migrate import stamp, migrate, upgrade
    
    print("Avvio migrazione del database...")
    
    # Crea un nuovo script di migrazione
    migrate()
    
    # Applica la migrazione
    upgrade()
    
    print("Migrazione completata con successo.")
