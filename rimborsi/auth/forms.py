# rimborsi/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, PasswordField, BooleanField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, Optional, Email

class LoginForm(FlaskForm):
    """
    Form per il login degli utenti.
    """
    email = StringField('Email', validators=[DataRequired(message="L'email è obbligatoria."), Email(message="Inserisci un'email valida.")]) 
    password = PasswordField('Password', 
                             validators=[DataRequired(message="La password è obbligatoria.")])
    remember = BooleanField('Ricordami')
    submit = SubmitField('Login')

# In futuro, qui aggiungeremo anche RegistrationForm, etc.

