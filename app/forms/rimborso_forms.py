from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class RimborsoForm(FlaskForm):
    descrizione = StringField('Descrizione', validators=[DataRequired(), Length(max=200)])
    importo = FloatField('Importo (€)', validators=[DataRequired(), NumberRange(min=0.01)])
    data_spesa = DateField('Data Spesa', validators=[DataRequired()], format='%Y-%m-%d')
    categoria = SelectField('Categoria', choices=[
        ('trasporto', 'Trasporto'),
        ('alloggio', 'Alloggio'),
        ('pasti', 'Pasti'),
        ('formazione', 'Formazione'),
        ('materiali', 'Materiali'),
        ('altro', 'Altro')
    ])
    note = TextAreaField('Note', validators=[Length(max=500)])
    file_allegato = FileField('Allegato (Ricevuta/Fattura)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Sono ammessi solo file immagine e PDF.')
    ])
    submit = SubmitField('Invia Richiesta')
