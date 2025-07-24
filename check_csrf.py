import os
import sys
import requests
from bs4 import BeautifulSoup

# Aggiungi la directory corrente al path per importare i moduli
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

app = create_app()

def check_csrf_protection():
    with app.test_client() as client:
        # Verifica che la protezione CSRF sia attiva
        with app.app_context():
            print(f"SECRET_KEY configurata: {app.config['SECRET_KEY'][:10]}...")
            print(f"WTF_CSRF_ENABLED: {app.config.get('WTF_CSRF_ENABLED', True)}")
            print(f"WTF_CSRF_SECRET_KEY: {app.config.get('WTF_CSRF_SECRET_KEY', 'Non impostata')}")
        
        # Ottieni la pagina di login
        response = client.get('/auth/login')
        print(f"Stato risposta login: {response.status_code}")
        
        # Estrai il CSRF token dalla pagina
        soup = BeautifulSoup(response.data, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
            print(f"CSRF Token trovato: {csrf_token[:15]}... (lunghezza: {len(csrf_token)})")
        else:
            print("CSRF Token non trovato nella pagina di login!")
            return
        
        # Simula un login senza CSRF token (dovrebbe fallire)
        login_response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=False)
        print(f"Login senza CSRF token: stato {login_response.status_code}")
        
        # Simula un login con CSRF token
        login_response = client.post('/auth/login', data={
            'csrf_token': csrf_token,
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=False)
        print(f"Login con CSRF token: stato {login_response.status_code}")
        
        if login_response.status_code == 302:
            redirect_location = login_response.location
            print(f"Reindirizzamento a: {redirect_location}")
        else:
            print(f"Contenuto risposta: {login_response.data[:100]}...")

if __name__ == "__main__":
    print("Controllo della protezione CSRF nell'applicazione...")
    check_csrf_protection()
