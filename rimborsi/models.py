# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from . import db

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
    
    impieghi = db.relationship('ImpiegoMezzoAttrezzatura', backref='mezzo_attrezzatura', lazy=True)
    
    __table_args__ = (db.UniqueConstraint('targa_inventario', name='uq_mezzoattrezzatura_targa_inventario'),)


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
class Richiesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stato = db.Column(db.String(1), default='A', nullable=False)
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
    )


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
    spese = db.relationship('Spesa', backref='impiego', lazy=True)
