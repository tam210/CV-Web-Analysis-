from flask import render_template, url_for, flash, redirect, request, abort
from main.forms import RegistrationForm, LoginForm, UploadFileForm, CandidateForm
from werkzeug.utils import secure_filename
import os
from main.analysis import getRessumeDF
from main import app, db, bcrypt
from main.models import Candidato, Categoria, Usuario, candidato_usuario, categoria_usuario

from flask_login import login_user, current_user, logout_user, login_required

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])

def home():
    """
    page: lo que se quiere obtener
    1: el valor por DEFAULT
    type: el tipo que debe tener la página, así se evitan strings u otro
    """
    page = request.args.get('page', 1, type=int) #default=1
    #candidatos = Candidato.query.all()
    candidatos = Candidato.query.paginate(page=page, per_page=5)
    return render_template('home.html',candidatos=candidatos)

@app.route("/ressume", methods=['GET', 'POST'])
def ressume():
    return render_template('ressume.html')

@app.route("/get_analysis", methods=['GET', 'POST'])
def get_analysis():
    form=UploadFileForm()
    # user_form = UserAdd()
    if form.validate_on_submit():
        ff = form.file.data.filename
        return redirect(url_for('analysis', file=ff))
    return render_template('get_analysis.html',title='get_analysis',form=form)



@app.route("/analysis/<string:file>", methods=['GET', 'POST'])
def analysis(file):
    # file = form.file.data
    # ff = file.filename
    # resumen = getRessumeDF(ff)
    resumen = getRessumeDF(file)
    plot_img = url_for('static', filename='files/'+'resume_results.png')

    return render_template('analysis.html', tables=[resumen.to_html(classes='data')], titles=resumen.columns.values, file=file, plot_img=plot_img)



@app.route("/register", methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_paswword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Usuario(nombre=form.name.data, clave=hashed_paswword, email=form.email.data, username=form.username.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Tu cuenta ha sido creada, {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.clave, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next') #args: diccionario
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Inicio de sesión fallido.')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():
    #image_file=url_for('static', filename='files/'+current_user.image_file)
    return render_template('account.html', title='Account')


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = CandidateForm()
    if form.validate_on_submit():
        cand = Candidato(nombre=form.name.data, categoria=form.category.data, estado=form.state.data, image_file=form.file.data, cargo_postulante=form.charge.data)
        current_user.candidatos.append(cand)
        db.session.add(cand)
        db.session.add(current_user)
        db.session.commit()
        flash('Candidato registrado', 'success')
        return redirect(url_for('home'))
    # image_file=url_for('static', filename='files/'+current_user.image_file)
    return render_template('create_post.html', title='New Post', 
                            form=form, legend='Registrar candidato')


@app.route("/post/<int:candidato_id>", methods=['GET', 'POST'])
def candidato(candidato_id):
    #dame el candidato y si no existe, retorna 404 (no existe pagina)
    candidato = Candidato.query.get_or_404(candidato_id)
    image_file=url_for('static', filename='files/'+candidato.image_file)
    return render_template('candidato.html', title=candidato_id, candidato=candidato, image_file=image_file)


@app.route("/post/<int:candidato_id>/update", methods=['GET', 'POST'])
@login_required
def update_candidato(candidato_id):
    #dame el candidato y si no existe, retorna 404 (no existe pagina)
    candidato = Candidato.query.get_or_404(candidato_id)
    #si el registro no fue hecho por el usuario logueado
    if current_user not in candidato.usuarios:
        abort(403)
    form = CandidateForm() #creo nuevo formulario

    if form.validate_on_submit():
        candidato.nombre = form.name.data 
        candidato.categoria = form.category.data
        candidato.estado = form.state.data
        candidato.cargo_postulante = form.charge.data
        candidato.image_file = form.file.data
        db.session.commit()
        flash('Información del candidato actualizada', 'success')
        return redirect(url_for('candidato', candidato_id=candidato.id))
    #cuando se carga la pagina, se carga con info ya cargada del sistema.
    #cuando el sistema quiere cargar la pagina, lo pide a traves del
    # 'GET', por lo que cuando se quiera cargar la pagina debemos
    # definir la info predeterminada a mostrar
    elif request.method == 'GET': #cuando cargamos/redirreciona la pagina
        form.name.data = candidato.nombre
        form.category.data = candidato.categoria
        form.state.data = candidato.estado
        form.charge.data = candidato.cargo_postulante
        form.file.data = candidato.image_file
    
    return render_template('create_post.html', title='Actualizar candidato',
                             form=form, legend='Actualizar candidato')

@app.route("/post/<int:candidato_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_candidato(candidato_id):
    #dame el candidato y si no existe, retorna 404 (no existe pagina)
    candidato = Candidato.query.get_or_404(candidato_id)
    #si el registro no fue hecho por el usuario logueado
    if current_user not in candidato.usuarios:
        abort(403)
    db.session.delete(candidato)
    db.session.commit()
    flash('Usuario eliminado', 'success')
    return redirect(url_for('home'))