#!/usr/bin/env python3
"""Test end-to-end del workflow spese aggiornato"""

from rimborsi import create_app, db
from rimborsi.models import Spesa, User, Richiesta, DocumentoSpesa
import tempfile
import os

def test_complete_workflow():
    """Test completo: crea spesa -> aggiungi documenti -> modifica spesa -> gestisci documenti"""
    app = create_app()
    
    with app.app_context():
        app.config['WTF_CSRF_ENABLED'] = False
        
        user = User.query.first()
        richiesta = Richiesta.query.first()
        
        if not user or not richiesta:
            print("❌ Dati mancanti nel database")
            return False
        
        print(f"🎯 Test workflow completo con Richiesta ID: {richiesta.id}")
        
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            # Step 1: Crea spesa base
            print("\n📝 Step 1: Crea spesa base")
            response = client.post(
                f'/richiesta/{richiesta.id}/spese/crea',
                data={
                    'categoria': '01',  # Carburante - richiede impiego
                    'data_spesa': '2024-01-15',
                    'descrizione_spesa': 'Test carburante workflow',
                    'importo_richiesto': '75.00',
                    'impiego': '1',  # ID dell'impiego disponibile
                    'submit': 'Salva Spesa e Aggiungi Documenti'
                },
                follow_redirects=False
            )
            
            if response.status_code == 302:
                print("✅ Spesa creata, redirect al step documenti")
                redirect_url = response.headers.get('Location', '')
                print(f"🔗 Redirect URL: {redirect_url}")
                if 'documenti/aggiungi' in redirect_url:
                    print("✅ Redirect corretto verso aggiunta documenti")
                    # Estrai l'ID della spesa dall'URL
                    import re
                    match = re.search(r'/spese/(\d+)/documenti', redirect_url)
                    if match:
                        spesa_id = match.group(1)
                        print(f"📋 Spesa ID estratto: {spesa_id}")
                    else:
                        print("❌ Impossibile estrarre ID spesa")
                        return False
                else:
                    print("❌ Redirect non verso documenti")
                    return False
            else:
                print(f"❌ Creazione spesa fallita: {response.status_code}")
                return False
            
            # Step 2: Aggiungi documenti 
            print("\n📎 Step 2: Aggiungi documenti")
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(b"Test workflow PDF content")
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    response = client.post(
                        f'/richiesta/spese/{spesa_id}/documenti/aggiungi',
                        data={
                            'documenti-0-tipo_documento': 'A',
                            'documenti-0-data_documento': '2024-01-15',
                            'documenti-0-fornitore': 'Distributore Test',
                            'documenti-0-importo_documento': '75.00',
                            'documenti-0-remove': 'false',
                            'documenti-0-allegato': (f, 'test_workflow.pdf'),
                            'submit': 'Salva Documenti'
                        },
                        content_type='multipart/form-data',
                        follow_redirects=True
                    )
                
                if response.status_code == 200:
                    html = response.get_data(as_text=True)
                    if 'Aggiunti' in html and 'documenti' in html:
                        print("✅ Documenti aggiunti con successo")
                    else:
                        print("❌ Problemi nell'aggiunta documenti")
                        return False
                else:
                    print(f"❌ Aggiunta documenti fallita: {response.status_code}")
                    return False
            finally:
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            
            # Step 3: Testa modifica spesa
            print(f"\n✏️  Step 3: Modifica spesa {spesa_id}")
            response = client.get(f'/richiesta/{richiesta.id}/spese/{spesa_id}/modifica')
            
            if response.status_code == 200:
                print("✅ Pagina modifica accessibile")
                html = response.get_data(as_text=True)
                if 'Gestisci Documenti' in html:
                    print("✅ Link gestione documenti presente in modifica")
                else:
                    print("⚠️  Link gestione documenti non trovato")
            else:
                print(f"❌ Accesso modifica fallito: {response.status_code}")
                return False
            
            # Step 4: Testa lista documenti
            print(f"\n📋 Step 4: Lista documenti per spesa {spesa_id}")
            response = client.get(f'/richiesta/spese/{spesa_id}/documenti')
            
            if response.status_code == 200:
                print("✅ Lista documenti accessibile")
                html = response.get_data(as_text=True)
                if 'test_workflow.pdf' in html or 'Distributore Test' in html:
                    print("✅ Documento presente nella lista")
                else:
                    print("⚠️  Documento non visibile nella lista")
            else:
                print(f"❌ Lista documenti non accessibile: {response.status_code}")
            
            # Step 5: Verifica nel dettaglio richiesta
            print(f"\n📊 Step 5: Verifica dettaglio richiesta")
            response = client.get(f'/richiesta/dettaglio/{richiesta.id}')
            
            if response.status_code == 200:
                html = response.get_data(as_text=True)
                if 'Test carburante workflow' in html:
                    print("✅ Spesa visibile nel dettaglio richiesta")
                    if f'({1})' in html:  # Conta documenti
                        print("✅ Contatore documenti corretto nel dettaglio")
                    else:
                        print("⚠️  Contatore documenti non trovato")
                else:
                    print("⚠️  Spesa non trovata nel dettaglio")
            else:
                print(f"❌ Dettaglio richiesta non accessibile: {response.status_code}")
            
            print("\n🎉 Test workflow completato!")
            return True

if __name__ == "__main__":
    print("🧪 Test End-to-End Workflow Spese")
    print("=" * 60)
    test_complete_workflow()