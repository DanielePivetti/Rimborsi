"""
Script per testare specificamente la rotta documenti_spesa
"""
import os
import sys
import traceback
from app import create_app, db
from app.models.spesa import Spesa
from flask import url_for

# Configura l'app
app = create_app()

def check_route_definition():
    """Controlla la definizione della rotta nel blueprint"""
    print("=== Controllo definizione rotte nel blueprint ===")
    try:
        from app.blueprints.spesa import spesa_bp
        print(f"Blueprint trovato: {spesa_bp.name}, url_prefix: {spesa_bp.url_prefix}")
        
        # Stampa tutte le rotte registrate nel blueprint
        print("\nRotte registrate nel blueprint:")
        for rule in app.url_map.iter_rules():
            if rule.endpoint.startswith('spesa.'):
                print(f"Rule: {rule}, Endpoint: {rule.endpoint}, Methods: {rule.methods}")
    except Exception as e:
        print(f"Errore durante il controllo del blueprint: {str(e)}")
        traceback.print_exc()

def check_route_handling():
    """Controlla la gestione della rotta"""
    print("\n=== Controllo gestione rotta ===")
    with app.test_request_context():
        try:
            print("Generazione URL per documenti_spesa:")
            url = url_for('spesa.documenti_spesa', spesa_id=1)
            print(f"URL generato: {url}")
        except Exception as e:
            print(f"Errore nella generazione URL per documenti_spesa: {str(e)}")
            traceback.print_exc()
        
        try:
            print("\nGenerazione URL per gestisci_documenti (alias):")
            # Se questo fallisce, significa che l'alias non è stato registrato correttamente
            url = url_for('spesa.gestisci_documenti', spesa_id=1)
            print(f"URL generato: {url}")
        except Exception as e:
            print(f"Errore nella generazione URL per gestisci_documenti: {str(e)}")
            traceback.print_exc()

def check_database_structure():
    """Controlla la struttura del database"""
    print("\n=== Controllo struttura database ===")
    try:
        # Verifica la tabella spese
        print("Verifica della tabella spese:")
        spese = Spesa.query.limit(3).all()
        print(f"Numero di spese trovate: {len(spese)}")
        
        if spese:
            for spesa in spese:
                print(f"ID: {spesa.id}, Tipo: {spesa.tipo}, Class: {spesa.__class__.__name__}")
                
        # Controlla le tabelle specifiche
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        print("\nTabelle nel database:")
        for table in inspector.get_table_names():
            if table.startswith('spese_'):
                print(f"- {table}")
                columns = inspector.get_columns(table)
                for column in columns:
                    print(f"  - {column['name']} ({column['type']})")
    except Exception as e:
        print(f"Errore durante il controllo del database: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    with app.app_context():
        print("Inizio diagnostica dell'applicazione...")
        check_route_definition()
        check_route_handling()
        check_database_structure()
        print("\nDiagnostica completata.")
