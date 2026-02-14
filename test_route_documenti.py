#!/usr/bin/env python3
"""Test script semplice per verificare l'accesso alla route documenti"""

from rimborsi import create_app, db
from rimborsi.models import Spesa, Richiesta

def test_route_access():
    """Testa l'accesso alla route aggiungi_documenti_spesa"""
    app = create_app()
    
    with app.test_client() as client:
        # Trova una spesa esistente
        with app.app_context():
            spesa = Spesa.query.first()
            if not spesa:
                print("❌ Nessuna spesa trovata nel database")
                return False
            
            print(f"✅ Spesa trovata: ID {spesa.id}")
        
        # Testa accesso GET alla route documenti
        url = f'/richiesta/spese/{spesa.id}/documenti/aggiungi'
        print(f"🔍 Testing GET {url}")
        
        response = client.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 302:
            print("↩️  Redirect (probabilmente per autenticazione)")
            print(f"Location: {response.headers.get('Location', 'N/A')}")
        elif response.status_code == 200:
            print("✅ Pagina caricata correttamente")
            
            # Verifica che il template contenga gli elementi aspettati
            html = response.get_data(as_text=True)
            if 'documenti' in html.lower():
                print("✅ Template contiene riferimenti a documenti")
            if 'form' in html.lower():
                print("✅ Template contiene form")
                
        elif response.status_code == 404:
            print("❌ Route non trovata (404)")
        elif response.status_code == 500:
            print("❌ Errore interno server (500)")
        else:
            print(f"⚠️  Status code inaspettato: {response.status_code}")
            
        return response.status_code

if __name__ == "__main__":
    print("🧪 Test accesso route documenti")
    print("=" * 40)
    test_route_access()