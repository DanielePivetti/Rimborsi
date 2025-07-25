from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(username='Pinna_v').first()
    if user:
        print(f'Username: {user.username}, Nome: {user.nome} {user.cognome}, Ruolo: {user.ruolo}')
    else:
        print('Utente Pinna_v non trovato')
