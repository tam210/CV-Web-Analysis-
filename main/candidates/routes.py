from flask import (render_template, url_for, flash, redirect, request, abort, Blueprint)
from main.candidates.forms import UploadFileForm, CandidateForm
from main.filters.forms import CategoriesStatusesForm
from main.analysis.analysis import obtenerDF_Email
from main import db
from main.models import Candidate, Category, Status, Offer, E_mail, Phone, Type, inicialize, Postulation
from sqlalchemy.exc import SQLAlchemyError
from flask_login import current_user, login_required
from main.main.utils import NAMETYPE_USER_CANDIDATE


candidates_bp = Blueprint('candidates', __name__)

@candidates_bp.route("/", methods=['GET', 'POST'])
@candidates_bp.route("/home", methods=['GET', 'POST'])
@candidates_bp.route("/candidates", methods=['GET', 'POST'])
def home():
    inicialize()
    page = request.args.get('page', 1, type=int) #default=1
    candidates = Candidate.query.paginate(page=page, per_page=5)

    form = CategoriesStatusesForm()    
    form.category.query = Category.query.filter(Category.id >=0)

    if form.validate_on_submit():
        print("ENTRO AL FORMULARIO")
        if form.category.data:
            cat = Category.query.get(form.category.data.id)
            candidates = Candidate.query.filter_by(category_id = cat.id)
        else:
            candidates =  Candidate.query.all()
    # if form.validate_on_submit():
    #     print("ENTRO AL FORMULARIO")
    #     #Si ambos filtros fueron completados
    #     if form.category.data and form.status.data:
    #         cat = Category.query.get(form.category.data.id)
    #         stat = Status.query.get(form.status.data.id)
    #         candidates = Candidate.query.filter_by(category_id = cat.id, status_id=stat.id)
    #     #Si uno o 0 filtros fueron completados
    #     else:
    #         # Si el filtro categoría fue completado, entonces el estado
    #         # no fue completado, así que se obtiene la query de categorías
    #         if(form.category.data):
    #             print("---Categoria seleccionada---")
    #             cat = Category.query.get(form.category.data.id)
    #             candidates = Candidate.query.filter_by(category_id = cat.id)
    #             print(candidates)

    #         else:
    #             print("---Categoria NO seleccionada--- 2 2 2 2s")
    #             # Si no  fue completada la categoría, entonces puede ser que
    #             # el estado sí esté completo
    #             if(form.status.data):
    #                 print("---Estado seleccionada---")
    #                 stat = Status.query.get(form.status.data.id)
    #                 candidates = Candidate.query.filter_by(status_id=stat.id)
    #             # Si llega hasta acá es porque ningún campo se completó,
    #             # Por default se obtendrán todas las ofertas    
    #             else:
    #                 candidates =  Candidate.query.all()
    """
    page: lo que se quiere obtener
    1: el valor por DEFAULT
    type: el tipo que debe tener la página, así se evitan strings u otro
    """
    #Candidates = Candidate.query.all()
    return render_template('home.html', title='Candidatos', legend='Candidatos', candidates=candidates, form=form)


@candidates_bp.route("/candidates/category/<int:category_id>", methods=['GET', 'POST'])
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


@candidates_bp.route("/candidates/new", methods=['GET', 'POST'])
@login_required
def create_candidate():
    form = CandidateForm()
    form.category.query = Category.query.filter(Category.id >=0)
    #form.status.query = Status.query.filter(Status.classification==CLASSIFICATION_STATUS_CANDIDATE)
    if form.validate_on_submit():
        try:
            #ff = form.file.data
            cand = Candidate(name=form.name.data,
                                category_id=form.category.data.id, 
                                #status_id=form.status.data.id, 
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
            return redirect(url_for('candidates.home'))

        except SQLAlchemyError as e:
            print("ERROR! - Registro de candidato")
            error = str(e.__dict__['orig'])
        return error
        
    return render_template('new_candidate.html', title='Nuevo Candidato', 
                            form=form, legend='Registrar Candidato')


@candidates_bp.route("/candidates/<int:candidate_id>", methods=['GET', 'POST'])
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
                            return redirect(url_for('candidates.candidate', candidate_id=candidate.id))
                    if phone:
                        print("INGRESANDO TELÉFONO")
                        if not Phone.query.filter_by(name=phone).first():
                            ph2 = Phone(name = phone, candidate_id=candidate.id, extracted_y_n='Y')
                            #db.session.add(ph2)            
                        else:
                            flash('El archivo ingresado pertenece a otro candidato.', 'danger')
                            return redirect(url_for('candidates.candidate', candidate_id=candidate.id))
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
                em2 = None
                ph2 = None

                if email: 
                    print("INGRESANDO EMAIL")
                    if not E_mail.query.filter_by(name=email).first():
                        em2 = E_mail(name = email, candidate_id=candidate.id, extracted_y_n='Y')
                    else:
                        flash('El archivo ingresado pertenece a otro candidato.', 'danger')
                        return redirect(url_for('candidates.candidate', candidate_id=candidate.id))
                if phone:
                    print("INGRESANDO TELÉFONO")
                    if not Phone.query.filter_by(name=phone).first():
                        ph2 = Phone(name = phone, candidate_id=candidate.id, extracted_y_n='Y')
                        #db.session.add(ph2)    lo añado a sesion despues, por si despues se redireciona y queda en sesion        
                    else:
                        flash('El archivo ingresado pertenece a otro candidato.', 'danger')
                        return redirect(url_for('candidates.candidate', candidate_id=candidate.id))
                if em2: 
                    db.session.add(em2)  
                #    db.session.commit()              
                if ph2:
                    db.session.add(ph2)
                candidate.file = form.file.data
                db.session.commit()              
                #candidate.file = form.file.data
                flash('Archivo actualizado', 'success')
                return redirect(url_for('candidates.home'))
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
            return redirect(url_for('candidates.home'))

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
            postulation = Postulation(offer_id=oferta.id, candidate_id=candidate.id, status_id=initial_status_postulation.id)
            db.session.add(postulation)
            db.session.commit()
            #oferta.candidates.append(candidate)
            flash('Oferta postulada', 'success')
        else:
            flash('La oferta ya se encuentra postulada', 'danger')
    candidate_postulations = Postulation.query.filter_by(candidate_id=candidate.id)
    return render_template('candidate.html', title=candidate_id, candidate=candidate, image_file=image_file, offers=offers, form=form, candidate_postulations=candidate_postulations)


@candidates_bp.route("/candidates/<int:candidate_id>/update", methods=['GET', 'POST'])
@login_required
def update_candidate(candidate_id):
    #dame el Candidate y si no existe, retorna 404 (no existe pagina)
    candidate = Candidate.query.get_or_404(candidate_id)
    #si el registro no fue hecho por el usuario logueado
    if current_user not in candidate.users:
        abort(403)
    form = CandidateForm() #creo nuevo formulario
        
    form.category.query = Category.query.filter(Category.id >=0)

    if form.validate_on_submit():
        candidate.name = form.name.data 
        candidate.description = form.description.data
        candidate.category_id = form.category.data.id
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
        return redirect(url_for('candidates.candidate', candidate_id=candidate.id))
    #-------------------------------------------
    # Cuando se carga la pagina, se carga con info ya cargada del sistema.
    # Cuando el sistema quiere cargar la pagina, lo pide a traves del
    # 'GET', por lo que cuando se quiera cargar la pagina debemos
    # definir la info predeterminada a mostrar
    #-------------------------------------------
    elif request.method == 'GET': #cuando cargamos/redirreciona la pagina
        form.name.data = candidate.name
        form.category.data = candidate.category
        form.description.data = candidate.description
        #form.file.data = candidate.file

        # if candidate.emails.count()>0: #si tiene emails registrados
        #     form.name          
    
    return render_template('new_candidate.html', title='Actualizar candidato',
                             form=form, legend='Actualizar candidato')

@candidates_bp.route("/candidates/<int:candidate_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_candidate(candidate_id):
    #dame el Candidate y si no existe, retorna 404 (no existe pagina)
    candidate = Candidate.query.get_or_404(candidate_id)
    postulations = Postulation.query.filter_by(candidate_id=candidate.id)
    #si el registro no fue hecho por el usuario logueado
    if current_user not in candidate.users:
        abort(403)
    db.session.delete(candidate)
 #   db.session.delete(postulations)

    #db.session.delete(candidate.phones)
    db.session.commit()
    flash('Usuario eliminado', 'success')
    return redirect(url_for('candidates.home'))
