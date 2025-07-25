from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from datetime import date
from app.models.evento import Evento

class EventoForm(FlaskForm):
    tipo = SelectField('Tipo Evento', choices=Evento.get_tipi_evento(), validators=[DataRequired()])
    nome = StringField('Nome Evento', validators=[DataRequired(), Length(min=3, max=255)])
    numero_attivazione = StringField('Numero Attivazione', validators=[DataRequired(), Length(max=50)])
    data_attivazione = DateField('Data Attivazione', validators=[DataRequired()], format='%Y-%m-%d')
    luogo = TextAreaField('Luogo', validators=[DataRequired()])
    data_inizio = DateField('Data Inizio', validators=[DataRequired()], format='%Y-%m-%d')
    data_fine = DateField('Data Fine', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Salva')
    
    def validate_data_fine(self, field):
        if field.data < self.data_inizio.data:
            raise ValidationError('La data di fine deve essere successiva alla data di inizio')
    
    def validate_data_inizio(self, field):
        if field.data < self.data_attivazione.data:
            raise ValidationError('La data di inizio deve essere successiva o uguale alla data di attivazione')
