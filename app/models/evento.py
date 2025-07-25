from app import db
from datetime import datetime

class Evento(db.Model):
    __tablename__ = 'eventi'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # EMERGENZA, ESERCITAZIONE, ALTRO
    nome = db.Column(db.String(255), nullable=False)
    numero_attivazione = db.Column(db.String(50), nullable=False)
    data_attivazione = db.Column(db.Date, nullable=False)
    luogo = db.Column(db.Text, nullable=False)
    data_inizio = db.Column(db.Date, nullable=False)
    data_fine = db.Column(db.Date, nullable=False)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_modifica = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Evento {self.nome}>'
    
    # Metodi di utilità
    @staticmethod
    def get_tipi_evento():
        return [
            ('EMERGENZA', 'Emergenza'),
            ('ESERCITAZIONE', 'Esercitazione'),
            ('ALTRO', 'Altro')
        ]
