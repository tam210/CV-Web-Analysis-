from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
#from main.models import Category, Status
app = Flask(__name__)

app.config['SECRET_KEY'] = '76e0456a45472c9cc0b9af2e3a881297'
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' #path, /// para ppth relativo
                                                               #///: debe estar en la carpeta
                                                               #de este proyecto
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) #Creo la instancia de la BD
app.app_context().push()



bcrypt=Bcrypt(app)
login_manager = LoginManager(app) #administra las sesiones en background
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'



#pongo las rutas despues de inicializar:
from main import routes
