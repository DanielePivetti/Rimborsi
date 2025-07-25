from app import db
from datetime import datetime

class ImpiegoMezzo(db.Model):
    __tablename__ = 'impiego_mezzo'
    
    id = db.Column(db.Integer, primary_key=True)
    mezzo_id = db.Column(db.Integer, db.ForeignKey('mezzo.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventi.id'), nullable=False)
    data_inizio = db.Column(db.DateTime, nullable=False)
    data_fine = db.Column(db.DateTime, nullable=False)
    km_partenza = db.Column(db.Integer, nullable=False)
    km_arrivo = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text)
    
    # Relazioni
    mezzo = db.relationship('Mezzo', backref='impieghi', lazy=True)
    evento = db.relationship('Evento', backref='impieghi_mezzi', lazy=True)
    
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_modifica = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ImpiegoMezzo {self.id} - Mezzo: {self.mezzo_id} - Evento: {self.evento_id}>'
    
    @property
    def km_percorsi(self):
        """Calcola i km percorsi basandosi sui km di partenza e arrivo"""
        return self.km_arrivo - self.km_partenza if self.km_arrivo and self.km_partenza else 0
    
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_modifica = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ImpiegoMezzo {self.id} - Mezzo: {self.mezzo_id} - Evento: {self.evento_id}>'
