from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SubmitField
from wtforms.validators import DataRequired
from app.models.odv import Odv

class AssociazioneUserOdvForm(FlaskForm):
    """Form per associare un compilatore a una o più organizzazioni."""
    organizzazioni = SelectMultipleField('Organizzazioni', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Salva Associazioni')
    
    def __init__(self, *args, **kwargs):
        super(AssociazioneUserOdvForm, self).__init__(*args, **kwargs)
        self.organizzazioni.choices = [(odv.id, odv.nome) for odv in Odv.query.order_by(Odv.nome).all()]
