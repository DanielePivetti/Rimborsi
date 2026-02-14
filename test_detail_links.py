#!/usr/bin/env python3
"""Test per verificare i puntamenti dei link nel dettaglio richiesta"""

from rimborsi import create_app, db
from rimborsi.models import Spesa, User, Richiesta
import re

def test_detail_links():
    """Testa che tutti i link nel dettaglio richiesta puntino correttamente"""
    app = create_app()
    
    with app.app_context():
        app.config['WTF_CSRF_ENABLED'] = False
        
        user = User.query.first()
        richiesta = Richiesta.query.first()
        
        if not user or not richiesta:
            print("❌ Dati mancanti nel database")
            return False
        
        print(f"✅ Testing con Richiesta ID: {richiesta.id}")
        
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            # Testa accesso al dettaglio richiesta
            response = client.get(f'/richiesta/dettaglio/{richiesta.id}')
            
            if response.status_code != 200:
                print(f"❌ Impossibile accedere al dettaglio richiesta: {response.status_code}")
                return False
            
            html = response.get_data(as_text=True)
            print("✅ Dettaglio richiesta caricato")
            
            # Cerca i link per documenti
            doc_links = re.findall(r'href="([^"]*documenti[^"]*)"', html)
            print(f"🔗 Link documenti trovati: {len(doc_links)}")
            for link in doc_links:
                print(f"   - {link}")
            
            # Cerca i link per modifica spesa
            edit_links = re.findall(r'href="([^"]*spese/[^/]*/modifica[^"]*)"', html)
            print(f"🔗 Link modifica spesa trovati: {len(edit_links)}")
            for link in edit_links:
                print(f"   - {link}")
            
            # Testa accesso a una modifica spesa se esiste
            if richiesta.spese:
                spesa = richiesta.spese[0]
                mod_url = f'/richiesta/{richiesta.id}/spese/{spesa.id}/modifica'
                print(f"🧪 Testing modifica spesa: {mod_url}")
                
                response = client.get(mod_url)
                if response.status_code == 200:
                    print("✅ Pagina modifica spesa accessibile")
                    
                    # Verifica che il template contenga link per documenti
                    html = response.get_data(as_text=True)
                    if spesa.documenti:
                        if 'Gestisci Documenti' in html:
                            print("✅ Link 'Gestisci Documenti' presente nella modifica")
                        else:
                            print("⚠️  Link 'Gestisci Documenti' mancante")
                    else:
                        if 'Aggiungi Documenti' in html:
                            print("✅ Link 'Aggiungi Documenti' presente nella modifica")
                        else:
                            print("⚠️  Link 'Aggiungi Documenti' mancante")
                else:
                    print(f"❌ Errore accesso modifica spesa: {response.status_code}")
            
            return True

if __name__ == "__main__":
    print("🧪 Test puntamenti link nel dettaglio richiesta")
    print("=" * 55)
    test_detail_links()