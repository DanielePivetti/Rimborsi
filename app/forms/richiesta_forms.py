from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, DateField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from app.models.spesa import TipoSpesa
from app.models.giustificativo import TipoGiustificativo

class RichiestaBaseForm(FlaskForm):
    """Form base per la creazione e modifica di una richiesta di rimborso"""
    odv_id = SelectField('Organizzazione', coerce=int, validators=[DataRequired()])
    evento_id = SelectField('Evento', coerce=int, validators=[DataRequired()])
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

class GiustificativoForm(FlaskForm):
    """Form per i giustificativi"""
    tipo = SelectField('Tipo documento', validators=[DataRequired()],
                      choices=[(tipo.value, tipo.name.capitalize()) for tipo in TipoGiustificativo])
    numero = StringField('Numero documento', validators=[Optional(), Length(max=100)])
    data_emissione = DateField('Data emissione', format='%Y-%m-%d', validators=[DataRequired()])
    emesso_da = StringField('Emesso da', validators=[DataRequired(), Length(max=255)])
    importo = FloatField('Importo', validators=[DataRequired(), NumberRange(min=0.01)])
    file = FileField('File allegato', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Solo immagini o PDF sono permessi.')
    ])
    submit = SubmitField('Salva')
