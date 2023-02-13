from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, SubmitField, SelectField, TextAreaField
from wtforms_sqlalchemy.fields import  QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from main.models import User, Category, Status, Phone, E_mail, Candidate

#Los formularios en HTML se harán con la sintaxis de flask:
#Formulario de registro
class RegistrationForm(FlaskForm):
    name = StringField('Nombre', 
                            validators=[DataRequired()])
    username = StringField('Username',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',  
                            validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar contraseña', 
                                        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('El usuario ingresado ya existe.')

    def validate_email(self, email):
        em = E_mail.query.filter_by(name=email.data).first()
        if em:
            raise ValidationError('El email ingresado ya existe.')


class LoginForm(FlaskForm):
    email = StringField('Email',  
                            validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')
    remember = BooleanField('Recuérdame')

class UploadFileForm(FlaskForm):
    file = FileField("Archivo PDF/JPG")
    submit=SubmitField("Subir archivo")

def category_query():
    
    return Category.query

def status_query():
    return Status.query


class CategoriesStatusesForm(FlaskForm):
    category = QuerySelectField('Filtrar por categoría', query_factory=category_query, allow_blank=True, get_label='name')
    status = QuerySelectField('Filtrar por estado', query_factory=status_query, allow_blank=True, get_label='name')
    submit = SubmitField('Enviar')

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


class CategoryForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    submit = SubmitField('Enviar')

    #El formato del nombre de la función para que automáticamente valide es: 'validate_[nombre de la variable a validar]'
    def validate_name(self, name):
        cat = Category.query.filter_by(name=name.data).first()
        if cat:
            raise ValidationError('La categoría ingresada ya existe.')

class StateForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    classification = StringField('Clasificación', validators=[DataRequired()])
    submit = SubmitField('Enviar')

    #El formato del nombre de la función para que automáticamente valide es: 'validate_[nombre de la variable a validar]'
    def validate_name(self, name):
        cat = Status.query.filter_by(name=name.data).first()
        if cat:
            raise ValidationError('El estado ingresado ya existe.')


class OfferForm(FlaskForm):
    name = StringField('Titulo de la oferta', validators=[DataRequired()])
    category = QuerySelectField('Categoría', query_factory=category_query, allow_blank=False, get_label='name')
    status = QuerySelectField('Estado', query_factory=status_query, allow_blank=False, get_label='name')
    # state = StringField('Estado', validators=[DataRequired()])
    description = TextAreaField('Descripción', validators=[DataRequired()])
    submit = SubmitField('Enviar')
