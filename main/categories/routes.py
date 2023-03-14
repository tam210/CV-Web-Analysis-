from flask import render_template, url_for, flash, redirect, Blueprint
from main.categories.forms import CategoryForm
from main import db
from main.models import Category
from flask_login import login_required

categories_bp = Blueprint('categories', __name__)

@categories_bp.route("/category/new", methods=['GET', 'POST'])
@login_required
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Categoría registrado', 'success')
        return redirect(url_for('categories.categories'))
    return render_template('new_category.html', title='Nueva Categoría', 
                            form=form, legend='Ingresar nueva categoría')

@categories_bp.route("/categories", methods=['GET', 'POST'])
@login_required
def categories():
    categories = Category.query.all()
    return render_template('categories.html', title='Categorías', 
                            categories=categories, legend='Categorías existentes')
