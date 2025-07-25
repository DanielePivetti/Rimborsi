from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from app.models.mezzo import TipologiaMezzo

class MezzoForm(FlaskForm):
    odv_id = SelectField('Organizzazione', 
                         validators=[DataRequired()], 
                         coerce=int)
    
    tipologia = SelectField('Tipologia', 
                           validators=[DataRequired()],
                           choices=[(tipo.name, tipo.value.capitalize()) for tipo in TipologiaMezzo],
                           coerce=lambda x: TipologiaMezzo[x] if x else None)
    
    targa_inventario = StringField('Targa o Numero Inventario', 
                                  validators=[DataRequired(), Length(max=50)])
    
    descrizione = TextAreaField('Descrizione', 
                              validators=[Optional(), Length(max=255)])
    
    submit = SubmitField('Salva')
