from app import db
from datetime import datetime
from sqlalchemy.orm import relationship
import enum

class TipoSpesa(enum.Enum):
    CARBURANTE = "01"
    VITTO = "02"
    PEDAGGI = "03"
    RIPRISTINO = "04"
    PARCHEGGIO = "05"
    ALTRO = "06"
    TRASPORTO_PUBBLICO = "07"

class Spesa(db.Model):
    __tablename__ = 'spese'
    
    id = db.Column(db.Integer, primary_key=True)
    richiesta_id = db.Column(db.Integer, db.ForeignKey('richieste.id'), nullable=False)
    tipo = db.Column(db.Enum(TipoSpesa), nullable=False)
    data_spesa = db.Column(db.Date, nullable=False)
    importo_richiesto = db.Column(db.Float, nullable=False)
    importo_approvato = db.Column(db.Float)
    note = db.Column(db.Text)
    nota_istruttoria = db.Column(db.Text)  # Nota dell'istruttore per questa spesa
    
    # Campi per il polimorfismo
    __mapper_args__ = {
        'polymorphic_on': tipo,
        'polymorphic_identity': None
    }
    
    # Relazione con i documenti spesa (il backref è definito nel modello DocumentoSpesa)
    
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_modifica = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Spesa {self.id} - Tipo: {self.tipo.value} - Importo: {self.importo_richiesto}>'

class SpesaCarburante(Spesa):
    __tablename__ = 'spese_carburante'
    
    id = db.Column(db.Integer, db.ForeignKey('spese.id'), primary_key=True)
    impiego_mezzo_id = db.Column(db.Integer, db.ForeignKey('impiego_mezzo.id'), nullable=False)
    tipo_carburante = db.Column(db.String(50), nullable=False)  # Benzina, Diesel, GPL, ecc.
    litri = db.Column(db.Float)
    
    # Relazione con l'impiego del mezzo
    impiego_mezzo = relationship("ImpiegoMezzo", backref="spese_carburante")
    
    __mapper_args__ = {
        'polymorphic_identity': TipoSpesa.CARBURANTE
    }

class SpesaPedaggi(Spesa):
    __tablename__ = 'spese_pedaggi'
    
    id = db.Column(db.Integer, db.ForeignKey('spese.id'), primary_key=True)
    impiego_mezzo_id = db.Column(db.Integer, db.ForeignKey('impiego_mezzo.id'), nullable=False)
    tratta = db.Column(db.String(255), nullable=False)  # es. "Milano-Bologna"
    
    # Relazione con l'impiego del mezzo
    impiego_mezzo = relationship("ImpiegoMezzo", backref="spese_pedaggi")
    
    __mapper_args__ = {
        'polymorphic_identity': TipoSpesa.PEDAGGI
    }

class SpesaRipristino(Spesa):
    __tablename__ = 'spese_ripristino'
    
    id = db.Column(db.Integer, db.ForeignKey('spese.id'), primary_key=True)
    impiego_mezzo_id = db.Column(db.Integer, db.ForeignKey('impiego_mezzo.id'), nullable=False)
    descrizione_intervento = db.Column(db.Text, nullable=False)
    
    # Relazione con l'impiego del mezzo
    impiego_mezzo = relationship("ImpiegoMezzo", backref="spese_ripristino")
    
    __mapper_args__ = {
        'polymorphic_identity': TipoSpesa.RIPRISTINO
    }

class SpesaVitto(Spesa):
    __tablename__ = 'spese_vitto'
    
    id = db.Column(db.Integer, db.ForeignKey('spese.id'), primary_key=True)
    numero_pasti = db.Column(db.Integer, nullable=False, default=1)
    
    __mapper_args__ = {
        'polymorphic_identity': TipoSpesa.VITTO
    }

class SpesaParcheggio(Spesa):
    __tablename__ = 'spese_parcheggio'
    
    id = db.Column(db.Integer, db.ForeignKey('spese.id'), primary_key=True)
    indirizzo = db.Column(db.String(255))
    durata_ore = db.Column(db.Float)
    
    __mapper_args__ = {
        'polymorphic_identity': TipoSpesa.PARCHEGGIO
    }

class SpesaAltro(Spesa):
    __tablename__ = 'spese_altro'
    
    id = db.Column(db.Integer, db.ForeignKey('spese.id'), primary_key=True)
    descrizione_dettagliata = db.Column(db.Text, nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': TipoSpesa.ALTRO
    }

class SpesaTrasportoPubblico(Spesa):
    __tablename__ = 'spese_trasporto_pubblico'
    
    id = db.Column(db.Integer, db.ForeignKey('spese.id'), primary_key=True)
    tipo_trasporto = db.Column(db.String(100), nullable=False)  # Treno, Bus, Metro, ecc.
    tratta = db.Column(db.String(255), nullable=False)  # es. "Milano-Roma"
    
    __mapper_args__ = {
        'polymorphic_identity': TipoSpesa.TRASPORTO_PUBBLICO
    }
