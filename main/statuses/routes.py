from flask import render_template, url_for, flash, redirect, Blueprint
from main.statuses.forms import StateForm
from main import db
from main.models import Status
from flask_login import login_required

statuses_bp = Blueprint('statuses', __name__)


@statuses_bp.route("/status", methods=['GET', 'POST'])
def status():
    statuses = Status.query.all()
    return render_template('status.html', title='Estados', 
                            statuses=statuses, legend='Estados')

@statuses_bp.route("/status/new", methods=['GET', 'POST'])
def create_status():
    form = StateForm()
    if form.validate_on_submit():
        state = Status(name=form.name.data, 
                        classification=form.classification.data)
        db.session.add(state)
        db.session.commit()
        flash('Estado registrado', 'success')
        return redirect(url_for('statuses.status'))
    return render_template('new_status.html', title='Nuevo estado', 
                            form=form, legend='Ingresar nuevo estado')
