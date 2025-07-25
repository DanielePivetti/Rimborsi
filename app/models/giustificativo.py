from app import db
from datetime import datetime
import enum

class TipoGiustificativo(enum.Enum):
    FATTURA = "fattura"
    SCONTRINO = "scontrino"
    RICEVUTA = "ricevuta"
    ALTRO = "altro"

class Giustificativo(db.Model):
    __tablename__ = 'giustificativi'
    
    id = db.Column(db.Integer, primary_key=True)
    spesa_id = db.Column(db.Integer, db.ForeignKey('spese.id'), nullable=False)
    tipo = db.Column(db.Enum(TipoGiustificativo), nullable=False)
    numero = db.Column(db.String(100))  # Numero fattura/ricevuta, se applicabile
    data_emissione = db.Column(db.Date, nullable=False)
    emesso_da = db.Column(db.String(255), nullable=False)  # Fornitore/emittente
    importo = db.Column(db.Float, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)  # Percorso del file allegato
    
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_modifica = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Giustificativo {self.id} - Tipo: {self.tipo.value} - Importo: {self.importo}>'
