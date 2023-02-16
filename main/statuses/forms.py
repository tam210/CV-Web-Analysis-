from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from main.models import Status

class StateForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    classification = StringField('Clasificación', validators=[DataRequired()])
    submit = SubmitField('Enviar')

    #El formato del nombre de la función para que automáticamente valide es: 'validate_[nombre de la variable a validar]'
    def validate_name(self, name):
        cat = Status.query.filter_by(name=name.data).first()
        if cat:
            raise ValidationError('El estado ingresado ya existe.')

