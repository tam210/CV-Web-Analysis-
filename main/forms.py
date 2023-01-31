from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, SubmitField, SelectField, TextAreaField
from wtforms_sqlalchemy.fields import  QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from main.models import Usuario, Categoria, Estado


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
        user = Usuario.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('El usuario ingresado ya existe.')

    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('El email ingresado ya existe.')

            
class LoginForm(FlaskForm):
    email = StringField('Email',  
                            validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')
    remember = BooleanField('Recuérdame')

class UploadFileForm(FlaskForm):
    file = FileField("Archivo")
    submit=SubmitField("Subir archivo")

def categoria_query():
    return Categoria.query

def state_query():
    return Estado.query


class CandidateForm(FlaskForm):
    name = StringField('Nombre del candidato', validators=[DataRequired()])
    category = QuerySelectField('Categoría', query_factory=categoria_query, allow_blank=False, get_label='name')
    state = QuerySelectField('Estado', query_factory=state_query, allow_blank=False, get_label='name')
    # state = StringField('Estado', validators=[DataRequired()])
    charge = TextAreaField('Descripción', validators=[DataRequired()])
    file = FileField("Archivo")
    submit = SubmitField('Enviar')


class CategoryForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    submit = SubmitField('Enviar')

    #El formato del nombre de la función para que automáticamente valide es: 'validate_[nombre de la variable a validar]'
    def validate_name(self, name):
        cat = Categoria.query.filter_by(name=name.data).first()
        if cat:
            raise ValidationError('La categoría ingresada ya existe.')

class StateForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    classification = StringField('Clasificación', validators=[DataRequired()])
    submit = SubmitField('Enviar')

    #El formato del nombre de la función para que automáticamente valide es: 'validate_[nombre de la variable a validar]'
    def validate_name(self, name):
        cat = Estado.query.filter_by(name=name.data).first()
        if cat:
            raise ValidationError('El estado ingresado ya existe.')


class OfferForm(FlaskForm):
    name = StringField('Titulo de la oferta', validators=[DataRequired()])
    category = QuerySelectField('Categoría', query_factory=categoria_query, allow_blank=False, get_label='name')
    state = QuerySelectField('Estado', query_factory=state_query, allow_blank=False, get_label='name')
    # state = StringField('Estado', validators=[DataRequired()])
    description = TextAreaField('Descripción', validators=[DataRequired()])
    submit = SubmitField('Enviar')
