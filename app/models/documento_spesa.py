from app import db
from datetime import datetime
import enum

class TipoDocumento(enum.Enum):
    SCONTRINO = "A"
    QUIETANZA = "B"
    FATTURA = "C"
    AUTORIZZAZIONE = "D"
    ATTESTAZIONE_DANNO = "E"

class DocumentoSpesa(db.Model):
    __tablename__ = 'documenti_spesa'
    
    id = db.Column(db.Integer, primary_key=True)
    spesa_id = db.Column(db.Integer, db.ForeignKey('spese.id'), nullable=False)
    tipo = db.Column(db.Enum(TipoDocumento), nullable=False)
    numero = db.Column(db.String(100))  # Numero del documento
    data = db.Column(db.Date, nullable=False)  # Data emissione documento
    descrizione = db.Column(db.Text)  # Descrizione breve
    file_path = db.Column(db.String(255), nullable=False)  # Percorso del file allegato
    
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_modifica = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazione con la spesa
    spesa = db.relationship("Spesa", backref="documenti", foreign_keys=[spesa_id])
    
    def __repr__(self):
        return f'<DocumentoSpesa {self.id} - Tipo: {self.tipo.value} - Data: {self.data}>'
