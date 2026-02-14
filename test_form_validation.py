#!/usr/bin/env python3
"""Test dettagliato per debugging validazione form"""

from rimborsi import create_app, db
from rimborsi.models import Spesa, User
from rimborsi.richiesta.forms import DocumentiSpesaForm
import tempfile
import os
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

def test_form_validation_detailed():
    """Test dettagliato della validazione form"""
    app = create_app()
    
    with app.app_context():
        # Disabilita CSRF per semplificare test  
        app.config['WTF_CSRF_ENABLED'] = False
        
        spesa = Spesa.query.first()
        user = User.query.first()
        
        if not spesa or not user:
            print("❌ Dati mancanti nel database")
            return False
        
        print(f"✅ Testing con Spesa ID: {spesa.id}, User: {user.username}")
        
        # Crea file temporaneo per test
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b"Test PDF content")
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                # Usa test client per simulare correttamente upload file
                with app.test_client() as client:
                    with client.session_transaction() as sess:
                        sess['_user_id'] = str(user.id)
                        sess['_fresh'] = True
                    
                    # Test POST con file upload
                    response = client.post(
                        f'/richiesta/spese/{spesa.id}/documenti/aggiungi',
                        data={
                            'documenti-0-tipo_documento': 'A',
                            'documenti-0-data_documento': '2024-01-15',
                            'documenti-0-fornitore': 'Test Fornitore SRL', 
                            'documenti-0-importo_documento': '25.50',
                            'documenti-0-remove': '',
                            'documenti-0-allegato': (f, 'test_doc.pdf'),
                            'submit': 'Salva Documenti'
                        },
                        content_type='multipart/form-data'
                    )
                    
                    print(f"🌐 Response status: {response.status_code}")
                    
                    if response.status_code == 302:
                        print("✅ Redirect - probabilmente successo!")
                        return True
                    else:
                        # Se non redirect, analizza contenuto risposta
                        html = response.get_data(as_text=True)
                        
                        # Cerca messaggi flash nella risposta
                        import re
                        flash_pattern = r'alert-(\w+).*?>(.*?)</div>'
                        flash_matches = re.findall(flash_pattern, html, re.DOTALL)
                        
                        if flash_matches:
                            for alert_type, message in flash_matches:
                                print(f"🚨 Flash {alert_type}: {message.strip()}")
                        
                        if 'Errori di validazione:' in html:
                            print("❌ Errori di validazione trovati nel HTML")
                        elif 'Correggi gli errori' in html:
                            print("⚠️  Form ha errori ma dettagli non mostrati")
                        
                        # Cerca errori specifici nei campi del form
                        if 'is-invalid' in html:
                            print("⚠️  Campi con errori trovati nel HTML")
                            
                        return False
        
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass

if __name__ == "__main__":
    print("🧪 Test dettagliato validazione DocumentiSpesaForm")
    print("=" * 60)
    test_form_validation_detailed()