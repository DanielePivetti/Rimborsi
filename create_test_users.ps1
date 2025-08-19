# Script PowerShell per creare utenti di test
# Esegui questo file con: .\create_test_users.ps1

Write-Host "===========================================" -ForegroundColor Green
Write-Host "Script per creare utenti di test - Rimborsi" -ForegroundColor Green  
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""

# Cambia nella directory del progetto
Set-Location "C:\DEV_FLASK\rimborsi"

Write-Host "Esecuzione script Python..." -ForegroundColor Yellow

# Esegui il comando Python
& "C:\DEV_FLASK\rimborsi\venv\Scripts\python.exe" -c @"
from rimborsi import create_app, db
from rimborsi.models import User
from werkzeug.security import generate_password_hash

print('🚀 Avvio creazione utenti di test...')
print('-' * 45)

app = create_app()

with app.app_context():
    # Dati utenti da creare
    users_data = [
        {'username': 'mariorossi', 'email': 'mariorossi@test.com', 'password': '12345'},
        {'username': 'mariobianchi', 'email': 'mariobianchi@test.com', 'password': '12345'},
        {'username': 'ritaneri', 'email': 'ritaneri@test.com', 'password': '12345'}
    ]
    
    created_count = 0
    existing_count = 0
    
    for user_data in users_data:
        # Controlla se esiste già
        existing = User.query.filter_by(email=user_data['email']).first()
        
        if existing:
            print(f'⚠️  {user_data['email']} - GIÀ ESISTENTE')
            existing_count += 1
        else:
            # Crea nuovo utente
            new_user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                role='compilatore'
            )
            db.session.add(new_user)
            print(f'✅ {user_data['email']} - CREATO')
            created_count += 1
    
    # Salva nel database
    if created_count > 0:
        try:
            db.session.commit()
            print(f'\n💾 Salvati {created_count} nuovi utenti nel database')
        except Exception as e:
            db.session.rollback()
            print(f'\n❌ Errore nel salvataggio: {e}')
            exit(1)
    
    print('-' * 45)
    print(f'📊 RIEPILOGO:')
    print(f'   • Nuovi utenti creati: {created_count}')
    print(f'   • Utenti già esistenti: {existing_count}')
    
    # Mostra tutti i compilatori
    print('\n👥 COMPILATORI NEL DATABASE:')
    compilatori = User.query.filter_by(role='compilatore').all()
    
    if not compilatori:
        print('   Nessun compilatore trovato')
    else:
        for user in compilatori:
            org_count = len(user.organizzazioni) if user.organizzazioni else 0
            status = '🔗 Associato' if org_count > 0 else '⭕ Da associare'
            print(f'   • {user.email} - {status}')
    
    print(f'\n🎯 Totale compilatori: {len(compilatori)}')
    da_associare = [u for u in compilatori if len(u.organizzazioni) == 0]
    print(f'🔄 Da associare: {len(da_associare)}')

print('\n✨ Script completato!')
"@

Write-Host ""
Write-Host "===========================================" -ForegroundColor Green
Write-Host "Script terminato!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
