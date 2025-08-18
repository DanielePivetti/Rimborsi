# rimborsi/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, PasswordField, BooleanField
from wtforms.fields import DateField, datetime
from wtforms.validators import DataRequired, Length, Optional, Email

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
