"""
Script per aggiungere il ruolo di istruttore a un utente specifico
"""
from app import create_app, db
from app.models.user import User

def update_user_role(username, new_role):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if user:
            old_role = user.ruolo
            user.ruolo = new_role
            db.session.commit()
            print(f"Ruolo di {username} aggiornato da '{old_role}' a '{new_role}'")
        else:
            print(f"Utente {username} non trovato")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Utilizzo: python add_istruttore.py <username> <nuovo_ruolo>")
        print("Esempio: python add_istruttore.py admin istruttore")
        sys.exit(1)
    
    username = sys.argv[1]
    new_role = sys.argv[2]
    
    valid_roles = ['utente', 'amministratore', 'istruttore']
    if new_role not in valid_roles:
        print(f"Ruolo non valido. Deve essere uno dei seguenti: {', '.join(valid_roles)}")
        sys.exit(1)
    
    update_user_role(username, new_role)
