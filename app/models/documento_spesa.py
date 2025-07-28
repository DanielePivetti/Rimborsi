from app import db
from datetime import datetime
import enum
from sqlalchemy.types import TypeDecorator, Enum
from sqlalchemy import event

# Definiamo la vecchia versione dell'enum che corrisponde ai valori nel database
class TipoDocumento(enum.Enum):
    SCONTRINO = "A"
    QUIETANZA = "B"
    FATTURA = "C"
    AUTORIZZAZIONE = "D"
    ATTESTAZIONE_DANNO = "E"
    
    def get_display_name(self):
        """Restituisce il nome leggibile dell'enum"""
        return self.name.replace('_', ' ').capitalize()
        
    @classmethod
    def from_name(cls, name):
        """Converte un nome come 'SCONTRINO' nell'enum appropriato"""
        try:
            return cls[name]
        except KeyError:
            return None

class DocumentoSpesa(db.Model):
    __tablename__ = 'documenti_spesa'
    
    id = db.Column(db.Integer, primary_key=True)
    spesa_id = db.Column(db.Integer, db.ForeignKey('spese.id'), nullable=False)
    tipo = db.Column(db.Enum(TipoDocumento), nullable=False)
    numero = db.Column(db.String(100))  # Numero del documento
    data = db.Column(db.Date, nullable=False)  # Data emissione documento
    descrizione = db.Column(db.Text)  # Descrizione breve
    file_path = db.Column(db.String(255), nullable=True)  # Percorso del file allegato (opzionale)
    
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_modifica = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazione con la spesa
    spesa = db.relationship("Spesa", backref="documenti", foreign_keys=[spesa_id])
    
    def __repr__(self):
        return f'<DocumentoSpesa {self.id} - Tipo: {self.tipo.value if self.tipo else "None"} - Data: {self.data}>'
