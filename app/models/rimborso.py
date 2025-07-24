from datetime import datetime
from app import db
from sqlalchemy.orm import relationship

class Rimborso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_richiesta = db.Column(db.DateTime, default=datetime.utcnow)
    descrizione = db.Column(db.String(200), nullable=False)
    importo = db.Column(db.Float, nullable=False)
    data_spesa = db.Column(db.Date, nullable=False)
    categoria = db.Column(db.String(50))  # Categoria di spesa (trasporto, alloggio, pasti, ecc.)
    stato = db.Column(db.String(20), default='in_attesa')  # 'in_attesa', 'approvato', 'rifiutato'
    note = db.Column(db.Text)
    file_allegato = db.Column(db.String(200))  # Percorso del file allegato (ricevuta/fattura)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    richiedente = relationship("User", foreign_keys=[user_id], backref="rimborsi")
    approvato_da = db.Column(db.Integer, db.ForeignKey('user.id'))
    approvatore = relationship("User", foreign_keys=[approvato_da])
    data_approvazione = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Rimborso #{self.id} - {self.importo}€>'
    
    @property
    def stato_formattato(self):
        stati = {
            'in_attesa': 'In attesa',
            'approvato': 'Approvato',
            'rifiutato': 'Rifiutato'
        }
        return stati.get(self.stato, self.stato)
