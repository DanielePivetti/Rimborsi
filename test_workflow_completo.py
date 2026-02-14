#!/usr/bin/env python3
"""Test completo workflow documenti con simulazione login"""

from rimborsi import create_app, db
from rimborsi.models import Spesa, Richiesta, User, DocumentoSpesa
import tempfile
import os
from datetime import date

def test_complete_workflow():
    """Test completo del workflow di salvataggio documenti"""
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            # Trova utente e spesa per test
            user = User.query.first()
            spesa = Spesa.query.first()
            
            if not user or not spesa:
                print("❌ Dati mancanti: user o spesa")
                return False
                
            print(f"✅ User: {user.username}, Spesa ID: {spesa.id}")
            
            # Step 1: Simula login (semplificato)
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            # Step 2: Accedi alla pagina documenti
            response = client.get(f'/richiesta/spese/{spesa.id}/documenti/aggiungi')
            print(f"GET Status: {response.status_code}")
            
            if response.status_code != 200:
                print("❌ Impossibile accedere alla pagina documenti")
                return False
                
            # Step 3: Simula upload documento
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(b"Test PDF document content")
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    # Dati form per il documento
                    data = {
                        'documenti-0-tipo_documento': 'A',
                        'documenti-0-data_documento': '2024-01-15', 
                        'documenti-0-fornitore': 'Test Fornitore SRL',
                        'documenti-0-importo_documento': '25.50',
                        'documenti-0-remove': '',
                        'submit': 'Salva Documenti',
                        'csrf_token': 'dummy_token'  # Potrebbe essere necessario
                    }
                    
                    files = {
                        'documenti-0-allegato': (f, 'test_document.pdf', 'application/pdf')
                    }
                    
                    # Submit form
                    response = client.post(
                        f'/richiesta/spese/{spesa.id}/documenti/aggiungi',
                        data={
                            **data,
                            'documenti-0-allegato': (f, 'test_document.pdf')
                        },
                        content_type='multipart/form-data',
                        follow_redirects=True
                    )
                    
                    print(f"POST Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        # Verifica se documento è stato salvato
                        documenti_count = DocumentoSpesa.query.filter_by(spesa_id=spesa.id).count()
                        print(f"✅ Documenti nel DB per spesa {spesa.id}: {documenti_count}")
                        
                        # Mostra messaggi flash se presenti
                        html = response.get_data(as_text=True)
                        if 'success' in html.lower():
                            print("✅ Messaggio di successo trovato")
                        if 'errore' in html.lower():
                            print("⚠️  Messaggio di errore trovato")
                            
                        return True
                    else:
                        print(f"❌ POST fallito con status {response.status_code}")
                        return False
                        
            finally:
                # Cleanup
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
            return False

if __name__ == "__main__":
    print("🧪 Test completo workflow documenti")
    print("=" * 50)
    test_complete_workflow()