from app import db
from datetime import datetime
from sqlalchemy.orm import relationship
import enum

class StatoRichiesta(enum.Enum):
    IN_ATTESA = "in_attesa"
    APPROVATA = "approvata"
    PARZIALMENTE_APPROVATA = "parzialmente_approvata"
    RIFIUTATA = "rifiutata"

class Richiesta(db.Model):
    __tablename__ = 'richieste'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    odv_id = db.Column(db.Integer, db.ForeignKey('odv.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventi.id'), nullable=False)
    data_richiesta = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    stato = db.Column(db.Enum(StatoRichiesta), default=StatoRichiesta.IN_ATTESA, nullable=False)
    note_richiedente = db.Column(db.Text)
    note_istruttore = db.Column(db.Text)
    approvato_da = db.Column(db.Integer, db.ForeignKey('user.id'))
    data_approvazione = db.Column(db.DateTime)
    
    # Relazioni
    richiedente = relationship("User", foreign_keys=[user_id], backref="richieste_inviate")
    approvatore = relationship("User", foreign_keys=[approvato_da], backref="richieste_approvate")
    odv = relationship("Odv", backref="richieste")
    evento = relationship("Evento", backref="richieste")
    spese = relationship("Spesa", backref="richiesta", cascade="all, delete-orphan")
    
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_modifica = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Richiesta #{self.id} - Stato: {self.stato.value}>'
    
    @property
    def importo_totale_richiesto(self):
        """Calcola l'importo totale richiesto sommando tutte le spese"""
        return sum(spesa.importo_richiesto for spesa in self.spese)
    
    @property
    def importo_totale_approvato(self):
        """Calcola l'importo totale approvato sommando tutte le spese approvate"""
        return sum(spesa.importo_approvato for spesa in self.spese if spesa.importo_approvato is not None)
