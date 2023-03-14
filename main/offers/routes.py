from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from main.offers.forms import OfferForm
from main.filters.forms import CategoriesStatusesForm
from main import db
from main.models import Candidate, Category, Status, Offer, Postulation
from flask_login import current_user, login_required
from main.main.utils import CLASSIFICATION_STATUS_OFFER, CLASSIFICATION_STATUS_CANDIDATE

offers_bp = Blueprint('offers', __name__)

@offers_bp.route("/offers/new", methods=['GET', 'POST'])
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
        return redirect(url_for('offers.offers'))

    # image_file=url_for('static', filename='files/'+current_user.image_file)
    return render_template('new_offer.html', title='Nueva oferta', 
                            form=form, legend='Registrar oferta')
#home 2
@offers_bp.route("/offers", methods=['GET', 'POST'])
@login_required
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

@offers_bp.route("/offers/<int:offer_id>", methods=['GET', 'POST'])
@login_required
def offer(offer_id):
    candidates = Candidate.query.all()
    offer = Offer.query.get_or_404(offer_id)
    select = request.form.getlist('skills')
    #Itero en los candidatos seleccionados
    for i in select:
        print(i)
        candidate = Candidate.query.get(i) #Candidato seleccionado
        print("----------nombre:-",candidate.name)
        verify_postulation = Postulation.query.filter_by(candidate_id=candidate.id, offer_id=offer.id).first()

        if not verify_postulation: #Si el candidato no está postulado
            print("No hay postulacion del candidato en esa oferta")
            initial_status_postulation = Status.query.filter_by(name='En evaluación').first()
            print(initial_status_postulation)
             #candidate.offers.offersend(offer) #Agrego la oferta al candidato
            postulation = Postulation(offer_id=offer.id, candidate_id=candidate.id, status_id=initial_status_postulation.id)
            #print(postulation)
            db.session.add(postulation)
            print(postulation)
            db.session.commit()
            flash('Candidato postulado', 'success')
        else:
            flash('El candidato ya se encuentra postulado', 'danger')

    select_status = request.form.get('statuses')

    if select_status:
        select_postulation = request.form.get('postulation')
        postu = Postulation.query.get(select_postulation)
        postu.status_id = select_status
        #db.session.add(postulation)
        db.session.commit()

    candidate_postulations = Postulation.query.filter_by(offer_id=offer.id)
    statuses = Status.query.filter_by(classification=CLASSIFICATION_STATUS_CANDIDATE)
    return render_template('offer.html', title=offer_id, offer=offer, candidates=candidates,candidate_postulations=candidate_postulations, statuses=statuses)

@offers_bp.route("/offers/<int:offer_id>/update", methods=['GET', 'POST'])
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
        return redirect(url_for('offers.offer', offer_id=offer.id))
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

@offers_bp.route("/offers/<int:offer_id>/delete", methods=['GET', 'POST'])
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
    return redirect(url_for('candidates.home'))
