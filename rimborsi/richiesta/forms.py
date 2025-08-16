from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Optional, NumberRange
# AGGIUNTE NECESSARIE
from wtforms_sqlalchemy.fields import QuerySelectField
from rimborsi.models import Evento

# Funzione helper che dice al campo come ottenere gli eventi
def evento_query():
    # Ordiniamo per data di inizio decrescente per mostrare i più recenti prima
    return Evento.query.order_by(Evento.data_inizio.desc())

class RichiestaForm(FlaskForm):
    """
    Form per la creazione dei dati generali di una Richiesta di rimborso.
    """
    # NUOVO CAMPO per la selezione dell'evento
    evento = QuerySelectField('Seleziona l\'Evento di Riferimento',
                              query_factory=evento_query,
                              get_label='nome',
                              allow_blank=False,
                              validators=[DataRequired(message="Devi selezionare un evento.")])
    
    data_inizio_attivita = DateField('Data Inizio Attività', 
                                     format='%Y-%m-%d', 
                                     validators=[DataRequired(message="La data di inizio è obbligatoria.")])
    
    data_fine_attivita = DateField('Data Fine Attività', 
                                   format='%Y-%m-%d', 
                                   validators=[DataRequired(message="La data di fine è obbligatoria.")])

    
    attivita_svolta = TextAreaField('Descrizione Attività Svolta', 
                                    validators=[DataRequired(message="La descrizione dell'attività è obbligatoria.")])
    
        
    numero_volontari_coinvolti = IntegerField('Numero Volontari Coinvolti', 
                                              validators=[Optional(), 
                                                          NumberRange(min=1, message="Il numero di volontari deve essere almeno 1.")])
    
    submit = SubmitField('Salva e Continua')