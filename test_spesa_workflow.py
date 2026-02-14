#!/usr/bin/env python3
"""
Test script per verificare la funzionalità del nuovo workflow spesa+documenti
"""
import sys
import os

# Aggiungi il percorso principale al Python path
sys.path.insert(0, os.path.abspath('.'))

def test_forms_import():
    """Test che i form si possano importare senza errori"""
    try:
        from rimborsi.richiesta.forms import SpesaForm, DocumentoSpesaInlineForm
        print("✅ Import dei forms riuscito!")
        return True
    except Exception as e:
        print(f"❌ Errore import forms: {e}")
        return False

def test_form_creation():
    """Test che il form si possa creare (test semplificato)"""
    try:
        from rimborsi.richiesta.forms import SpesaForm, DocumentoSpesaInlineForm
        
        print("✅ Classi form importate correttamente!")
        
        # Test che le classi abbiano gli attributi necessari
        assert hasattr(SpesaForm, 'categoria')
        assert hasattr(SpesaForm, 'documenti') 
        assert hasattr(SpesaForm, 'importo_richiesto')
        print("✅ Attributi SpesaForm verificati!")
        
        assert hasattr(DocumentoSpesaInlineForm, 'tipo_documento')
        assert hasattr(DocumentoSpesaInlineForm, 'allegato')
        assert hasattr(DocumentoSpesaInlineForm, 'remove')
        print("✅ Attributi DocumentoSpesaInlineForm verificati!")
        
        # Verifica che la classe DocumentoSpesaInlineForm sia definita prima di SpesaForm nel codice
        import inspect
        import rimborsi.richiesta.forms as forms_module
        source_lines = inspect.getsourcelines(forms_module)[0]
        
        inline_form_line = None
        spesa_form_line = None
        
        for i, line in enumerate(source_lines):
            if 'class DocumentoSpesaInlineForm' in line:
                inline_form_line = i
            elif 'class SpesaForm' in line:
                spesa_form_line = i
        
        if inline_form_line is not None and spesa_form_line is not None:
            assert inline_form_line < spesa_form_line, "DocumentoSpesaInlineForm deve essere definita prima di SpesaForm"
            print("✅ Ordine delle classi verificato!")
        
        return True
    except Exception as e:
        print(f"❌ Errore creazione form: {e}")
        return False

def test_config():
    """Test che la configurazione sia corretta"""
    try:
        from config import Config
        
        assert hasattr(Config, 'UPLOAD_FOLDER')
        assert hasattr(Config, 'MAX_CONTENT_LENGTH')
        print("✅ Configurazione verificata!")
        return True
    except Exception as e:
        print(f"❌ Errore configurazione: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Test del nuovo workflow spesa+documenti\n")
    
    tests = [
        test_config,
        test_forms_import,
        test_form_creation,
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Risultati: {passed}/{len(tests)} test passati")
    
    if passed == len(tests):
        print("🎉 Tutti i test sono passati! L'implementazione di base funziona.")
    else:
        print("⚠️ Alcuni test non sono passati. Verifica gli errori sopra.")