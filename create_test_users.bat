@echo off
echo ========================================
echo Script per creare utenti di test
echo ========================================
echo.

cd /d "C:\DEV_FLASK\rimborsi"

echo Attivazione ambiente virtuale...
call "venv\Scripts\activate.bat"

echo.
echo Creazione utenti di test...
python -c "
from rimborsi import create_app, db
from rimborsi.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print('Inizio creazione utenti...')
    
    # Lista utenti da creare
    users_data = [
        ('mariorossi', 'mariorossi@test.com', '12345'),
        ('mariobianchi', 'mariobianchi@test.com', '12345'), 
        ('ritaneri', 'ritaneri@test.com', '12345')
    ]
    
    created = 0
    for username, email, password in users_data:
        existing = User.query.filter_by(email=email).first()
        if not existing:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role='compilatore'
            )
            db.session.add(user)
            print(f'Creato: {email}')
            created += 1
        else:
            print(f'Esistente: {email}')
    
    if created > 0:
        db.session.commit()
        print(f'Salvati {created} nuovi utenti.')
    
    # Mostra tutti i compilatori
    compilatori = User.query.filter_by(role='compilatore').all()
    print(f'Totale compilatori: {len(compilatori)}')
    for user in compilatori:
        org_count = len(user.organizzazioni) if user.organizzazioni else 0
        status = 'senza org.' if org_count == 0 else f'{org_count} org.'
        print(f'  - {user.email} ({status})')
"

echo.
echo ========================================
echo Script completato!
echo ========================================
pause
