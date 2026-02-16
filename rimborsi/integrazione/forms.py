from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class IntegrazioneRequestForm(FlaskForm):
    """
    Form per gestire le richieste di integrazione.
    """
    motivazione = TextAreaField('Motivazione della richiesta',
                 validators=[DataRequired(message="La motivazione è obbligatoria."),
                        Length(min=10, max=500, message="La motivazione deve essere compresa tra 10 e 500 caratteri.")
                    ]
                )
    
    submit = SubmitField('Invia Richiesta di Integrazione')
