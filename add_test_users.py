#!/usr/bin/env python
"""
Script per aggiungere utenti di test al database Rimborsi
Aggiunge 3 utenti compilatori per i test dell'applicazione
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Aggiungi il percorso del progetto al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rimborsi import create_app, db
from rimborsi.models import User

def create_test_users():
    """Crea gli utenti di test nel database"""
    
    # Lista degli utenti da creare
    test_users = [
        {
            'username': 'mariorossi',
            'email': 'mariorossi@test.com',
            'password': '12345',
            'role': 'compilatore'
        },
        {
            'username': 'mariobianchi', 
            'email': 'mariobianchi@test.com',
            'password': '12345',
            'role': 'compilatore'
        },
        {
            'username': 'ritaneri',
            'email': 'ritaneri@test.com',  # Corretto l'errore di battitura
            'password': '12345',
            'role': 'compilatore'
        }
    ]
    
    app = create_app()
    
    with app.app_context():
        print("🚀 Avvio creazione utenti di test...")
        print("-" * 50)
        
        created_count = 0
        skipped_count = 0
        
        for user_data in test_users:
            # Controlla se l'utente esiste già
            existing_user = User.query.filter(
                (User.email == user_data['email']) | 
                (User.username == user_data['username'])
            ).first()
            
            if existing_user:
                print(f"⚠️  Utente {user_data['email']} già esistente - SALTATO")
                skipped_count += 1
                continue
            
            # Crea il nuovo utente
            new_user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                role=user_data['role']
            )
            
            try:
                db.session.add(new_user)
                db.session.commit()
                print(f"✅ Creato utente: {user_data['email']} (username: {user_data['username']})")
                created_count += 1
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Errore nella creazione di {user_data['email']}: {str(e)}")
        
        print("-" * 50)
        print(f"📊 Riepilogo:")
        print(f"   • Utenti creati: {created_count}")
        print(f"   • Utenti saltati: {skipped_count}")
        print(f"   • Totale processati: {len(test_users)}")
        
        if created_count > 0:
            print("\n🎯 Utenti pronti per il test!")
            print("   Puoi ora utilizzare questi utenti per testare l'associazione alle organizzazioni.")
            print("   Tutti gli utenti hanno ruolo 'compilatore' e password '12345'")

def show_existing_users():
    """Mostra gli utenti esistenti nel database"""
    app = create_app()
    
    with app.app_context():
        print("\n📋 Utenti esistenti nel database:")
        print("-" * 50)
        
        users = User.query.all()
        
        if not users:
            print("   Nessun utente trovato nel database")
        else:
            for user in users:
                org_count = len(user.organizzazioni) if user.organizzazioni else 0
                org_status = f"({org_count} org.)" if org_count > 0 else "(senza org.)"
                print(f"   • {user.email} - {user.role} {org_status}")

if __name__ == "__main__":
    print("🔧 Script di creazione utenti di test - App Rimborsi")
    print("=" * 60)
    
    # Mostra utenti esistenti
    show_existing_users()
    
    # Crea i nuovi utenti
    create_test_users()
    
    # Mostra di nuovo la lista aggiornata
    print("\n" + "=" * 60)
    show_existing_users()
    
    print("\n✨ Script completato!")
