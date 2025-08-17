from operator import length_hint
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, IntegerField, SubmitField, ValidationError
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from rimborsi.models import Evento, Spesa, MezzoAttrezzatura
from wtforms import FloatField, DateTimeField

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
    

# (la funzione mezzi_query che abbiamo già scritto va bene)

class SpesaForm(FlaskForm):
    """
    Form unificato per creare/modificare una Spesa e il suo eventuale Impiego.
    """
    # --- Campi della SPESA ---
    categoria = SelectField('Categoria di Spesa', choices=[
        ('01', 'Carburante'),
        ('02', 'Pedaggi autostradali'),
        ('03', 'Pasti'),
        ('04', 'Ripristino danni mezzi'),
        ('05', 'Viaggio'),
        ('06', 'Altro')
    ], validators=[DataRequired()])
    
    data_spesa = DateField('Data della Spesa', format='%Y-%m-%d', validators=[DataRequired()])
    descrizione_spesa = TextAreaField('Descrizione Dettagliata', validators=[DataRequired(), Length(max=250)])
    importo_richiesto = FloatField('Importo Richiesto (€)', validators=[DataRequired()])
    
    # --- Campi dell'IMPIEGO MEZZO (Facoltativi) ---
    # Questi campi verranno mostrati/nascosti nel template con JavaScript
    mezzo_attrezzatura = QuerySelectField('Mezzo/Attrezzatura Utilizzato',
                                          query_factory=lambda: MezzoAttrezzatura.query.all(), # Query temporanea
                                          get_label='targa_inventario',
                                          allow_blank=True) # Permettiamo che sia vuoto
    
    localita_impiego = StringField('Località di Impiego', validators=[Optional(), Length(max=200)])
    data_ora_inizio_impiego = DateTimeField('Data/Ora Inizio', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    data_ora_fine_impiego = DateTimeField('Data/Ora Fine', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    km_partenza = FloatField('Km Partenza', validators=[Optional()])
    km_arrivo = FloatField('Km Arrivo', validators=[Optional()])

    submit = SubmitField('Salva Spesa')

    # Costruttore per filtrare i mezzi per organizzazione
    def __init__(self, organizzazione_id, *args, **kwargs):
        super(SpesaForm, self).__init__(*args, **kwargs)
        self.mezzo_attrezzatura.query = MezzoAttrezzatura.query.filter_by(organizzazione_id=organizzazione_id).order_by(MezzoAttrezzatura.targa_inventario)

    # Validazione personalizzata
    def validate_mezzo_attrezzatura(self, field):
        """
        Questo validatore rende il campo 'mezzo_attrezzatura' obbligatorio
        solo se la categoria di spesa lo richiede.
        """
        categorie_con_impiego = ['01', '02', '04']
        # Se la categoria scelta è una di quelle che richiede il mezzo...
        if self.categoria.data in categorie_con_impiego:
            # ... e il campo del mezzo è vuoto (non è stato selezionato nulla)...
            if not field.data:
                # ... allora solleva un errore di validazione.
                raise ValidationError('Per questa categoria di spesa è obbligatorio selezionare un mezzo/attrezzatura.')