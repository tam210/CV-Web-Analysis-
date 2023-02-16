from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SubmitField, TextAreaField
from wtforms_sqlalchemy.fields import  QuerySelectField
from wtforms.validators import DataRequired
from main.filters.utils import status_query, category_query

class OfferForm(FlaskForm):
    name = StringField('Titulo de la oferta', validators=[DataRequired()])
    category = QuerySelectField('Categoría', query_factory=category_query, allow_blank=False, get_label='name')
    status = QuerySelectField('Estado', query_factory=status_query, allow_blank=False, get_label='name')
    # state = StringField('Estado', validators=[DataRequired()])
    description = TextAreaField('Descripción', validators=[DataRequired()])
    submit = SubmitField('Enviar')
