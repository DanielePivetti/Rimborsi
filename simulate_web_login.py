import os
import sys
import requests
from bs4 import BeautifulSoup

# Porta su cui gira l'applicazione Flask
PORT = 5000
BASE_URL = f"http://localhost:{PORT}"

def get_csrf_token(session, url):
    """Ottieni il token CSRF dalla pagina."""
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Cerca il campo nascosto con il token CSRF
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        return csrf_input.get('value')
    return None

def simulate_login(username, password):
    """Simula un login all'applicazione web."""
    print(f"Tentativo di login con: {username} / {password}")
    
    # Crea una sessione per mantenere i cookie
    session = requests.Session()
    
    # Ottieni il token CSRF dalla pagina di login
    login_url = f"{BASE_URL}/auth/login"
    csrf_token = get_csrf_token(session, login_url)
    
    if not csrf_token:
        print("Errore: Impossibile ottenere il token CSRF")
        return False
    
    # Prepara i dati del form di login
    login_data = {
        'csrf_token': csrf_token,
        'username': username,
        'password': password,
        'remember_me': 'y',  # Checkbox spuntata
        'submit': 'Accedi'
    }
    
    # Esegui il login
    login_response = session.post(login_url, data=login_data, allow_redirects=False)
    
    # Verifica il codice di stato della risposta
    print(f"Codice di stato: {login_response.status_code}")
    
    # Se il login ha successo, dovresti essere reindirizzato (codice 302)
    if login_response.status_code == 302:
        redirect_url = login_response.headers.get('Location', '')
        print(f"Reindirizzamento a: {redirect_url}")
        
        # Verifica se sei stato reindirizzato alla dashboard (successo) o di nuovo al login (fallimento)
        if 'dashboard' in redirect_url:
            print("Login riuscito! Reindirizzato alla dashboard.")
            
            # Facciamo una richiesta alla dashboard per confermare
            dashboard_response = session.get(BASE_URL + redirect_url)
            if 'Benvenuto' in dashboard_response.text:
                print("Confermato: sei nella dashboard")
            return True
        else:
            print("Login fallito: reindirizzato a un'altra pagina.")
            return False
    else:
        print("Login fallito: nessun reindirizzamento.")
        return False

if __name__ == "__main__":
    print("Simulazione di login all'applicazione...")
    
    # Prova a fare login con le credenziali degli utenti
    simulate_login("admin", "admin123")
    simulate_login("istruttore", "istruttore123")
    simulate_login("mario", "mario123")
    simulate_login("giulia", "giulia123")
    
    # Prova con credenziali errate
    simulate_login("admin", "password_sbagliata")
