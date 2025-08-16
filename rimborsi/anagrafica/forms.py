from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from rimborsi.models import Organizzazione, MezzoAttrezzatura

class OrganizzazioneForm(FlaskForm):
    nome = StringField('Nome Organizzazione', validators=[DataRequired(), Length(max=150)])
    acronimo = StringField('Acronimo', validators=[Optional(), Length(max=20)])
    codice_interno = StringField('Codice Interno', validators=[Optional(), Length(max=20)])
    indirizzo = StringField('Indirizzo', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Salva')
    
    # AGGIUNTA: Costruttore per accettare l'ID durante la modifica
    def __init__(self, *args, **kwargs):
        super(OrganizzazioneForm, self).__init__(*args, **kwargs)
        self.id_organizzazione = kwargs.get('id_organizzazione')

    def validate_codice_interno(self, field):
        if field.data:
            org = Organizzazione.query.filter_by(codice_interno=field.data).first()
            if org and org.id != self.id_organizzazione:
                raise ValidationError('Questo codice interno è già utilizzato.')

class MezzoAttrezzaturaForm(FlaskForm):
    tipologia = SelectField('Tipologia', choices=[
        ('M', 'Autoveicolo'), ('A', 'Attrezzatura')
    ], validators=[DataRequired()])
    targa_inventario = StringField('Targa/Numero Inventario', validators=[DataRequired(), Length(max=50)])
    descrizione = TextAreaField('Descrizione', validators=[Optional(), Length(max=200)])
    organizzazione_id = HiddenField()
    submit = SubmitField('Salva')
    
    # AGGIUNTA: Costruttore per accettare l'ID durante la modifica
    def __init__(self, *args, **kwargs):
        super(MezzoAttrezzaturaForm, self).__init__(*args, **kwargs)
        self.id_mezzo = kwargs.get('id_mezzo')

    def validate_targa_inventario(self, field):
        mezzo = MezzoAttrezzatura.query.filter_by(targa_inventario=field.data).first()
        if mezzo and mezzo.id != self.id_mezzo:
            raise ValidationError('Questa targa/numero inventario è già utilizzato.')