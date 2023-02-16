from flask_wtf import FlaskForm
from wtforms import SubmitField, SubmitField
from wtforms_sqlalchemy.fields import  QuerySelectField
from main.filters.utils import status_query, category_query

class CategoriesStatusesForm(FlaskForm):
    category = QuerySelectField('Filtrar por categoría', query_factory=category_query, allow_blank=True, get_label='name')
    status = QuerySelectField('Filtrar por estado', query_factory=status_query, allow_blank=True, get_label='name')
    submit = SubmitField('Enviar')
