from flask import render_template, url_for, flash, redirect, request, abort
from main.forms import RegistrationForm, LoginForm, UploadFileForm, CandidateForm, CategoryForm, StateForm, OfferForm
from werkzeug.utils import secure_filename
import os
from main.analysis import obtenerDF_Email
from main import app, db, bcrypt
from main.models import Candidate, Category, User, Status, Offer, E_mail, Phone, inicialize
from sqlalchemy.exc import SQLAlchemyError


from flask_login import login_user, current_user, logout_user, login_required

NAMETYPE_USER_USER = 'Usuario'
NAMETYPE_USER_CANDIDATE = 'Candidato'

CLASSIFICATION_STATUS_OFFER = 'Trabajo'
CLASSIFICATION_STATUS_CANDIDATE = 'Candidato'




@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
@app.route("/candidates", methods=['GET', 'POST'])
def home():
    inicialize()
    """
    page: lo que se quiere obtener
    1: el valor por DEFAULT
    type: el tipo que debe tener la página, así se evitan strings u otro
    """
    page = request.args.get('page', 1, type=int) #default=1
    #Candidates = Candidate.query.all()
    candidates = Candidate.query.paginate(page=page, per_page=5)
    return render_template('home.html',candidates=candidates)

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
    return render_template('get_analysis.html',title='Obtener análisis',form=form)



@app.route("/analysis/<string:file>", methods=['GET', 'POST'])
def analysis(file):
    # file = form.file.data
    # ff = file.filename
    # resumen = getRessumeDF(file)
    ressume, email, phone = obtenerDF_Email(file)
    plot_img = url_for('static', filename='files/'+'resume_results.png')

    return render_template('analysis.html', tables=[ressume.to_html(classes='data')], titles=ressume.columns.values, file=file, plot_img=plot_img, email=email, phone=phone)



@app.route("/register", methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_paswword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, 
                        password=hashed_paswword, 
                        email=form.email.data, 
                        username=form.username.data, type=NAMETYPE_USER_USER)
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
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
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


@app.route("/candidates/new", methods=['GET', 'POST'])
@login_required
def create_candidate():
    form = CandidateForm()
    form.category.query = Category.query.filter(Category.id >=0)
    form.status.query = Status.query.filter(Status.classification==CLASSIFICATION_STATUS_CANDIDATE)
    if form.validate_on_submit():
        try:
            ff = form.file.data
            cand = Candidate(name=form.name.data,
                                category_id=form.category.data.id, 
                                status_id=form.status.data.id, 
                                file=form.file.data, 
                                description=form.description.data, type=NAMETYPE_USER_CANDIDATE)
            #Si ingresó un email en el formulario crea un email nuevo
            current_user.candidates.append(cand)
            if form.email.data:
                print("Email agregado por formulario")
                em = E_mail(name=form.email.data, candidate_id=cand.id)
                print("\n\nEMAIL A INGRESAR",em)
                db.session.add(em)
            #Si ingresó un teléfono en el formulario crea un email nuevo
            if form.phone.data:
                print("Telefono agregado por formulario")
                ph = Phone(name=form.phone.data, candidate_id=cand.id)
                db.session.add(ph)
            #Si ingresó un email en el formulario crea un email nuevo
            #if cand.file: #si tiene imagen
            if form.file.data: #si tiene imagen
                _, email, phone = obtenerDF_Email(ff)
                if email: #si ingresó email
                    #si no existe un email con ese nombre, NO ESTÁ REGISTRADO
                    if not E_mail.query.filter_by(name=email).first():
                        print("-------NO ESTÁ REGISTRADO EM-----------")
                        em2 = E_mail(name = email, candidate_id=cand.id)
                        db.session.add(em2)
                        print("Email agregado por cv")
                    else:
                        print("-------SI ESTÁ REGISTRADO EM-----------")
                if phone:
                    if not Phone.query.filter_by(name=phone).first():
                        print("-------NO ESTÁ REGISTRADO-----------")
                        ph2 = Phone(name = phone, candidate_id=cand.id)
                        db.session.add(ph2)
                        print("Telefono agregado por cv")
            db.session.add(cand)
            db.session.add(current_user)
            print("RESUMEN:")
            print(cand)
            print(cand.phones.count())
            print(cand.emails.count())
            db.session.commit()
            flash('Candidato registrado', 'success')
            return redirect(url_for('home'))

        except SQLAlchemyError as e:
            print("ERROR-------------X-X-X-X-X")
            error = str(e.__dict__['orig'])
        return error
        
    return render_template('new_candidate.html', title='Nuevo Candidato', 
                            form=form, legend='Registrar Candidato')


@app.route("/candidates/<int:candidate_id>", methods=['GET', 'POST'])
def candidate(candidate_id):
    #dame el Candidate y si no existe, retorna 404 (no existe pagina)
    
    candidate = Candidate.query.get_or_404(candidate_id)
    image_file=url_for('static', filename='files/'+candidate.file)
    print("XXXXXXXXXXXXXXXXXXXXXXX")
    print(candidate.phones)
    print("XXXXXXXXXXXXXXXXXXXXXXX")
    return render_template('candidate.html', title=candidate_id, candidate=candidate, image_file=image_file)


@app.route("/candidates/<int:candidate_id>/update", methods=['GET', 'POST'])
@login_required
def update_candidate(candidate_id):
    #dame el Candidate y si no existe, retorna 404 (no existe pagina)
    candidate = Candidate.query.get_or_404(candidate_id)
    #si el registro no fue hecho por el usuario logueado
    if current_user not in candidate.users:
        abort(403)
    form = CandidateForm() #creo nuevo formulario
        
    form.category.query = Category.query.filter(Category.id >=0)
    form.status.query = Status.query.filter(Status.classification==CLASSIFICATION_STATUS_CANDIDATE)

    if form.validate_on_submit():
        candidate.name = form.name.data 
        # candidate.category = form.category.data
        # candidate.status = form.status.data

        
        # candidate.emails = form.email.data.id
        # candidate.phones = form.phone.data
        candidate.description = form.description.data
        candidate.file = form.file.data
        if form.email.data:
            if form.email.data not in candidate.emails:
                em = E_mail(name=form.email.data, candidate_id=candidate.id)
                db.session.add(em)
            else:
                print ("---------------------NNN----")
        if form.phone.data:
            if form.phone.data not in candidate.phones:
                ph = Phone(name=form.phone.data, candidate_id=candidate.id)
                db.session.add(ph)
            else:
                print ("---------------------NNN----")
        db.session.commit()
        #print(candidate)
        flash('Información del candidato actualizada', 'success')
        return redirect(url_for('candidate', candidate_id=candidate.id))
    #cuando se carga la pagina, se carga con info ya cargada del sistema.
    #cuando el sistema quiere cargar la pagina, lo pide a traves del
    # 'GET', por lo que cuando se quiera cargar la pagina debemos
    # definir la info predeterminada a mostrar
    elif request.method == 'GET': #cuando cargamos/redirreciona la pagina
        form.name.data = candidate.name
        form.category.data = candidate.category
        form.status.data = candidate.status

        form.description.data = candidate.description
        form.file.data = candidate.file
    
    return render_template('new_candidate.html', title='Actualizar candidato',
                             form=form, legend='Actualizar candidato')

@app.route("/candidates/<int:candidate_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_candidate(candidate_id):
    #dame el Candidate y si no existe, retorna 404 (no existe pagina)
    candidate = Candidate.query.get_or_404(candidate_id)
    #si el registro no fue hecho por el usuario logueado
    if current_user not in candidate.users:
        print("SDSDSD")
        abort(403)
    db.session.delete(candidate)
    db.session.delete(candidate.emails)
    db.session.delete(candidate.phones)
    db.session.commit()
    flash('Usuario eliminado', 'success')
    return redirect(url_for('home'))

@app.route("/category/new", methods=['GET', 'POST'])
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Categoría registrado', 'success')
        return redirect(url_for('categories'))
    return render_template('new_category.html', title='Nueva Categoría', 
                            form=form, legend='Ingresar nueva categoría')

@app.route("/categories", methods=['GET', 'POST'])
def categories():
    categories = Category.query.all()
    return render_template('categories.html', title='Categorías', 
                            categories=categories, legend='Categorías existentes')

@app.route("/users", methods=['GET', 'POST'])
def users():
    users = User.query.all()
    return render_template('users.html', title='Usuarios', 
                            users=users, legend='Usuarios existentes')

@app.route("/status", methods=['GET', 'POST'])
def status():
    statuses = Status.query.all()
    return render_template('status.html', title='Estados', 
                            statuses=statuses, legend='Estados')

@app.route("/status/new", methods=['GET', 'POST'])
def create_status():
    form = StateForm()
    if form.validate_on_submit():
        state = Status(name=form.name.data, 
                        classification=form.classification.data)
        db.session.add(state)
        db.session.commit()
        flash('Estado registrado', 'success')
        return redirect(url_for('status'))
    return render_template('new_status.html', title='Nuevo estado', 
                            form=form, legend='Ingresar nuevo estado')

@app.route("/offers/new", methods=['GET', 'POST'])
@login_required
def create_offer():
    form = OfferForm()
    form.category.query = Category.query.filter(Category.id >=0)
    form.status.query = Status.query.filter(Status.classification==CLASSIFICATION_STATUS_OFFER)
    #estado convocatoria: abierta o cerrada
    if form.validate_on_submit():
        oferta = Offer(name=form.name.data, 
                        category_id=form.category.data.id, 
                        status_id=form.status.data.id, 
                        description=form.description.data,
                        user_id = current_user.id)

        db.session.add(oferta)
        db.session.commit()
        flash('Oferta registrada', 'success')
        return redirect(url_for('offers'))

    # image_file=url_for('static', filename='files/'+current_user.image_file)
    return render_template('new_offer.html', title='Nueva oferta', 
                            form=form, legend='Registrar oferta')
#home 2
@app.route("/offers", methods=['GET', 'POST'])
def offers():
    offers = Offer.query.all()
    return render_template('offers.html', title='Ofertas', 
                            offers=offers, legend='Ofertas')

@app.route("/offers/<int:offer_id>", methods=['GET', 'POST'])
def offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    return render_template('offer.html', title=offer_id, offer=offer)

