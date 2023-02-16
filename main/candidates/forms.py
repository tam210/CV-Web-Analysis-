from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, SubmitField, TextAreaField
from wtforms_sqlalchemy.fields import  QuerySelectField
from wtforms.validators import DataRequired, ValidationError
from main.models import Phone, E_mail, Category, Status



def category_query():
    return Category.query

def status_query():
    return Status.query

class CandidateForm(FlaskForm):
    name = StringField('Nombre del candidato', validators=[DataRequired()])
    category = QuerySelectField('Categoría', query_factory=category_query, allow_blank=False, get_label='name')
    # state = StringField('Estado', validators=[DataRequired()])
    email = StringField('Email')
    phone = StringField('Teléfono')
    description = TextAreaField('Descripción', validators=[DataRequired()])
    description = TextAreaField('Descripción', validators=[DataRequired()])
    #file = FileField("Archivo")
    submit = SubmitField('Enviar')
    
    def validate_phone(self, phone):
        # print(Email.query.all())
        em = Phone.query.filter_by(name=phone.data).first()
        if em:
            raise ValidationError('El teléfono ingresado ya existe.')

    
    def validate_email(self, email):
        em = E_mail.query.filter_by(name=email.data).first()
        if em:
            raise ValidationError('El email ingresado ya existe.')

    # def validate_file(self, file):
    #     candidate = Candidate.query.filter_by(file=file.data).first()
    #     if candidate: #si existe un candidato con ese archivo ya almacenado
    #         raise ValidationError('El archivo ingresado ya existe.')


class UploadFileForm(FlaskForm):
    file = FileField("Archivo PDF/JPG")
    submit=SubmitField("Subir archivo")
