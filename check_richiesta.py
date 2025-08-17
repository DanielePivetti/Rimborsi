from app import db, create_app
from app.models.richiesta import Richiesta

app = create_app()
with app.app_context():
    richiesta = Richiesta.query.get(2)
    if richiesta:
        print(f"La richiesta con ID 2 esiste ancora: {richiesta.id}")
    else:
        print("La richiesta con ID 2 è stata eliminata con successo.")
    
    # Elenco delle richieste ancora presenti
    richieste = Richiesta.query.all()
    print(f"\nRichieste ancora presenti nel database ({len(richieste)}):")
    for r in richieste:
        print(f"ID: {r.id}, ODV: {r.odv.nome}, Stato: {r.stato.name}")
