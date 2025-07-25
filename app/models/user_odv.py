from app import db
from datetime import datetime

# Tabella di associazione tra utenti compilatori e organizzazioni
user_odv_association = db.Table('user_odv_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('odv_id', db.Integer, db.ForeignKey('odv.id'), primary_key=True),
    db.Column('data_assegnazione', db.DateTime, default=datetime.utcnow),
    db.Column('assegnato_da', db.Integer, db.ForeignKey('user.id'))
)
