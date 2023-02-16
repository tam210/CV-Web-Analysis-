from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from main.models import User, E_mail

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
