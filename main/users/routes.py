from flask import render_template, url_for, flash, redirect, request, Blueprint
from main.users.forms import RegistrationForm, LoginForm
from main import db, bcrypt
from main.models import User, E_mail, Type
from flask_login import login_user, current_user, logout_user, login_required
from main.main.utils import NAMETYPE_USER_USER

users_bp = Blueprint('users', __name__)

@users_bp.route("/register", methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('candidates.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_paswword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, 
                        password=hashed_paswword, 
                        
                        username=form.username.data)
        type_id = Type.query.filter_by(nametype=NAMETYPE_USER_USER).first()
        email = E_mail(name=form.email.data, extracted_y_n='N')
        #user.email = email.id
        email.user = user
        user.type = type_id.id
        db.session.add(email)
        db.session.add(user)
        try:        
            db.session.commit()
            a = User.query.all()
            asss = E_mail.query.all()
            print(a)
            print(asss)
            print("\n\n\n")
        except:
            print("\n\nError haciendo el commit\n\n")
        flash(f'Tu cuenta ha sido creada, {form.username.data}!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('candidates.home'))

    form = LoginForm()
    if form.validate_on_submit():
        email = E_mail.query.filter_by(name=form.email.data).first()
        if email:
            user = User.query.get(email.user_id)
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next') #args: diccionario
                return redirect(next_page) if next_page else redirect(url_for('candidates.home'))
            else:
                flash('Inicio de sesión fallido. Intente nuevamente')
        else:
            flash('El email ingresado no existe')
    return render_template('login.html', title='Login', form=form)

@users_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('candidates.home'))

@users_bp.route("/account")
@login_required
def account():
    #image_file=url_for('static', filename='files/'+current_user.image_file)
    print(current_user.email)
    return render_template('account.html', title='Account')

@users_bp.route("/users", methods=['GET', 'POST'])
def users():
    users = User.query.all()
    return render_template('users.html', title='Usuarios', 
                            users=users, legend='Usuarios existentes')
