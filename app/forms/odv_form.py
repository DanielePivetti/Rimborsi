from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional, ValidationError
import re

class OdvForm(FlaskForm):
    nome = StringField('Nome Organizzazione', 
                      validators=[DataRequired(), Length(min=3, max=255)])
    acronimo = StringField('Acronimo', 
                          validators=[Optional(), Length(max=50)])
    codice_interno = StringField('Codice Interno', 
                               validators=[Optional(), Length(max=100)])
    provincia = StringField('Provincia', 
                          validators=[DataRequired(), Length(min=2, max=100)])
    comune = StringField('Comune', 
                        validators=[DataRequired(), Length(min=2, max=100)])
    indirizzo = StringField('Indirizzo', 
                           validators=[DataRequired(), Length(min=5, max=255)])
    pec = StringField('PEC', 
                     validators=[DataRequired(), Email(), Length(max=255)])
    recapito_telefonico = StringField('Recapito Telefonico', 
                                     validators=[DataRequired(), Length(max=50)])
    legale_rappresentante = StringField('Legale Rappresentante', 
                                      validators=[DataRequired(), Length(min=5, max=255)])
    iban = StringField('IBAN', 
                      validators=[DataRequired(), Length(min=15, max=34)])
    
    submit = SubmitField('Salva')
    
    def validate_iban(self, field):
        # Verifica che l'IBAN sia nel formato corretto
        if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}$', field.data):
            raise ValidationError('Formato IBAN non valido.')
