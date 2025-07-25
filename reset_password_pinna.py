from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

# Password che vuoi impostare
password = 'Pinna_v123'

with app.app_context():
    user = User.query.filter_by(username='Pinna_v').first()
    if user:
        user.password_hash = generate_password_hash(password)
        db.session.commit()
        print(f'Password aggiornata per l\'utente {user.username}')
        print(f'Credenziali: Username = {user.username}, Password = {password}')
        print(f'Ruolo: {user.ruolo}')
    else:
        print('Utente Pinna_v non trovato')
