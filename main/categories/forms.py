from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from main.models import Category

class CategoryForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    submit = SubmitField('Enviar')

    #El formato del nombre de la función para que automáticamente valide es: 'validate_[nombre de la variable a validar]'
    def validate_name(self, name):
        cat = Category.query.filter_by(name=name.data).first()
        if cat:
            raise ValidationError('La categoría ingresada ya existe.')
