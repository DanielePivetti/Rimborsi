from app import db
from datetime import datetime

class Odv(db.Model):
    __tablename__ = 'odv'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    acronimo = db.Column(db.String(50))
    codice_interno = db.Column(db.String(100))
    provincia = db.Column(db.String(100), nullable=False)
    comune = db.Column(db.String(100), nullable=False)
    indirizzo = db.Column(db.String(255), nullable=False)
    pec = db.Column(db.String(255), nullable=False)
    recapito_telefonico = db.Column(db.String(50), nullable=False)
    legale_rappresentante = db.Column(db.String(255), nullable=False)
    iban = db.Column(db.String(50), nullable=False)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_modifica = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    mezzi = db.relationship('Mezzo', backref='organizzazione', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<ODV {self.nome} ({self.acronimo})>'
