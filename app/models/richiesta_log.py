from app import db
from datetime import datetime
import enum



# Enum per gli stati della richiesta
class StatoRichiesta(enum.Enum):
    IN_LAVORAZIONE = "in_lavorazione"
    TRASMESSA = "trasmessa"
    APPROVATA = "approvata"
    RIFIUTATA = "rifiutata"

class RichiestaLog(db.Model):
    __tablename__ = 'richiesta_log'
    
    id = db.Column(db.Integer, primary_key=True)
    richiesta_id = db.Column(db.Integer, db.ForeignKey('richieste.id'), nullable=False)
    utente_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    descrizione = db.Column(db.String(255), nullable=True)
    dati_aggiuntivi = db.Column(db.JSON, nullable=True)

    stato = db.Column(db.Enum(StatoRichiesta), nullable=True)
    
    # Relazioni
    richiesta = db.relationship('Richiesta', backref=db.backref('log_eventi', lazy='dynamic', cascade="all, delete-orphan"))
    utente = db.relationship('User', backref=db.backref('log_richieste', lazy='dynamic'))
    
    def __repr__(self):
        return f'<RichiestaLog {self.id} - {self.stato.value if self.stato else None} - {self.timestamp}>'
