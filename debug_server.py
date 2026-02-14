#!/usr/bin/env python3
"""Test debugging form validation issues"""

from rimborsi import create_app, db
import os
import tempfile

def start_test_server():
    """Avvia il server Flask per test manuali"""
    app = create_app()
    
    # Abilita debug per vedere tutti i log
    app.config['DEBUG'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disabilita CSRF per semplificare test
    
    print("🚀 Avviando server Flask in modalità debug...")
    print("📍 Vai su: http://localhost:5000")
    print("📍 Test URL: http://localhost:5000/richiesta/spese/1/documenti/aggiungi")
    print("⚠️  CSRF disabilitato per test - ricorda di riabilitarlo in produzione")
    
    # Crea directory upload se non esiste
    upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        print(f"📁 Creata directory upload: {upload_dir}")
    
    app.run(debug=True, port=5000)

if __name__ == "__main__":
    start_test_server()