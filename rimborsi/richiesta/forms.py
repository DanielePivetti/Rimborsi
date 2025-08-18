from operator import length_hint
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, FileField, TextAreaField, IntegerField, SubmitField, ValidationError
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from rimborsi.models import Richiesta, Evento, Spesa, MezzoAttrezzatura,ImpiegoMezzoAttrezzatura, DocumentoSpesa
from wtforms import FloatField, DateTimeField
from flask_wtf.file import FileAllowed

# ... (altre classi di form) ...


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
    
# In rimborsi/richieste/forms.py


class ImpiegoMezzoForm(FlaskForm):
    """
    Form per creare/modificare un Impiego di Mezzo/Attrezzatura.
    """
    mezzo_attrezzatura = QuerySelectField('Mezzo/Attrezzatura Utilizzato',
                                          get_label='targa_inventario',
                                          allow_blank=False,
                                          validators=[DataRequired("È obbligatorio selezionare un mezzo.")])
    
    localita_impiego = StringField('Località di Impiego', validators=[Optional(), Length(max=200)])
    data_ora_inizio_impiego = DateTimeField('Data e Ora Inizio Impiego', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    data_ora_fine_impiego = DateTimeField('Data e Ora Fine Impiego', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    km_partenza = FloatField('Km Partenza', validators=[Optional()])
    km_arrivo = FloatField('Km Arrivo', validators=[Optional()])
    submit = SubmitField('Salva Impiego')

    def __init__(self, organizzazione_id, *args, **kwargs):
        super(ImpiegoMezzoForm, self).__init__(*args, **kwargs)
        # Filtra i mezzi per mostrare solo quelli dell'organizzazione corrente
        self.mezzo_attrezzatura.query = MezzoAttrezzatura.query.filter_by(
            organizzazione_id=organizzazione_id
        ).order_by(MezzoAttrezzatura.targa_inventario)
        
# In rimborsi/richieste/forms.py

# Assicurati di avere tutti gli import necessari

# Funzione helper per la query degli impieghi non ancora associati a una spesa
def impieghi_disponibili_query(richiesta_id):
    return ImpiegoMezzoAttrezzatura.query.filter_by(richiesta_id=richiesta_id).all()

class SpesaForm(FlaskForm):
    """
    Form per creare/modificare una Spesa e collegarla a un eventuale Impiego.
    """
    categoria = SelectField('Categoria di Spesa', choices=[
        ('01', 'Carburante'), ('02', 'Pedaggi autostradali'), ('03', 'Pasti'),
        ('04', 'Ripristino danni mezzi'), ('05', 'Viaggio'), ('06', 'Altro')
    ], validators=[DataRequired()])
    
    data_spesa = DateField('Data della Spesa', format='%Y-%m-%d', validators=[DataRequired()])
    descrizione_spesa = TextAreaField('Descrizione Dettagliata', validators=[DataRequired(), Length(max=250)])
    importo_richiesto = FloatField('Importo Richiesto (€)', validators=[DataRequired()])
    
    # Campo per selezionare un impiego esistente
    impiego = QuerySelectField('Collega a un Impiego Mezzo (se necessario)',
                               get_label=lambda i: f"{i.mezzo_attrezzatura.targa_inventario} del {i.data_ora_inizio_impiego.strftime('%d/%m')}",
                               allow_blank=True)

    submit = SubmitField('Salva Spesa')

    def __init__(self, richiesta_id, *args, **kwargs):
        super(SpesaForm, self).__init__(*args, **kwargs)
        # Filtra gli impieghi per mostrare solo quelli disponibili per questa richiesta
        self.impiego.query = impieghi_disponibili_query(richiesta_id)

    def validate_impiego(self, field):
        categorie_con_impiego = ['01', '02', '04']
        if self.categoria.data in categorie_con_impiego and not field.data:
            raise ValidationError('Per questa categoria di spesa è obbligatorio selezionare un impiego.')

            
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
