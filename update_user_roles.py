import os
import sys

# Aggiungi la directory corrente al path per importare i moduli
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.user import User

app = create_app()

def update_user_roles():
    with app.app_context():
        # Trova l'utente Pinna_v e impostalo come approvatore
        pinna = User.query.filter_by(username="Pinna_v").first()
        if pinna:
            pinna.ruolo = "approvatore"
            print(f"Utente {pinna.username} impostato come {pinna.ruolo}")
        else:
            print("Utente Pinna_v non trovato nel database!")
        
        # Trova l'utente Pivetti_d e impostalo come utente normale
        pivetti = User.query.filter_by(username="Pivetti_d").first()
        if pivetti:
            pivetti.ruolo = "utente"
            print(f"Utente {pivetti.username} impostato come {pivetti.ruolo}")
        else:
            print("Utente Pivetti_d non trovato nel database!")
        
        # Salva le modifiche nel database
        if pinna or pivetti:
            db.session.commit()
            print("Modifiche salvate nel database!")
        else:
            print("Nessuna modifica da salvare.")
        
        # Verifica tutti gli utenti e i loro ruoli
        print("\nElenco di tutti gli utenti nel database:")
        users = User.query.all()
        for user in users:
            print(f"- {user.username}: {user.ruolo}")

if __name__ == "__main__":
    update_user_roles()
