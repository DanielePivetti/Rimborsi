from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from app import db, login_manager
from app.models.user_odv import user_odv_association

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nome = db.Column(db.String(64))
    cognome = db.Column(db.String(64))
    ruolo = db.Column(db.String(20), default='utente')  # 'utente', 'amministratore', 'istruttore'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazione molti-a-molti con le organizzazioni
    organizzazioni = db.relationship('Odv', 
                                    secondary=user_odv_association,
                                    primaryjoin=(user_odv_association.c.user_id == id),
                                    secondaryjoin="Odv.id == user_odv_association.c.odv_id",
                                    backref=db.backref('compilatori', lazy='dynamic'),
                                    lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.ruolo == 'amministratore'
    
    def is_istruttore(self):
        return self.ruolo == 'istruttore' or self.ruolo == 'amministratore'
    
    def is_compilatore(self):
        return self.ruolo == 'utente'
    
    def can_access_odv(self, odv_id):
        """Verifica se l'utente può accedere a una specifica organizzazione"""
        # Amministratori e istruttori possono accedere a tutte le organizzazioni
        if self.is_admin() or self.is_istruttore():
            return True
        
        # Per i compilatori, verifica se l'organizzazione è associata
        return self.organizzazioni.filter_by(id=odv_id).first() is not None
