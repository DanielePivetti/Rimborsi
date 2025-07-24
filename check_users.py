from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print("Utenti nel database:")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Ruolo: {user.ruolo}")
