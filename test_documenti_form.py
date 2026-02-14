#!/usr/bin/env python3
"""Test script per verificare il workflow di salvataggio documenti"""

from rimborsi import create_app, db
from rimborsi.models import Spesa, DocumentoSpesa, Richiesta
from rimborsi.richiesta.forms import DocumentiSpesaForm
import tempfile
import os
from werkzeug.datastructures import FileStorage

def test_form_creation():
    """Testa la creazione del form DocumentiSpesaForm"""
    app = create_app()
    
    with app.app_context():
        # Crea una spesa di test se non esiste
        richiesta = Richiesta.query.first()
        if not richiesta:
            print("❌ Nessuna richiesta trovata nel database")
            return False
            
        spesa = Spesa.query.filter_by(richiesta_id=richiesta.id).first()
        if not spesa:
            print("❌ Nessuna spesa trovata nel database")
            return False
            
        print(f"✅ Spesa trovata: ID {spesa.id}")
        
        # Testa creazione form
        try:
            form = DocumentiSpesaForm()
            print(f"✅ Form creato con {len(form.documenti.entries)} entries iniziali")
            
            # Aggiungi un entry
            form.documenti.append_entry()
            print(f"✅ Entry aggiunto, ora ci sono {len(form.documenti.entries)} entries")
            
            # Verifica i campi del primo entry
            first_entry = form.documenti.entries[0]
            print(f"✅ Primo entry ha campi: {[field.name for field in first_entry]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Errore creazione form: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_form_validation():
    """Testa la validazione del form con dati simulati"""
    app = create_app()
    
    with app.app_context():
        try:
            # Crea un file temporaneo per simulare l'upload
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(b"Test PDF content")
                temp_file_path = temp_file.name
            
            # Simula FormData
            with open(temp_file_path, 'rb') as f:
                file_storage = FileStorage(
                    stream=f,
                    filename="test_document.pdf",
                    content_type="application/pdf"
                )
                
                form_data = {
                    'documenti-0-tipo_documento': 'A',
                    'documenti-0-data_documento': '2024-01-15',
                    'documenti-0-fornitore': 'Test Fornitore',
                    'documenti-0-importo_documento': '25.50',
                    'documenti-0-remove': 'false',
                    'submit': 'Salva Documenti'
                }
                
                files_data = {
                    'documenti-0-allegato': file_storage
                }
                
                with app.test_request_context(method='POST', data=form_data, files=files_data):
                    form = DocumentiSpesaForm()
                    
                    if form.documenti.entries:
                        first_entry = form.documenti.entries[0]
                        print(f"✅ Primo entry popolato:")
                        print(f"   - tipo_documento: {first_entry.tipo_documento.data}")
                        print(f"   - data_documento: {first_entry.data_documento.data}")
                        print(f"   - fornitore: {first_entry.fornitore.data}")
                        print(f"   - importo_documento: {first_entry.importo_documento.data}")
                        print(f"   - allegato: {first_entry.allegato.data}")
                        print(f"   - remove: {first_entry.remove.data}")
                        
                        # Testa validazione
                        is_valid = form.validate()
                        print(f"✅ Form valido: {is_valid}")
                        
                        if not is_valid:
                            print(f"❌ Errori form: {form.errors}")
                            
                        return is_valid
                    else:
                        print("❌ Nessun entry nel form")
                        return False
            
            # Cleanup
            os.unlink(temp_file_path)
            
        except Exception as e:
            print(f"❌ Errore test validazione: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🧪 Test DocumentiSpesaForm")
    print("=" * 50)
    
    print("\n1. Test creazione form...")
    if test_form_creation():
        print("\n2. Test validazione form...")
        test_form_validation()
    else:
        print("❌ Test fallito alla creazione form")