"""
Script semplificato per aggiungere utenti di test
"""
from rimborsi import create_app, db
from rimborsi.models import User
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy

app = create_app()

with app.app_context():
    print("Creazione utenti di test...")
    
    # Utente 1: Mario Rossi
    if not User.query.filter_by(email='mariorossi@test.com').first():
        user1 = User(
            username='mariorossi',
            email='mariorossi@test.com',
            password_hash=generate_password_hash('12345'),
            role='compilatore'
        )
        db.session.add(user1)
        print("✅ Creato: Mario Rossi")
    else:
        print("⚠️ Mario Rossi già esistente")
    
    # Utente 2: Mario Bianchi  
    if not User.query.filter_by(email='mariobianchi@test.com').first():
        user2 = User(
            username='mariobianchi',
            email='mariobianchi@test.com', 
            password_hash=generate_password_hash('12345'),
            role='compilatore'
        )
        db.session.add(user2)
        print("✅ Creato: Mario Bianchi")
    else:
        print("⚠️ Mario Bianchi già esistente")
    
    # Utente 3: Rita Neri
    if not User.query.filter_by(email='ritaneri@test.com').first():
        user3 = User(
            username='ritaneri',
            email='ritaneri@test.com',
            password_hash=generate_password_hash('12345'),
            role='compilatore'
        )
        db.session.add(user3)
        print("✅ Creato: Rita Neri")
    else:
        print("⚠️ Rita Neri già esistente")
    
    # Salva tutto
    try:
        db.session.commit()
        print("\n🎉 Utenti di test creati con successo!")
        print("Email e password per tutti: 12345")
        print("Ruolo: compilatore")
        
        # Mostra tutti i compilatori
        compilatori = User.query.filter_by(role='compilatore').all()
        print(f"\nTotale compilatori nel DB: {len(compilatori)}")
        for comp in compilatori:
            org_count = len(comp.organizzazioni) if comp.organizzazioni else 0
            print(f"- {comp.email} ({org_count} organizzazioni)")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Errore: {e}")
