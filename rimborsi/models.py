from sqlalchemy import event
from datetime import datetime
from flask_login import UserMixin
from . import db
import enum

# db = SQLAlchemy()

# --- TABELLA ASSOCIATIVA ---
associazione_utente_organizzazione = db.Table('associazione_utente_organizzazione',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('organizzazione_id', db.Integer, db.ForeignKey('organizzazione.id'), primary_key=True)
)

# --- MODELLI ---

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # Rimosso unique=True da qui
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    
    organizzazioni = db.relationship('Organizzazione', secondary=associazione_utente_organizzazione, back_populates='utenti_compilatori')

    # Aggiunto __table_args__ per definire i vincoli con un nome
    __table_args__ = (
        db.UniqueConstraint('username', name='uq_user_username'),
        db.UniqueConstraint('email', name='uq_user_email'),
    )

class Organizzazione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    acronimo = db.Column(db.String(20))
    codice_interno = db.Column(db.String(20)) # Rimosso unique=True
    indirizzo = db.Column(db.String(200))

    mezzi = db.relationship('MezzoAttrezzatura', backref='organizzazione', lazy=True)
    richieste = db.relationship('Richiesta', backref='organizzazione', lazy=True)
    utenti_compilatori = db.relationship('User', secondary=associazione_utente_organizzazione, back_populates='organizzazioni')
    
    __table_args__ = (db.UniqueConstraint('codice_interno', name='uq_organizzazione_codice_interno'),)

class MezzoAttrezzatura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipologia = db.Column(db.String(1), nullable=False)
    targa_inventario = db.Column(db.String(50), nullable=False) # Rimosso unique=True
    descrizione = db.Column(db.String(200))
    organizzazione_id = db.Column(db.Integer, db.ForeignKey('organizzazione.id'), nullable=False)
    # Campi per mezzi temporanei (aggiungi dopo organizzazione_id)
    is_temporary = db.Column(db.Boolean, default=False, nullable=False)
    authorization_document = db.Column(db.String(255), nullable=True)  # Nome file autorizzazione
    authorizing_entity = db.Column(db.String(200), nullable=True)  # Ente che rilascia autorizzazione
    authorization_date = db.Column(db.Date, nullable=True)  # Data autorizzazione
    
    impieghi = db.relationship('ImpiegoMezzoAttrezzatura', backref='mezzo_attrezzatura', lazy=True)
    
    __table_args__ = (db.UniqueConstraint('targa_inventario', name='uq_mezzoattrezzatura_targa_inventario'),)

# Aggiungi questo metodo alla classe MezzoAttrezzatura
def is_authorization_valid(self):
    """Verifica se il mezzo temporaneo ha un'autorizzazione valida."""
    if not self.is_temporary:
        return True
    return (self.authorization_document is not None and 
            self.authorizing_entity is not None and 
            self.authorization_date is not None)

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    protocollo_attivazione = db.Column(db.String(50), unique=True)
    nome = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text)
    tipologia = db.Column(db.String(1), nullable=False)
    data_inizio = db.Column(db.Date)
    data_fine = db.Column(db.Date)
    richieste = db.relationship('Richiesta', backref='evento', lazy=True)

    __table_args__ = (db.UniqueConstraint('protocollo_attivazione', name='uq_evento_protocollo_attivazione'),)

# Gestione centralizzata degli stati della richiesta

class StatoRichiesta(enum.Enum):
    BOZZA = 'A'
    IN_ISTRUTTORIA = 'B'
    ISTRUITA = 'C'
 
    @property
    def label(self):
        # Mappatura per visualizzare un'etichetta leggibile nel frontend
        return {
            self.BOZZA: 'In Bozza',
            self.IN_ISTRUTTORIA: 'In Istruttoria',
            self.ISTRUITA: 'Istruita'
        }.get(self)


class Richiesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codice_uni = db.Column(db.String(25),  nullable=False)
    stato = db.Column(db.Enum(StatoRichiesta), default=StatoRichiesta.BOZZA, nullable=False)
    esito = db.Column(db.String(1))
    attivita_svolta = db.Column(db.Text)
    data_inizio_attivita = db.Column(db.Date)
    data_fine_attivita = db.Column(db.Date)
    numero_volontari_coinvolti = db.Column(db.Integer)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_invio = db.Column(db.DateTime)
    protocollo_invio = db.Column(db.String(50), nullable=True)
    note_istruttoria = db.Column(db.Text, nullable=True)
    data_fine_istruttoria = db.Column(db.DateTime)
    protocollo_istruttoria = db.Column(db.String(50), nullable=True)
    
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)
    organizzazione_id = db.Column(db.Integer, db.ForeignKey('organizzazione.id'), nullable=False)
    impieghi = db.relationship('ImpiegoMezzoAttrezzatura', backref='richiesta', lazy=True, cascade="all, delete-orphan")
    spese = db.relationship('Spesa', backref='richiesta', lazy=True, cascade="all, delete-orphan")
   
    __table_args__ = (
        db.UniqueConstraint('protocollo_invio', name='uq_richiesta_protocollo_invio'),
        db.UniqueConstraint('protocollo_istruttoria', name='uq_richiesta_protocollo_istruttoria'),
        db.UniqueConstraint('codice_uni', name='uq_richiesta_codice_uni')
    )

# Generazione automatica del codice

@event.listens_for(Richiesta, 'before_insert')
def generate_codice(mapper, connection, target):
    if not target.codice_uni:
        org = Organizzazione.query.get(target.organizzazione_id)
        if org and org.codice_interno:
            datastamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            target.codice_uni = f"{org.codice_interno}{datastamp}"
        else:
            datastamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            target.codice_uni = f"ORG{datastamp}"


class Spesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_spesa = db.Column(db.Date, nullable=False)
    categoria = db.Column(db.String(1), nullable=False)
    descrizione_spesa = db.Column(db.String(250))
    importo_richiesto = db.Column(db.Float, nullable=False)
    importo_approvato = db.Column(db.Float)
    note_istruttoria = db.Column(db.Text)
    
    richiesta_id = db.Column(db.Integer, db.ForeignKey('richiesta.id'), nullable=False)
    
    # --- RELAZIONE CORRETTA ---
    # Questa riga dice a SQLAlchemy: "una Spesa può avere molti Documenti".
    # Il 'backref' crea un attributo virtuale 'spesa' nel modello DocumentoSpesa.
    documenti = db.relationship('DocumentoSpesa', backref='spesa', lazy=True, cascade="all, delete-orphan")
    impiego_id = db.Column(db.Integer, db.ForeignKey('impiego_mezzo_attrezzatura.id'), nullable=True)

class DocumentoSpesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_documento = db.Column(db.Date, nullable=False)
    fornitore = db.Column(db.String(150))
    importo_documento = db.Column(db.Float, nullable=False)
    tipo_documento = db.Column(db.String(50))
    verificato = db.Column(db.Boolean, default=False)
    note_istruttoria = db.Column(db.Text, nullable=True)

    # --- CHIAVE ESTERNA CORRETTA ---
    # Questa è la colonna che collega fisicamente questa tabella alla tabella 'spesa'.
    spesa_id = db.Column(db.Integer, db.ForeignKey('spesa.id'), nullable=False)
    nome_file = db.Column(db.String(255), nullable=True) # Campo per il nome del file salvato


    # Metodo per visualizzare il tipo di documento
    def get_tipo_documento_display(self):
        """
        Restituisce il nome completo del tipo di documento.
        """
        tipo = {
            'A': 'Scontrino',
            'B': 'Fattura',
            'C': 'Autorizzazione',
            'D': 'Attestazione Danno'
        }
        # Restituisce il valore corrispondente alla chiave, o il codice stesso se non trovato
        return tipo.get(self.tipo_documento, self.tipo_documento)

class ImpiegoMezzoAttrezzatura(db.Model):
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

    richiesta_id = db.Column(db.Integer, db.ForeignKey('richiesta.id'), nullable=False)
    mezzo_attrezzatura_id = db.Column(db.Integer, db.ForeignKey('mezzo_attrezzatura.id'), nullable=False)
   # spesa_id = db.Column(db.Integer, db.ForeignKey('spesa.id'), unique=True, nullable=True)
    spese = db.relationship('Spesa', backref='impiego', lazy='dynamic')

class Comunicazione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    richiesta_id = db.Column(db.Integer, db.ForeignKey('richiesta.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    data_transazione = db.Column(db.DateTime, nullable=True)
    protocollo = db.Column(db.String(30), nullable=True)
    stato_precedente = db.Column(db.String(30), nullable=True)
    stato_successore = db.Column(db.String(30), nullable=True)
    descrizione = db.Column(db.Text, nullable=True)

    # Definisci la relazione con db.relationship
    richiesta = db.relationship('Richiesta', backref='comunicazioni')
    utente = db.relationship('User', backref='comunicazioni')
