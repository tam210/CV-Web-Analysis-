from flask import render_template, url_for, flash, redirect, request, abort
from main.forms import RegistrationForm, LoginForm, UploadFileForm, CandidateForm, CategoryForm, StateForm, OfferForm, CategoriesStatusesForm
from werkzeug.utils import secure_filename
import os
from main.analysis import obtenerDF_Email
from main import app, db, bcrypt
from main.models import Candidate, Category, User, Status, Offer, E_mail, Phone, Type, inicialize, Postulation
from sqlalchemy.exc import SQLAlchemyError

from flask_login import login_user, current_user, logout_user, login_required

NAMETYPE_USER_USER = 'Usuario'
NAMETYPE_USER_CANDIDATE = 'Candidato'
NAMETYPE_USER_ADMINISTRATOR = 'Administrador'

CLASSIFICATION_STATUS_OFFER = 'Trabajo'
CLASSIFICATION_STATUS_CANDIDATE = 'Candidato'



@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
@app.route("/candidates", methods=['GET', 'POST'])
def home():
    inicialize()
    page = request.args.get('page', 1, type=int) #default=1
    candidates = Candidate.query.paginate(page=page, per_page=5)

    form = CategoriesStatusesForm()    
    form.category.query = Category.query.filter(Category.id >=0)
    form.status.query = Status.query.filter(Status.classification==CLASSIFICATION_STATUS_CANDIDATE)

    if form.validate_on_submit():
        print("ENTRO AL FORMULARIO")
        #Si ambos filtros fueron completados
        if form.category.data and form.status.data:
            cat = Category.query.get(form.category.data.id)
            stat = Status.query.get(form.status.data.id)
            candidates = Candidate.query.filter_by(category_id = cat.id, status_id=stat.id)
        #Si uno o 0 filtros fueron completados
        else:
            # Si el filtro categoría fue completado, entonces el estado
            # no fue completado, así que se obtiene la query de categorías
            if(form.category.data):
                print("---Categoria seleccionada---")
                cat = Category.query.get(form.category.data.id)
                candidates = Candidate.query.filter_by(category_id = cat.id)
                print(candidates)

            else:
                print("---Categoria NO seleccionada--- 2 2 2 2s")
                # Si no  fue completada la categoría, entonces puede ser que
                # el estado sí esté completo
                if(form.status.data):
                    print("---Estado seleccionada---")
                    stat = Status.query.get(form.status.data.id)
                    candidates = Candidate.query.filter_by(status_id=stat.id)
                # Si llega hasta acá es porque ningún campo se completó,
                # Por default se obtendrán todas las ofertas    
                else:
                    candidates =  Candidate.query.all()
    # return render_template('offers.html', title='Ofertas', 
    #                         offers=offers, legend='Ofertas', form=form)

    """
    page: lo que se quiere obtener
    1: el valor por DEFAULT
    type: el tipo que debe tener la página, así se evitan strings u otro
    """
    #Candidates = Candidate.query.all()
    return render_template('home.html', title='Candidatos', legend='Candidatos', candidates=candidates, form=form)


@app.route("/candidates/category/<int:category_id>", methods=['GET', 'POST'])
def candidates(category_id):
    #page = request.args.get('page', 1, type=int) #default=1
    if not category_id:
        candidates = Candidate.query.all()
        #candidates = Candidate.query.paginate(page=page, per_page=5)
        print("Vale 0")
    else:
        print("NO vale 0")
        category = Category.query.get(category_id)
        print(category)
        candidates = Candidate.query.filter_by(category_id=category.id)
        if candidates:
            print("si")
        #candidates.paginate(page=page, per_page=5)
            #return redirect(url_for('home', category_id=category.id))

    #page = request.args.get('page', 1, type=int) #default=1
    #candidates = Candidate.query.paginate(page=page, per_page=5)
    return render_template('candidates.html',candidates=candidates)






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
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        email = E_mail.query.filter_by(name=form.email.data).first()
        if email:
            user = User.query.get(email.user_id)
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next') #args: diccionario
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Inicio de sesión fallido. Intente nuevamente')
        else:
            flash('El email ingresado no existe')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():
    #image_file=url_for('static', filename='files/'+current_user.image_file)
    print(current_user.email)
    return render_template('account.html', title='Account')


@app.route("/candidates/new", methods=['GET', 'POST'])
@login_required
def create_candidate():
    form = CandidateForm()
    form.category.query = Category.query.filter(Category.id >=0)
    form.status.query = Status.query.filter(Status.classification==CLASSIFICATION_STATUS_CANDIDATE)
    if form.validate_on_submit():
        try:
            #ff = form.file.data
            cand = Candidate(name=form.name.data,
                                category_id=form.category.data.id, 
                                status_id=form.status.data.id, 
                                #file=form.file.data, 
                                description=form.description.data)
            type_id = Type.query.filter_by(nametype=NAMETYPE_USER_CANDIDATE).first().id
            print(cand,"---", type_id)
            cand.type = type_id
            #Si se introdujo un archivo distinto al que tenía el candidato
            # if form.file.data != cand.file:
            #     # Si no existe un candidato con ese archivo
            #     if not Candidate.query.filter_by(file=form.file.data).first():
            #         cand.file = form.file.data
            #     else:
            #         flash('El archivo ingresado pertenece a otro candidato.')
            # else:
            #     cand.file = form.file.data

            
            db.session.add(cand)
            current_user.candidates.append(cand)
            db.session.add(current_user)
            #--------------------------------------------
            # Si ingresó un archivo
            #--------------------------------------------


            # if form.file.data:
            #     # Obtengo el email y teléfono del documento
            #     _, email, phone = obtenerDF_Email(ff)
            #     # Si se obtuvo un email válido (no nulo)
            #     if email: 
            #         # Si no existe un email con ese nombre se puede ingresar uno nuevo
            #         if not E_mail.query.filter_by(name=email).first():
            #             em2 = E_mail(name = email, candidate_id=cand.id, extracted_y_n='Y')
            #             db.session.add(em2)
            #         # Si no existe un teléfono con ese nombre se puede ingresar uno nuevo
            #     # Si se obtuvo un contacto válido (no nulo)
            #     if phone:
            #         # Si no existe un teléfono con ese nombre se puede ingresar uno nuevo
            #         if not Phone.query.filter_by(name=phone).first():
            #             ph2 = Phone(name = phone, candidate_id=cand.id, extracted_y_n='Y')
            #             db.session.add(ph2)



            #-------------------------------------------
            # Si ingresó un email y teléfono manualmente
            #-------------------------------------------
            #Si ingresó un email en el formulario crea un email nuevo
            if form.email.data:
                print("Email agregado por formulario")
                em = E_mail(name=form.email.data, candidate_id=cand.id, extracted_y_n='N')
                print("\n\nEMAIL A INGRESAR",em)
                db.session.add(em)
            #Si ingresó un teléfono en el formulario crea un email nuevo
            if form.phone.data:
                print("Telefono agregado por formulario")
                ph = Phone(name=form.phone.data, candidate_id=cand.id, extracted_y_n='N')
                db.session.add(ph)
            #Si ingresó un email en el formulario crea un email nuevo
            db.session.commit()
            flash('Candidato registrado', 'success')
            print(Candidate.query.all())
            return redirect(url_for('home'))

        except SQLAlchemyError as e:
            print("ERROR! - Registro de candidato")
            error = str(e.__dict__['orig'])
        return error
        
    return render_template('new_candidate.html', title='Nuevo Candidato', 
                            form=form, legend='Registrar Candidato')


@app.route("/candidates/<int:candidate_id>", methods=['GET', 'POST'])
def candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    #dame el Candidate y si no existe, retorna 404 (no existe pagina)
    form=UploadFileForm()
    # user_form = UserAdd()
    if form.validate_on_submit():
        print("           -            ")
        print(form.file.data)
        ff=form.file.data
        #print(form.file.data.filename)
        #ff = form.file.data.filename
        #Si ingresó algo no nulo
        if form.file.data:
            print("\n\n\n\n")
            print("\n\nINGRESÓ UN ARCHIVO\n\n")
            #Si el archivo ingresado no es nulo y es distinto al original
            # CASOS 
            #       => documento a documento: se reemplazará información de distintas fuentes
            #       => vacio a documento: se agregará información de una fuente
            print("\n\nCANDIDATO!!!!!!: FILE",candidate.file,"\n\n")
            if candidate.file: #Documento a documento: se reemplazará información de distintas fuentes
                if candidate.file != form.file.data:

                    print("\n\nDOCUMENTO A DOCUMENTO\n\n")
                    # Obtengo los datos del documento para ver si no se repiten en otro archivo
                    _, email, phone = obtenerDF_Email(ff)
                    if email: 
                        print("INGRESANDO EMAIL")
                        if not E_mail.query.filter_by(name=email).first():
                            em2 = E_mail(name = email, candidate_id=candidate.id, extracted_y_n='Y')
                            #db.session.add(em2)
                        else:
                            flash('El archivo ingresado pertenece a otro candidato.', 'danger')
                            return redirect(url_for('candidate', candidate_id=candidate.id))
                    if phone:
                        print("INGRESANDO TELÉFONO")
                        if not Phone.query.filter_by(name=phone).first():
                            ph2 = Phone(name = phone, candidate_id=candidate.id, extracted_y_n='Y')
                            #db.session.add(ph2)            
                        else:
                            flash('El archivo ingresado pertenece a otro candidato.', 'danger')
                            return redirect(url_for('candidate', candidate_id=candidate.id))
                    print(em2)
                    if em2: 
                        db.session.add(em2)  
                        #db.session.commit()              
                    if ph2:
                        db.session.add(ph2)
                        #db.session.commit()              
                    #Una vez verificado que el documento a ingresar no choca con nada, borro los registros del documento anterior
                    # para liberarlos
                    candidate_extracted_email = E_mail.query.filter_by(candidate_id=candidate.id, extracted_y_n='Y').first()
                    candidate_extracted_phone = Phone.query.filter_by(candidate_id=candidate.id, extracted_y_n='Y').first()
                    if candidate_extracted_email:
                        db.session.delete(candidate_extracted_email)
                        #db.session.commit()
                    if candidate_extracted_phone:
                        db.session.delete(candidate_extracted_phone)
                        #db.session.commit()
                    candidate.file = form.file.data
                    db.session.commit()
                    
            else:
                print("\n\nVACIO A DOCUMENTO\n\n")
                _, email, phone = obtenerDF_Email(ff)
                if email: 
                    print("INGRESANDO EMAIL")
                    if not E_mail.query.filter_by(name=email).first():
                        em2 = E_mail(name = email, candidate_id=candidate.id, extracted_y_n='Y')
                    else:
                        flash('El archivo ingresado pertenece a otro candidato.', 'danger')
                        return redirect(url_for('candidate', candidate_id=candidate.id))
                if phone:
                    print("INGRESANDO TELÉFONO")
                    if not Phone.query.filter_by(name=phone).first():
                        ph2 = Phone(name = phone, candidate_id=candidate.id, extracted_y_n='Y')
                        #db.session.add(ph2)    lo añado a sesion despues, por si despues se redireciona y queda en sesion        
                    else:
                        flash('El archivo ingresado pertenece a otro candidato.', 'danger')
                        return redirect(url_for('candidate', candidate_id=candidate.id))
                if em2: 
                    db.session.add(em2)  
                #    db.session.commit()              
                if ph2:
                    db.session.add(ph2)
                candidate.file = form.file.data
                db.session.commit()              
                #candidate.file = form.file.data
                flash('Archivo actualizado', 'success')
                return redirect(url_for('home'))
            #Vacio a documento: se agregará información de una fuente
            #else:

        # Si ingresó nulo, que se borren los registros
        else:
            print("\n\nNO INGRESÓ UN ARCHIVO\n\n")
            candidate_extracted_email = E_mail.query.filter_by(candidate_id=candidate.id, extracted_y_n='Y').first()
            candidate_extracted_phone = Phone.query.filter_by(candidate_id=candidate.id, extracted_y_n='Y').first()
            if candidate_extracted_email:
                db.session.delete(candidate_extracted_email)
                #db.session.commit()
            if candidate_extracted_phone:
                db.session.delete(candidate_extracted_phone)
                #db.session.commit()
            candidate.file = form.file.data
            flash('Archivo actualizado', 'success')
            return redirect(url_for('home'))

    
    offers = Offer.query.all()
    candidate = Candidate.query.get_or_404(candidate_id)
    if candidate.file:
        image_file=url_for('static', filename='files/'+candidate.file)
    else:
        image_file=url_for('static', filename='files/default.jpg')
    
    select = request.form.getlist('skills')
    print("\n\n\n\n\n\n\n")

    for i in select:
        oferta = Offer.query.get(i)
        # Veo si existe una postulacion del candidato en la oferta
        verify_postulation = Postulation.query.filter_by(candidate_id=candidate.id, offer_id=oferta.id).first()
        print(verify_postulation)
        if not verify_postulation:
            initial_status_postulation = Status.query.filter_by(name='En evaluación').first()
            postulation = Postulation(offer_id=oferta.id, candidate_id=candidate.id, status_id=initial_status_postulation)
            db.session.add(postulation)
            #oferta.candidates.append(candidate)
            flash('Oferta postulada', 'success')
        else:
            flash('La oferta ya se encuentra postulada', 'danger')
    db.session.commit()
    candidate_postulations = Postulation.query.filter_by(candidate_id=candidate.id)
    
    #print(oferta.candidates)    
    return render_template('candidate.html', title=candidate_id, candidate=candidate, image_file=image_file, offers=offers, form=form, candidate_postulations=candidate_postulations)


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
        candidate.description = form.description.data
        candidate.category_id = form.category.data.id
        candidate.status_id = form.status.data.id
        # Si introdujo un email manualmente
        if form.email.data:
            if not E_mail.query.filter_by(name=form.email.data).first():
                em = E_mail(name=form.email.data, candidate_id=candidate.id, extracted_y_n='N')
                db.session.add(em)
            else:
                print ("-------------------------")
        # Si introdujo un teléfono manualmente
        if form.phone.data:
            if not Phone.query.filter_by(name=form.phone.data).first():
                ph = Phone(name=form.phone.data, candidate_id=candidate.id, extracted_y_n='N')
                db.session.add(ph)
            else:
                print ("-------------------------")
        


        # #Si se introdujo un archivo distinto al que tenía el candidato
        # if form.file.data != candidate.file:
        #     # Si no existe un candidato con ese archivo
        #     if not Candidate.query.filter_by(file=form.file.data).first():
        #         candidate.file = form.file.data
        #         candidate_extracted_email = E_mail.query.filter_by(candidate_id=candidate.id, extracted_y_n='Y').first()
        #         candidate_extracted_phone = Phone.query.filter_by(candidate_id=candidate.id, extracted_y_n='Y').first()
        #         # Borro las extracciones anteriores de emails
        #         if candidate_extracted_email:
        #             db.session.delete(candidate_extracted_email)
        #             db.session.commit()
        #         if candidate_extracted_phone:
        #             db.session.delete(candidate_extracted_phone)
        #             db.session.commit()
            
            
        #     # Extraigo los emails y teléfonos del documento y los asocio al candidato
        #     ff = form.file.data
        #     # Si subió un archivo en el formulario
        #     if form.file.data:
        #         # Obtengo el email y teléfono del documento
        #         _, email, phone = obtenerDF_Email(ff)
        #         # Si se obtuvo un email válido (no nulo)
        #         if email: 
        #             # Si no existe un email con ese nombre se puede ingresar uno nuevo
        #             if not E_mail.query.filter_by(name=email).first():
        #                 em2 = E_mail(name = email, candidate_id=candidate.id, extracted_y_n='Y')
        #                 db.session.add(em2)
        #             else:
        #                 flash('El archivo ingresado pertenece a otro candidato.', 'danger')
        #                 return redirect(url_for('candidate', candidate_id=candidate.id))

        #             # Si no existe un teléfono con ese nombre se puede ingresar uno nuevo
        #         # Si se obtuvo un contacto válido (no nulo)
        #         if phone:
        #             # Si no existe un teléfono con ese nombre se puede ingresar uno nuevo
        #             if not Phone.query.filter_by(name=phone).first():
        #                 ph2 = Phone(name = phone, candidate_id=candidate.id, extracted_y_n='Y')
        #                 db.session.add(ph2)            
        #             else:
        #                 flash('El archivo ingresado pertenece a otro candidato.', 'danger')
        #                 return redirect(url_for('candidate', candidate_id=candidate.id))

        #         db.session.commit()
            

        #     # else:
        #     #     flash('El archivo ingresado pertenece a otro candidato.', 'danger')
        #     #     return redirect(url_for('candidate', candidate_id=candidate.id))

        # candidate.file = form.file.data

            
        db.session.commit()
        #print(candidate)
        flash('Información del candidato actualizada', 'success')
        return redirect(url_for('candidate', candidate_id=candidate.id))
    #-------------------------------------------
    # Cuando se carga la pagina, se carga con info ya cargada del sistema.
    # Cuando el sistema quiere cargar la pagina, lo pide a traves del
    # 'GET', por lo que cuando se quiera cargar la pagina debemos
    # definir la info predeterminada a mostrar
    #-------------------------------------------
    elif request.method == 'GET': #cuando cargamos/redirreciona la pagina
        form.name.data = candidate.name
        form.category.data = candidate.category
        form.status.data = candidate.status
        form.description.data = candidate.description
        #form.file.data = candidate.file

        # if candidate.emails.count()>0: #si tiene emails registrados
        #     form.name          
    
    return render_template('new_candidate.html', title='Actualizar candidato',
                             form=form, legend='Actualizar candidato')

@app.route("/candidates/<int:candidate_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_candidate(candidate_id):
    #dame el Candidate y si no existe, retorna 404 (no existe pagina)
    candidate = Candidate.query.get_or_404(candidate_id)
    #si el registro no fue hecho por el usuario logueado
    if current_user not in candidate.users:
        abort(403)
    db.session.delete(candidate)
    #db.session.delete(candidate.emails)
    #db.session.delete(candidate.phones)
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
        print(Offer.query.all())
        return redirect(url_for('offers'))

    # image_file=url_for('static', filename='files/'+current_user.image_file)
    return render_template('new_offer.html', title='Nueva oferta', 
                            form=form, legend='Registrar oferta')
#home 2
@app.route("/offers", methods=['GET', 'POST'])
def offers():
    #cambio variable global
    form = CategoriesStatusesForm()    
    form.category.query = Category.query.filter(Category.id >=0)
    form.status.query = Status.query.filter(Status.classification==CLASSIFICATION_STATUS_OFFER)
    offers = Offer.query.all()
    if form.validate_on_submit():
        #Si ambos filtros fueron completados
        if form.category.data and form.status.data:
            cat = Category.query.get(form.category.data.id)
            stat = Status.query.get(form.status.data.id)
            offers = Offer.query.filter_by(category_id = cat.id, status_id=stat.id)
        #Si uno o 0 filtros fueron completados
        else:
            # Si el filtro categoría fue completado, entonces el estado
            # no fue completado, así que se obtiene la query de categorías
            if(form.category.data):
                print("---Categoria seleccionada---")
                cat = Category.query.get(form.category.data.id)
                offers = Offer.query.filter_by(category_id = cat.id)

            else:
                print("---Categoria NO seleccionada--- 2 2 2 2s")
                # Si no  fue completada la categoría, entonces puede ser que
                # el estado sí esté completo
                if(form.status.data):
                    print("---Estado seleccionada---")
                    stat = Status.query.get(form.status.data.id)
                    offers = Offer.query.filter_by(status_id=stat.id)
                # Si llega hasta acá es porque ningún campo se completó,
                # Por default se obtendrán todas las ofertas    
                else:
                    offers = Offer.query.all()
    return render_template('offers.html', title='Ofertas', 
                            offers=offers, legend='Ofertas', form=form)

@app.route("/offers/<int:offer_id>", methods=['GET', 'POST'])
def offer(offer_id):
    candidates = Candidate.query.all()
    offer = Offer.query.get_or_404(offer_id)
    select = request.form.getlist('skills')
    #Itero en los candidatos seleccionados
    for i in select:
        print(i)
        candidate = Candidate.query.get(i) #Candidato seleccionado

        verify_postulation = Postulation.query.filter_by(candidate_id=candidate.id, offer_id=offer.id).first()

        if not verify_postulation: #Si el candidato no está postulado
            print("No hay postulacion del candidato en esa oferta")
            initial_status_postulation = Status.query.filter_by(name='En evaluación').first()
            print(initial_status_postulation)
             #candidate.offers.append(offer) #Agrego la oferta al candidato
            postulation = Postulation(offer_id=offer.id, candidate_id=candidate.id, status_id=initial_status_postulation.id)
            #print(postulation)
            db.session.add(postulation)
            print(postulation)
            db.session.commit()
            flash('Candidato postulado', 'success')
        else:
            flash('El candidato ya se encuentra postulado', 'danger')
    candidate_postulations = Postulation.query.filter_by(offer_id=offer.id)
    print(candidate_postulations)
    #candidate_postulations = offer.candidates
    return render_template('offer.html', title=offer_id, offer=offer, candidates=candidates,candidate_postulations=candidate_postulations)

@app.route("/offers/<int:offer_id>/update", methods=['GET', 'POST'])
@login_required
def update_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    if current_user != offer.user:
        abort(403)
    form = OfferForm()        
    form.category.query = Category.query.filter(Category.id >=0)
    form.status.query = Status.query.filter(Status.classification==CLASSIFICATION_STATUS_OFFER)
    if form.validate_on_submit():
        offer.name = form.name.data 
        offer.description = form.description.data
        offer.category_id = form.category.data.id
        offer.status_id = form.status.data.id
            
        db.session.commit()
        #print(candidate)
        flash('Información de la oferta actualizada', 'success')
        return redirect(url_for('offer', offer_id=offer.id))
    #-------------------------------------------
    # Cuando se carga la pagina, se carga con info ya cargada del sistema.
    # Cuando el sistema quiere cargar la pagina, lo pide a traves del
    # 'GET', por lo que cuando se quiera cargar la pagina debemos
    # definir la info predeterminada a mostrar
    #-------------------------------------------
    elif request.method == 'GET': #cuando cargamos/redirreciona la pagina
        form.name.data = offer.name
        form.category.data = offer.category
        form.status.data = offer.status
        form.description.data = offer.description

        # if candidate.emails.count()>0: #si tiene emails registrados
        #     form.name          
    
    return render_template('new_offer.html', title='Actualizar oferta',
                             form=form, legend='Actualizar oferta')

@app.route("/offers/<int:offer_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_offer(offer_id):
    #dame el Candidate y si no existe, retorna 404 (no existe pagina)
    offer = Offer.query.get_or_404(offer_id)
    #si el registro no fue hecho por el usuario logueado
    if current_user != offer.user:
        abort(403)
    db.session.delete(offer)
    db.session.commit()
    flash('Oferta eliminada', 'success')
    return redirect(url_for('home'))
