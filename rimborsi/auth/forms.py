# rimborsi/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, PasswordField, BooleanField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, Optional, Email, EqualTo, ValidationError
from rimborsi.models import User

class LoginForm(FlaskForm):
    """
    Form per il login degli utenti.
    """
    email = StringField('Email', validators=[DataRequired(message="L'email è obbligatoria."), Email(message="Inserisci un'email valida.")]) 
    password = PasswordField('Password', 
                             validators=[DataRequired(message="La password è obbligatoria.")])
    remember = BooleanField('Ricordami')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """
    Form per la registrazione di nuovi utenti compilatori.
    """
    username = StringField('Nome utente', validators=[
        DataRequired(message="Il nome utente è obbligatorio."),
        Length(min=3, max=20, message="Il nome utente deve essere tra 3 e 20 caratteri.")
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message="L'email è obbligatoria."),
        Email(message="Inserisci un'email valida.")
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message="La password è obbligatoria."),
        Length(min=5, message="La password deve essere di almeno 5 caratteri.")
    ])
    
    password2 = PasswordField('Conferma Password', validators=[
        DataRequired(message="Conferma la password."),
        EqualTo('password', message="Le password devono coincidere.")
    ])
    
    submit = SubmitField('Registrati come Compilatore')
    
    def validate_username(self, username):
        """Controlla che il nome utente non sia già in uso"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Nome utente già in uso. Scegline un altro.')
    
    def validate_email(self, email):
        """Controlla che l'email non sia già in uso"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email già registrata. Usa un\'altra email o effettua il login.')

