from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Optional, NumberRange

class RichiestaForm(FlaskForm):
    """
    Form per la creazione dei dati generali di una Richiesta di rimborso.
    """
    
    # Campi compilati dall'utente
    attivita_svolta = TextAreaField('Descrizione Attività Svolta', 
                                    validators=[DataRequired(message="La descrizione dell'attività è obbligatoria.")])
    
    data_inizio_attivita = DateField('Data Inizio Attività', 
                                     format='%Y-%m-%d', 
                                     validators=[DataRequired(message="La data di inizio è obbligatoria.")])
    
    data_fine_attivita = DateField('Data Fine Attività', 
                                   format='%Y-%m-%d', 
                                   validators=[DataRequired(message="La data di fine è obbligatoria.")])
    
    numero_volontari_coinvolti = IntegerField('Numero Volontari Coinvolti', 
                                              validators=[Optional(), 
                                                          NumberRange(min=1, message="Il numero di volontari deve essere almeno 1.")])
    
    submit = SubmitField('Salva e Continua')