from rimborsi import create_app
from rimborsi.models import db, Richiesta, Organizzazione
from datetime import datetime

app = create_app()  # Assicurati che questa funzione esista nel tuo progetto

with app.app_context():
    for richiesta in Richiesta.query.all():
        if not richiesta.codice_uni:
            org = db.session.get(Organizzazione, richiesta.organizzazione_id)
            if org and org.codice_interno:
                datastamp = richiesta.data_creazione.strftime('%Y%m%d%H%M%S') if richiesta.data_creazione else datetime.utcnow().strftime('%Y%m%d%H%M%S')
                richiesta.codice_uni = f"{org.codice_interno}{datastamp}"
            else:
                datastamp = richiesta.data_creazione.strftime('%Y%m%d%H%M%S') if richiesta.data_creazione else datetime.utcnow().strftime('%Y%m%d%H%M%S')
                richiesta.codice_uni = f"ORG{datastamp}"
    db.session.commit()