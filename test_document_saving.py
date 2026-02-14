#!/usr/bin/env python3
"""Test per verificare il salvataggio documenti nel database"""

from rimborsi import create_app, db
from rimborsi.models import Spesa, User, DocumentoSpesa
import tempfile
import os

def test_document_saving():
    """Test che verifica il salvataggio effettivo dei documenti nel database"""
    app = create_app()
    
    with app.app_context():
        # Disabilita CSRF per semplificare test
        app.config['WTF_CSRF_ENABLED'] = False
        
        # Trova spesa per test
        spesa = Spesa.query.first()
        user = User.query.first()
        
        if not spesa or not user:
            print("❌ Dati mancanti nel database")
            return False
        
        # Conta documenti esistenti per questa spesa
        docs_before = DocumentoSpesa.query.filter_by(spesa_id=spesa.id).count()
        print(f"📊 Documenti prima del test: {docs_before}")
        
        # Test completo con client
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id) 
                sess['_fresh'] = True
            
            # Crea file temporaneo
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(b"Test PDF document for validation")
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    response = client.post(
                        f'/richiesta/spese/{spesa.id}/documenti/aggiungi',
                        data={
                            'documenti-0-tipo_documento': 'A',
                            'documenti-0-data_documento': '2024-01-15',
                            'documenti-0-fornitore': 'Test Fornitore SRL',
                            'documenti-0-importo_documento': '25.50',
                            'documenti-0-remove': 'false',
                            'documenti-0-allegato': (f, 'test_validation.pdf'),
                            'submit': 'Salva Documenti'
                        },
                        content_type='multipart/form-data',
                        follow_redirects=True
                    )
                
                print(f"🌐 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    # Controlla se ci sono stati errori
                    html = response.get_data(as_text=True)
                    if 'Errori di validazione:' in html:
                        # Estrai il messaggio di errore
                        import re
                        error_match = re.search(r'Errori di validazione: (.*?)</div>', html, re.DOTALL)
                        if error_match:
                            error_msg = error_match.group(1).strip()
                            print(f"❌ Errore validazione: {error_msg}")
                        return False
                    elif 'Aggiunti' in html and 'documenti' in html:
                        print("✅ Messaggio di successo trovato!")
                
                # Verifica salvataggio nel database
                docs_after = DocumentoSpesa.query.filter_by(spesa_id=spesa.id).count()
                print(f"📊 Documenti dopo il test: {docs_after}")
                
                if docs_after > docs_before:
                    print(f"✅ Documento salvato nel database! (+{docs_after - docs_before})")
                    
                    # Mostra dettagli ultimo documento
                    last_doc = DocumentoSpesa.query.filter_by(spesa_id=spesa.id).order_by(DocumentoSpesa.id.desc()).first()
                    if last_doc:
                        print(f"📄 Ultimo documento:")
                        print(f"   - Tipo: {last_doc.tipo_documento}")
                        print(f"   - Fornitore: {last_doc.fornitore}")
                        print(f"   - Importo: €{last_doc.importo_documento}")
                        print(f"   - File: {last_doc.nome_file}")
                    
                    return True
                else:
                    print("❌ Documento non salvato nel database")
                    return False
                    
            finally:
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

if __name__ == "__main__":
    print("🧪 Test salvataggio documenti nel database")
    print("=" * 50)
    test_document_saving()