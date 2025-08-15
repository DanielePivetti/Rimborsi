# rimborsi/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    """
    Form per il login degli utenti.
    """
    email = StringField('Email', 
                        validators=[DataRequired(message="L'email è obbligatoria."), 
                                    Email(message="Inserisci un'email valida.")])
    password = PasswordField('Password', 
                             validators=[DataRequired(message="La password è obbligatoria.")])
    remember = BooleanField('Ricordami')
    submit = SubmitField('Login')

# In futuro, qui aggiungeremo anche RegistrationForm, etc.
