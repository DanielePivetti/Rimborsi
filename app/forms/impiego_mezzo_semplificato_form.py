from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length

class ImpiegoMezzoSemplificatoForm(FlaskForm):
    """Form semplificato per la registrazione dell'impiego di un mezzo nel processo multi-step"""
    mezzo_id = SelectField('Mezzo', coerce=int, validators=[DataRequired()])
    data_utilizzo = DateField('Data Utilizzo', validators=[DataRequired()], format='%Y-%m-%d')
    km_percorsi = IntegerField('KM Percorsi', validators=[DataRequired(), NumberRange(min=1, message="Il valore deve essere maggiore di zero")])
    note = TextAreaField('Note', validators=[Optional()], render_kw={"rows": 3})
