# rimborsi/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, PasswordField, BooleanField
from wtforms.fields import DateField,FileField
from wtforms.validators import DataRequired, Length, Optional, Email
from flask_wtf.file import FileAllowed
from wtforms import SelectField, DateField, FloatField
from wtforms.validators import DataRequired, Optional, Length



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

class EventoForm(FlaskForm):
    """
    Form per creare e modificare un Evento.
    """
    protocollo_attivazione = StringField('Protocollo di Attivazione', validators=[Optional(), Length(max=50)])
    nome = StringField('Nome Evento', validators=[DataRequired(message="Il nome dell'evento è obbligatorio."), Length(max=100)])
    # descrizione: area di testo opzionale per testi lunghi
    descrizione = TextAreaField('Descrizione', validators=[Optional()])
    # tipologia: menu a tendina per una scelta controllata
    tipologia = SelectField('Tipologia',
                            choices=[
                                ('N', 'Nazionale'),
                                ('R', 'Regionale'),
                                ('P', 'Provinciale'),
                                ('L', 'Locale')
                            ],
                            validators=[DataRequired(message="Seleziona una tipologia.")])
    # data_inizio: campo data opzionale
    data_inizio = DateField('Data Inizio', format='%Y-%m-%d', validators=[Optional()])
    # data_fine: campo data opzionale
    data_fine = DateField('Data Fine', format='%Y-%m-%d', validators=[Optional()])
    # submit: pulsante per inviare il modulo
    submit = SubmitField('Salva Evento')


# ... (le altre tue classi di form) ...

class DocumentoSpesaForm(FlaskForm):
    """Form per inserire i dati di un documento di spesa."""
    tipo_documento = SelectField('Tipo Documento', choices=[
        ('A', 'Scontrino'),
        ('B', 'Fattura'),
        ('C', 'Autorizzazione'),
        ('D', 'Attestazione Danno')
    ], validators=[DataRequired()])
    
    data_documento = DateField('Data del Documento', format='%Y-%m-%d', validators=[DataRequired()])
    fornitore = StringField('Fornitore', validators=[Optional(), Length(max=150)])
    importo_documento = FloatField('Importo del Documento (€)', validators=[DataRequired()])
    allegato = FileField('Allega Documento (PDF, PNG, JPG)', validators=[
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 'Sono ammessi solo file PDF, PNG e JPG!')
    ])
    submit = SubmitField('Aggiungi Documento')