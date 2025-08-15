"""
Script per resettare la password di utenti specifici.
"""
from werkzeug.security import generate_password_hash
from rimborsi import create_app, db
from rimborsi.models import User

def reset_password(email, new_password):
    """Resetta la password per l'utente con l'email specificata."""
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"Utente con email {email} non trovato.")
            return False
        
        # Genera l'hash della nuova password
        hashed_password = generate_password_hash(new_password)
        
        # Aggiorna la password
        user.password_hash = hashed_password
        
        # Salva le modifiche
        db.session.commit()
        
        print(f"Password resettata con successo per l'utente {user.username} ({email}).")
        return True

def reset_multiple_passwords(users_data):
    """Resetta le password per più utenti."""
    app = create_app()
    
    with app.app_context():
        for email, password in users_data:
            reset_password(email, password)

if __name__ == "__main__":
    # Lista di (email, nuova_password) per gli utenti da aggiornare
    users_to_update = [
        ("istruttore@test.com", "12345"),
        ("admin@test.com", "12345"),
        ("compilatore@test.com", "12345")

    ]
    
    # Resetta le password per tutti gli utenti specificati
    reset_multiple_passwords(users_to_update)
