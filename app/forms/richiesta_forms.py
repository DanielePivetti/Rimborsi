from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, DateField, FloatField, IntegerField, SubmitField, HiddenField, FieldList, FormField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from app.models.spesa import TipoSpesa
from app.models.documento_spesa import TipoDocumento

class AggiungiSpesaForm(FlaskForm):
    """Form vuoto per CSRF protection"""
    pass

class RichiestaBaseForm(FlaskForm):
    """Form base per la creazione e modifica di una richiesta di rimborso"""
    odv_id = SelectField('Organizzazione', coerce=int, validators=[DataRequired()])
    evento_id = SelectField('Evento', coerce=int, validators=[DataRequired()])
    attivita_svolta = TextAreaField('Attività Svolta', validators=[DataRequired(), Length(max=1000)], 
                                  description="Descrivi in dettaglio l'attività svolta")
    data_inizio_attivita = DateField('Data Inizio Attività', format='%Y-%m-%d', validators=[DataRequired()])
    data_fine_attivita = DateField('Data Fine Attività', format='%Y-%m-%d', validators=[DataRequired()])
    volontari_impiegati = IntegerField('Volontari Impiegati', validators=[DataRequired(), NumberRange(min=1)],
                                     description="Numero di volontari impiegati nell'attività")
    note_richiedente = TextAreaField('Note', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Salva')

class SpesaBaseForm(FlaskForm):
    """Form base per tutte le spese"""
    tipo = SelectField('Tipo di spesa', validators=[DataRequired()], 
                      choices=[(tipo.value, f"{tipo.value} - {tipo.name.capitalize()}") for tipo in TipoSpesa])
    data_spesa = DateField('Data spesa', format='%Y-%m-%d', validators=[DataRequired()])
    importo_richiesto = FloatField('Importo richiesto', validators=[DataRequired(), NumberRange(min=0.01)])
    note = TextAreaField('Note', validators=[Optional(), Length(max=500)])
    
class SpesaCarburanteForm(SpesaBaseForm):
    """Form per spese di carburante (01)"""
    impiego_mezzo_id = SelectField('Impiego mezzo', coerce=int, validators=[DataRequired()])
    tipo_carburante = SelectField('Tipo carburante', validators=[DataRequired()],
                                choices=[
                                    ('benzina', 'Benzina'),
                                    ('diesel', 'Diesel'),
                                    ('gpl', 'GPL'),
                                    ('metano', 'Metano'),
                                    ('elettrico', 'Ricarica elettrica')
                                ])
    litri = FloatField('Litri', validators=[Optional(), NumberRange(min=0.1)])
    submit = SubmitField('Salva')

class SpesaPedaggiForm(SpesaBaseForm):
    """Form per spese di pedaggi (03)"""
    impiego_mezzo_id = SelectField('Impiego mezzo', coerce=int, validators=[DataRequired()])
    tratta = StringField('Tratta', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Salva')

class SpesaRipristinoForm(SpesaBaseForm):
    """Form per spese di ripristino (04)"""
    impiego_mezzo_id = SelectField('Impiego mezzo', coerce=int, validators=[DataRequired()])
    descrizione_intervento = TextAreaField('Descrizione intervento', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Salva')

class SpesaVittoForm(SpesaBaseForm):
    """Form per spese di vitto (02)"""
    numero_pasti = IntegerField('Numero pasti', validators=[DataRequired(), NumberRange(min=1)], default=1)
    submit = SubmitField('Salva')

class SpesaParcheggioForm(SpesaBaseForm):
    """Form per spese di parcheggio (05)"""
    indirizzo = StringField('Indirizzo', validators=[Optional(), Length(max=255)])
    durata_ore = FloatField('Durata (ore)', validators=[Optional(), NumberRange(min=0.5)])
    submit = SubmitField('Salva')

class SpesaAltroForm(SpesaBaseForm):
    """Form per altre spese (06)"""
    descrizione_dettagliata = TextAreaField('Descrizione dettagliata', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Salva')

class DocumentoSpesaForm(FlaskForm):
    """Form per i documenti di spesa"""
    tipo = SelectField('Tipo documento', validators=[DataRequired()],
                      choices=[(tipo.name, f"{tipo.value} - {tipo.get_display_name()}") for tipo in TipoDocumento])
    numero = StringField('Numero documento', validators=[Optional(), Length(max=100)])
    data = DateField('Data emissione', format='%Y-%m-%d', validators=[DataRequired()])
    descrizione = TextAreaField('Descrizione', validators=[Optional(), Length(max=500)])
    file = FileField('File allegato', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Solo immagini o PDF sono permessi.')
    ])
    submit = SubmitField('Salva')

class SpesaDocumentiForm(FlaskForm):
    """Form combinato per la spesa e i suoi documenti"""
    # Campi comuni della spesa
    tipo_spesa = SelectField('Tipo di spesa', validators=[DataRequired()], 
                      choices=[(tipo.value, f"{tipo.value} - {tipo.name.capitalize()}") for tipo in TipoSpesa])
    data_spesa = DateField('Data spesa', format='%Y-%m-%d', validators=[DataRequired()])
    importo_richiesto = FloatField('Importo richiesto', validators=[DataRequired(), NumberRange(min=0.01)])
    note = TextAreaField('Note spesa', validators=[Optional(), Length(max=500)])
    
    # Campi specifici per SpesaCarburante
    impiego_mezzo_id = SelectField('Impiego mezzo', coerce=int, validators=[Optional()])
    tipo_carburante = SelectField('Tipo carburante', validators=[Optional()],
                                choices=[
                                    ('', 'Seleziona...'),
                                    ('benzina', 'Benzina'),
                                    ('diesel', 'Diesel'),
                                    ('gpl', 'GPL'),
                                    ('metano', 'Metano'),
                                    ('elettrico', 'Ricarica elettrica')
                                ])
    litri = FloatField('Litri', validators=[Optional(), NumberRange(min=0.1)])
    
    # Campi per SpesaPedaggi
    tratta = StringField('Tratta', validators=[Optional(), Length(max=255)])
    
    # Campi per SpesaRipristino
    descrizione_intervento = TextAreaField('Descrizione intervento', validators=[Optional(), Length(max=500)])
    
    # Campi per SpesaVitto
    numero_pasti = IntegerField('Numero pasti', validators=[Optional(), NumberRange(min=1)], default=1)
    
    # Campi per SpesaParcheggio
    indirizzo = StringField('Indirizzo', validators=[Optional(), Length(max=255)])
    durata_ore = FloatField('Durata (ore)', validators=[Optional(), NumberRange(min=0.5)])
    
    # Campi per SpesaAltro
    descrizione_dettagliata = TextAreaField('Descrizione dettagliata', validators=[Optional(), Length(max=500)])
    
    # Campi per il documento principale (A, B o C)
    doc_tipo = SelectField('Tipo documento', validators=[DataRequired()],
                       choices=[
                           (TipoDocumento.SCONTRINO.name, f"{TipoDocumento.SCONTRINO.value} - Scontrino"),
                           (TipoDocumento.QUIETANZA.name, f"{TipoDocumento.QUIETANZA.value} - Quietanza"),
                           (TipoDocumento.FATTURA.name, f"{TipoDocumento.FATTURA.value} - Fattura")
                       ])
    doc_numero = StringField('Numero documento', validators=[Optional(), Length(max=100)])
    doc_data = DateField('Data emissione', format='%Y-%m-%d', validators=[DataRequired()])
    doc_descrizione = TextAreaField('Descrizione documento', validators=[Optional(), Length(max=500)])
    doc_file = FileField('File documento', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Solo immagini o PDF sono permessi.')
    ])
    
    # Campi per documento aggiuntivo attestazione danno (E) - per tipo 04 Ripristino
    attestazione_danno_file = FileField('Attestazione danno', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Solo immagini o PDF sono permessi.')
    ])
    
    # Campi per documento aggiuntivo autorizzazione (D) - per tipo 05 Parcheggio e 06 Altro
    autorizzazione_file = FileField('Autorizzazione', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Solo immagini o PDF sono permessi.')
    ])
    
    # Campo per i documenti multipli
    documenti = FieldList(FormField(DocumentoSpesaForm), min_entries=0)
    
    submit = SubmitField('Salva')

# Nuovi form per l'interfaccia a tabs
class CarburanteForm(FlaskForm):
    """Form per spese di carburante (01) nell'interfaccia a tab"""
    data_spesa = DateField('Data spesa', format='%Y-%m-%d', validators=[DataRequired()])
    importo_richiesto = FloatField('Importo richiesto (€)', validators=[DataRequired(), NumberRange(min=0.01)])
    tipo_carburante = SelectField('Tipo carburante', validators=[DataRequired()],
                                choices=[
                                    ('benzina', 'Benzina'),
                                    ('diesel', 'Diesel'),
                                    ('gpl', 'GPL'),
                                    ('metano', 'Metano'),
                                    ('elettrico', 'Ricarica elettrica')
                                ])
    litri = FloatField('Litri', validators=[Optional(), NumberRange(min=0.1)])
    note = TextAreaField('Note', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Salva')

class PastoForm(FlaskForm):
    """Form per spese di vitto (02) nell'interfaccia a tab"""
    data_spesa = DateField('Data spesa', format='%Y-%m-%d', validators=[DataRequired()])
    importo_richiesto = FloatField('Importo richiesto (€)', validators=[DataRequired(), NumberRange(min=0.01)])
    numero_pasti = IntegerField('Numero pasti', validators=[DataRequired(), NumberRange(min=1)], default=1)
    note = TextAreaField('Note', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Salva')

class PedaggioForm(FlaskForm):
    """Form per spese di pedaggi (03) nell'interfaccia a tab"""
    data_spesa = DateField('Data spesa', format='%Y-%m-%d', validators=[DataRequired()])
    importo_richiesto = FloatField('Importo richiesto (€)', validators=[DataRequired(), NumberRange(min=0.01)])
    tratta = StringField('Tratta', validators=[DataRequired(), Length(max=255)])
    note = TextAreaField('Note', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Salva')

class ManutenzioneForm(FlaskForm):
    """Form per spese di ripristino (04) nell'interfaccia a tab"""
    data_spesa = DateField('Data spesa', format='%Y-%m-%d', validators=[DataRequired()])
    importo_richiesto = FloatField('Importo richiesto (€)', validators=[DataRequired(), NumberRange(min=0.01)])
    descrizione_intervento = TextAreaField('Descrizione intervento', validators=[DataRequired(), Length(max=500)])
    note = TextAreaField('Note', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Salva')

class ParcheggioForm(FlaskForm):
    """Form per spese di parcheggio (05) nell'interfaccia a tab"""
    data_spesa = DateField('Data spesa', format='%Y-%m-%d', validators=[DataRequired()])
    importo_richiesto = FloatField('Importo richiesto (€)', validators=[DataRequired(), NumberRange(min=0.01)])
    indirizzo = StringField('Destinazione', validators=[DataRequired(), Length(max=255)])
    durata_ore = FloatField('Durata (ore)', validators=[Optional(), NumberRange(min=0.5)])
    note = TextAreaField('Note', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Salva')

class AltraSpesaForm(FlaskForm):
    """Form per altre spese (06) nell'interfaccia a tab"""
    data_spesa = DateField('Data spesa', format='%Y-%m-%d', validators=[DataRequired()])
    importo_richiesto = FloatField('Importo richiesto (€)', validators=[DataRequired(), NumberRange(min=0.01)])
    descrizione_dettagliata = TextAreaField('Descrizione dettagliata', validators=[DataRequired(), Length(max=500)])
    note = TextAreaField('Note', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Salva')
