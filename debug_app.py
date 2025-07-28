"""
Script per testare e identificare errori nell'applicazione Flask
"""
import os
import logging
from flask import url_for
from app import create_app

# Configura logging avanzato
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug_app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_routes():
    """Testa le rotte principali dell'applicazione"""
    app = create_app()
    with app.test_client() as client:
        with app.app_context():
            try:
                # Test della home
                logger.info("Testando la home page...")
                response = client.get('/')
                logger.info(f"Home page: status={response.status_code}")
                
                # Test della pagina di login
                logger.info("Testando la pagina di login...")
                response = client.get('/auth/login')
                logger.info(f"Login page: status={response.status_code}")
                
                # Test della lista richieste
                logger.info("Testando la lista richieste...")
                response = client.get('/richieste/lista')
                logger.info(f"Lista richieste: status={response.status_code}")
                
                # Test delle spese
                logger.info("Testando la gestione spese...")
                try:
                    # Questo test potrebbe fallire se non ci sono richieste nel DB
                    response = client.get('/spese/richieste/1/gestione')
                    logger.info(f"Gestione spese: status={response.status_code}")
                except Exception as e:
                    logger.error(f"Errore nella gestione spese: {str(e)}")
                
                # Testa il percorso documenti_spesa
                logger.info("Testando il percorso documenti_spesa...")
                try:
                    response = client.get('/spese/documenti/1')
                    logger.info(f"Documenti spesa: status={response.status_code}")
                except Exception as e:
                    logger.error(f"Errore nei documenti spesa: {str(e)}")
                
                # Testa il percorso gestisci-documenti (alias)
                logger.info("Testando il percorso gestisci-documenti...")
                try:
                    response = client.get('/spese/gestisci-documenti/1')
                    logger.info(f"Gestisci documenti: status={response.status_code}")
                except Exception as e:
                    logger.error(f"Errore nei gestisci documenti: {str(e)}")
                
            except Exception as e:
                logger.error(f"Errore durante il test delle rotte: {str(e)}")

if __name__ == "__main__":
    logger.info("Avvio del test dell'applicazione...")
    test_routes()
    logger.info("Test completato. Controlla il file debug_app.log per i dettagli.")
