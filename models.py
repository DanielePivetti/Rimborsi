from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Inizializzazione dell'oggetto db (verrà configurato nell'app.py)
db = SQLAlchemy()

# Tabella associativa per la relazione Molti-a-Molti tra Utente e Organizzazione
associazione_utente_organizzazione = db.Table('associazione_utente_organizzazione',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('organizzazione_id', db.Integer, db.ForeignKey('organizzazione.id'), primary_key=True)
)

class User(db.Model):
    """ Modello per gli utenti del sistema (Amministratore, Compilatore, Istruttore) """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False) 
    role = db.Column(db.String(20), nullable=False) # Es. 'amministratore', 'compilatore', 'istruttore'
    
    # Relazione Molti-a-Molti con Organizzazione
    organizzazioni = db.relationship('Organizzazione', secondary=associazione_utente_organizzazione,
                                     back_populates='utenti_compilatori')

class Organizzazione(db.Model):
    """ Anagrafica delle organizzazioni di volontariato """
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    acronimo = db.Column(db.String(20))
    codice_interno = db.Column(db.String(20), unique=True)
    indirizzo = db.Column(db.String(200))

    # Relazioni (lato "uno" di una relazione uno-a-molti)
    mezzi = db.relationship('MezzoAttrezzatura', backref='organizzazione', lazy=True)
    richieste = db.relationship('Richiesta', backref='organizzazione', lazy=True)
    utenti_compilatori = db.relationship('User', secondary=associazione_utente_organizzazione,
                                         back_populates='organizzazioni')

class MezzoAttrezzatura(db.Model):
    """ Registro dei mezzi e delle attrezzature di ogni organizzazione """
    id = db.Column(db.Integer, primary_key=True)
    tipologia = db.Column(db.String(1), nullable=False) # 'A': Mezzo, 'B': Attrezzatura
    targa_inventario = db.Column(db.String(50), unique=True, nullable=False)
    descrizione = db.Column(db.String(200))
    organizzazione_id = db.Column(db.Integer, db.ForeignKey('organizzazione.id'), nullable=False)

class Evento(db.Model):
    """ Descrive l'evento (emergenza, esercitazione, etc.) """
    id = db.Column(db.Integer, primary_key=True)
    protocollo_attivazione = db.Column(db.String(50), unique=True)
    nome = db.Column(db.String(150), nullable=False)
    tipologia = db.Column(db.String(1), nullable=False) # 'A', 'B', 'C', 'D', 'E'
    data_inizio = db.Column(db.Date)
    data_fine = db.Column(db.Date)
    descrizione = db.Column(db.Text)
    richieste = db.relationship('Richiesta', backref='evento', lazy=True)

class Richiesta(db.Model):
    """ Contenitore principale della richiesta di rimborso """
    id = db.Column(db.Integer, primary_key=True)
    stato = db.Column(db.String(1), default='A', nullable=False) # 'A': bozza, 'B': trasmessa, 'C': istruita
    esito = db.Column(db.String(1)) # 'A': Approvata, 'B': parzialmente, 'C': respinta
    attivita_svolta = db.Column(db.Text)
    data_inizio_attivita = db.Column(db.Date)
    data_fine_attivita = db.Column(db.Date)
    numero_volontari_coinvolti = db.Column(db.Integer)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_invio = db.Column(db.DateTime)
    data_fine_istruttoria = db.Column(db.DateTime)
    
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)
    organizzazione_id = db.Column(db.Integer, db.ForeignKey('organizzazione.id'), nullable=False)
    
    spese = db.relationship('SpesaRichiesta', backref='richiesta', lazy=True, cascade="all, delete-orphan")

class SpesaRichiesta(db.Model):
    """ Singola voce di costo all'interno di una richiesta """
    id = db.Column(db.Integer, primary_key=True)
    data_spesa = db.Column(db.Date, nullable=False)
    categoria = db.Column(db.String(1), nullable=False) # 'A', 'B', 'C', 'D', 'E'
    descrizione_spesa = db.Column(db.String(250))
    importo_richiesto = db.Column(db.Float, nullable=False)
    importo_approvato = db.Column(db.Float)
    note_istruttoria = db.Column(db.Text)
    
    richiesta_id = db.Column(db.Integer, db.ForeignKey('richiesta.id'), nullable=False)
    
    documenti = db.relationship('DocumentoSpesa', backref='spesa', lazy=True, cascade="all, delete-orphan")
    impiego = db.relationship('ImpiegoMezzoAttrezzatura', backref='spesa', uselist=False, cascade="all, delete-orphan")

class DocumentoSpesa(db.Model):
    """ Dettagli del giustificativo di spesa (scontrino, fattura, etc.) """
    id = db.Column(db.Integer, primary_key=True)
    data_documento = db.Column(db.Date, nullable=False)
    fornitore = db.Column(db.String(150))
    importo_documento = db.Column(db.Float, nullable=False)
    tipo_documento = db.Column(db.String(50)) # "Giustificativo", "AttestazioneDanno", "Autorizzazione"
    
    spesa_id = db.Column(db.Integer, db.ForeignKey('spesa.id'), nullable=False)

class ImpiegoMezzoAttrezzatura(db.Model):
    """ Dettaglio dell'utilizzo di un mezzo/attrezzatura per una spesa """
    id = db.Column(db.Integer, primary_key=True)
    localita_impiego = db.Column(db.String(200))
    data_ora_inizio_impiego = db.Column(db.DateTime)
    data_ora_fine_impiego = db.Column(db.DateTime)
    km_partenza = db.Column(db.Float)
    km_arrivo = db.Column(db.Float)
    
    @property
    def km_totali(self):
        if self.km_partenza is not None and self.km_arrivo is not None:
            return self.km_arrivo - self.km_partenza
        return 0

    mezzo_attrezzatura_id = db.Column(db.Integer, db.ForeignKey('mezzo_attrezzatura.id'), nullable=False)
    spesa_id = db.Column(db.Integer, db.ForeignKey('spesa.id'), unique=True, nullable=False)