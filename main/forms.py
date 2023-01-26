from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from main.models import Usuario


#Los formularios en HTML se harán con la sintaxis de flask:
#Formulario de registro
class RegistrationForm(FlaskForm):
    #DataRequired: Que se ingrese un valor
    #Length: Que tenga intervalo de cantidad de caracteres
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

class CandidateForm(FlaskForm):
    name = StringField('Nombre del candidato', validators=[DataRequired()])
    category = StringField('Categoría', validators=[DataRequired()])
    state = StringField('Estado', validators=[DataRequired()])
    charge = TextAreaField('Descripción', validators=[DataRequired()])
    file = FileField("Archivo")
    submit = SubmitField('Enviar')