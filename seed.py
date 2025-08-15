# seed.py
from flask import app
from rimborsi  import create_app  # Importa l'istanza dell'app Flask dal tuo file principale
from rimborsi.models  import db, User, Organizzazione, Evento, MezzoAttrezzatura
from werkzeug.security import generate_password_hash
from datetime import date

app = create_app()

def populate_db():
    """
    Popola il database con dati di test se è vuoto.
    """
    # Lavoriamo all'interno del contesto dell'applicazione Flask
    with app.app_context():
        # --- CONTROLLO: Esegui solo se il database è vuoto ---
        if User.query.first() is not None:
            print("Il database sembra essere già popolato. Nessuna azione eseguita.")
            return

        print("Database vuoto. Inizio il caricamento dei dati di test...")

        # --- 1. Creazione Utenti ---
        # Hasheremo una password semplice ("password") per tutti gli utenti di test.
        # In un'applicazione reale, questa non sarebbe una buona pratica.
        hashed_password = generate_password_hash("password", method='pbkdf2:sha256')

        admin_user = User(
            username='admin',
            email='admin@test.com',
            password_hash=hashed_password,
            role='amministratore'
        )
        istruttore_user = User(
            username='istruttore',
            email='istruttore@test.com',
            password_hash=hashed_password,
            role='istruttore'
        )
        compilatore_user = User(
            username='compilatore',
            email='compilatore@test.com',
            password_hash=hashed_password,
            role='compilatore'
        )
        db.session.add_all([admin_user, istruttore_user, compilatore_user])
        print("-> Utenti creati.")

        # --- 2. Creazione Organizzazioni ---
        org1 = Organizzazione(
            nome="Croce Rossa Italiana - Comitato di Roma",
            acronimo="CRI Roma",
            codice_interno="RM001",
            indirizzo="Via della Croce Rossa 4, Roma"
        )
        org2 = Organizzazione(
            nome="Croce Verde Torino",
            acronimo="CVT",
            codice_interno="TO001",
            indirizzo="Corso Unità d'Italia 1, Torino"
        )
        db.session.add_all([org1, org2])
        print("-> Organizzazioni create.")

        # --- 3. Creazione Eventi ---
        evento1 = Evento(
            protocollo_attivazione="20250812DPC_0001",
            nome="Emergenza Sisma Centro Italia 2025",
            tipologia='A', # Emergenza
            data_inizio=date(2025, 8, 12),
            descrizione="Evento sismico di magnitudo 6.0 nell'Appennino centrale."
        )
        evento2 = Evento(
            protocollo_attivazione="20250915DPC_0002",
            nome="Esercitazione Nazionale Alpi 2025",
            tipologia='C', # Esercitazione
            data_inizio=date(2025, 9, 15),
            descrizione="Esercitazione di ricerca e soccorso in ambiente montano."
        )
        db.session.add_all([evento1, evento2])
        print("-> Eventi creati.")
        
        # È necessario fare un commit qui per assegnare gli ID a org1 e org2
        # prima di poter creare i mezzi che dipendono da loro.
        db.session.commit()

        # --- 4. Creazione Mezzi/Attrezzature ---
        mezzo1 = MezzoAttrezzatura(
            tipologia='A', # Mezzo
            targa_inventario='CRI-RM-123',
            descrizione='Ambulanza Fiat Ducato',
            organizzazione_id=org1.id
        )
        attrezzatura1 = MezzoAttrezzatura(
            tipologia='B', # Attrezzatura
            targa_inventario='CVT-IDRO-01',
            descrizione='Idrovora 1500 l/min',
            organizzazione_id=org2.id
        )
        db.session.add_all([mezzo1, attrezzatura1])
        print("-> Mezzi e Attrezzature creati.")

        # --- 5. Associazione Utente-Organizzazione ---
        # Associamo l'utente 'compilatore' all'organizzazione 'CRI Roma'
        compilatore_user.organizzazioni.append(org1)
        print("-> Associazione Compilatore-Organizzazione creata.")

        # --- SALVATAGGIO FINALE ---
        db.session.commit()
        print("\nCaricamento completato con successo!")


if __name__ == '__main__':
    populate_db()
