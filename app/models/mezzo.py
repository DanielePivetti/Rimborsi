from app import db
from datetime import datetime
import enum

class TipologiaMezzo(enum.Enum):
    VEICOLO = "veicolo"
    AUTOCARRO = "autocarro"
    IDROPULITRICE = "idropulitrice"
    TORREFARO = "torrefaro"

class Mezzo(db.Model):
    __tablename__ = 'mezzo'
    
    id = db.Column(db.Integer, primary_key=True)
    odv_id = db.Column(db.Integer, db.ForeignKey('odv.id'), nullable=False)
    tipologia = db.Column(db.Enum(TipologiaMezzo), nullable=False)
    targa_inventario = db.Column(db.String(50), nullable=False)
    descrizione = db.Column(db.String(255))
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_modifica = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Mezzo {self.tipologia.value} - {self.targa_inventario}>'
