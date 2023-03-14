from flask import (render_template, Blueprint)
from main.home.utils import inicialize


home_bp = Blueprint('home', __name__)

@home_bp.route("/", methods=['GET', 'POST'])
@home_bp.route("/home", methods=['GET', 'POST'])
def home():
    inicialize()
    return render_template('home.html', title='Inicio')
