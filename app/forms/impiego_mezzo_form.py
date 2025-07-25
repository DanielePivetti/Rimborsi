from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from app.models.mezzo import Mezzo

class ImpiegoMezzoForm(FlaskForm):
    mezzo_id = SelectField('Mezzo', coerce=int, validators=[DataRequired()])
    evento_id = SelectField('Evento', coerce=int, validators=[DataRequired()])
    data_inizio = DateTimeField('Data e ora inizio', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    data_fine = DateTimeField('Data e ora fine', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    km_partenza = IntegerField('Km alla partenza', validators=[DataRequired(), NumberRange(min=0)])
    km_arrivo = IntegerField('Km all\'arrivo', validators=[DataRequired(), NumberRange(min=0)])
    note = TextAreaField('Note', validators=[Optional()])
    submit = SubmitField('Salva')
    
    def validate_km_arrivo(self, field):
        """Verifica che i km all'arrivo siano maggiori o uguali ai km alla partenza"""
        if field.data < self.km_partenza.data:
            raise ValueError('I km all\'arrivo devono essere maggiori o uguali ai km alla partenza')
