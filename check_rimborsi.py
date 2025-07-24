from app import create_app, db
from app.models.rimborso import Rimborso

app = create_app()

with app.app_context():
    rimborsi = Rimborso.query.all()
    print(f"Numero totale di rimborsi: {len(rimborsi)}")
    
    # Conteggio per stato
    stati = {}
    for r in rimborsi:
        if r.stato in stati:
            stati[r.stato] += 1
        else:
            stati[r.stato] = 1
    
    print("\nConteggio per stato:")
    for stato, count in stati.items():
        print(f"{stato}: {count}")
    
    # Conteggio per utente
    utenti = {}
    for r in rimborsi:
        if r.user_id in utenti:
            utenti[r.user_id] += 1
        else:
            utenti[r.user_id] = 1
    
    print("\nConteggio per utente:")
    for user_id, count in utenti.items():
        print(f"Utente ID {user_id}: {count} rimborsi")
