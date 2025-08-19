"""
Script per testare un compilatore senza organizzazioni
Crea un utente compilatore di test che non ha organizzazioni associate
"""
from rimborsi import create_app, db
from rimborsi.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("🧪 Creazione utente compilatore di test SENZA organizzazioni...")
    
    test_email = 'test.senza.org@test.com'
    
    # Controlla se esiste già
    existing_user = User.query.filter_by(email=test_email).first()
    if existing_user:
        print(f"⚠️ Utente {test_email} già esistente")
        # Rimuovi le organizzazioni se ne ha
        existing_user.organizzazioni = []
        db.session.commit()
        print("✅ Rimosso dalle organizzazioni per il test")
    else:
        # Crea nuovo utente
        test_user = User(
            username='testsenzaorg',
            email=test_email,
            password_hash=generate_password_hash('12345'),
            role='compilatore'
        )
        db.session.add(test_user)
        db.session.commit()
        print(f"✅ Creato nuovo utente: {test_email}")
    
    print(f"\n🎯 Test pronto!")
    print(f"Email: {test_email}")
    print(f"Password: 12345") 
    print(f"Ruolo: compilatore")
    print(f"Organizzazioni: NESSUNA (per testare il messaggio)")
    
    # Mostra tutti i compilatori senza organizzazioni
    compilatori_senza_org = User.query.filter(
        User.role == 'compilatore',
        ~User.organizzazioni.any()
    ).all()
    
    print(f"\n📊 Compilatori senza organizzazioni nel DB:")
    for user in compilatori_senza_org:
        print(f"  - {user.email}")
        
    print(f"\nTotale: {len(compilatori_senza_org)} compilatori senza organizzazioni")
