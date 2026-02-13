from operator import length_hint
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, IntegerField, SubmitField, ValidationError
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from rimborsi.models import Richiesta, Evento, Spesa, MezzoAttrezzatura,ImpiegoMezzoAttrezzatura, DocumentoSpesa, StatoRichiesta
from wtforms import FloatField, DateTimeField
from flask_wtf.file import FileField, FileAllowed

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
                                      query_factory=lambda: MezzoAttrezzatura.query.filter_by(id=0),  # Query vuota di default
                                      get_label=lambda obj: f"{'[TEMP] ' if obj.is_temporary else ''}{obj.targa_inventario} - {obj.descrizione or 'N/D'}",
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
        # Includi sia mezzi permanenti che temporanei dell'organizzazione
        from sqlalchemy import or_, and_
        self.mezzo_attrezzatura.query = MezzoAttrezzatura.query.filter_by(
            organizzazione_id=organizzazione_id
        ).filter(
            or_(
                MezzoAttrezzatura.is_temporary == False,
                and_(
                    MezzoAttrezzatura.is_temporary == True,
                    MezzoAttrezzatura.authorization_document.isnot(None)
                )
            )
    ).order_by(MezzoAttrezzatura.is_temporary, MezzoAttrezzatura.targa_inventario)

        
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


# Definiamo i tipi di documento che NON richiedono un importo.
# Usare una costante rende il codice più leggibile e manutenibile.

TIPI_SENZA_IMPORTO = ['C', 'D']            
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
    # Rimuoviamo DataRequired() e aggiungiamo Optional() perché l'importo
    # non sarà sempre obbligatorio. La logica vera è nel validatore sotto.
    importo_documento = FloatField('Importo del Documento (€)', validators=[Optional()])
    allegato = FileField('Allega Documento (PDF, PNG, JPG)', validators=[
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 'Sono ammessi solo file PDF, PNG e JPG!')
    ])
    submit = SubmitField('Aggiungi Documento')
    
     # --- NUOVO VALIDATORE PERSONALIZZATO ---
    # Questa funzione funge da "rete di sicurezza" lato server
    
    def validate_importo_documento(self, field):
        """
        Controlla che l'importo sia presente solo se il tipo di documento lo richiede.
        """
        tipo_selezionato = self.tipo_documento.data
        
        # Se il tipo di documento NON è tra quelli speciali E l'importo non è stato inserito...
        if tipo_selezionato not in TIPI_SENZA_IMPORTO and not field.data:
            # ...allora solleva un errore di validazione.
            raise ValidationError('L\'importo è obbligatorio per Scontrini e Fatture.')
        
        # Se il tipo di documento È tra quelli speciali...
        if tipo_selezionato in TIPI_SENZA_IMPORTO:
            # ...svuotiamo il campo per sicurezza, anche se l'utente provasse a inviare un valore.
            field.data = None

# Aggiungi questa classe alla fine del file
class TemporaryMezzoForm(FlaskForm):
    """Form per creare mezzi/attrezzature temporanei"""
    tipologia = SelectField('Tipologia', 
                           choices=[('M', 'Autoveicolo'), ('A', 'Attrezzatura')], 
                           validators=[DataRequired()])
    targa_inventario = StringField('Targa/Inventario', validators=[DataRequired(), Length(max=50)])
    descrizione = StringField('Descrizione', validators=[Optional(), Length(max=200)])
    authorizing_entity = StringField('Ente Autorizzante', validators=[DataRequired(), Length(max=200)])
    authorization_date = DateField('Data Autorizzazione', format='%Y-%m-%d', validators=[DataRequired()])
    authorization_document = FileField('Documento Autorizzazione', 
                                     validators=[DataRequired(), 
                                               FileAllowed(['pdf', 'png', 'jpg', 'jpeg'])])
    submit = SubmitField('Salva Mezzo Temporaneo')
    
    def validate_targa_inventario(self, field):
        """Verifica che targa/inventario non esista nei mezzi permanenti"""
        if current_user.organizzazioni:
            existing = MezzoAttrezzatura.query.filter_by(
                targa_inventario=field.data,
                is_temporary=False,
                organizzazione_id=current_user.organizzazioni[0].id
            ).first()
            if existing:
                raise ValidationError('Questa targa/inventario esiste già nei mezzi permanenti.')