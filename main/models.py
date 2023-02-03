from main import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def inicialize():
    if Status.query.all()== []:

        ob1 = Status(name='Activo',classification='Trabajo')
        ob2 = Status(name='Finalizado',classification='Trabajo')

        ob3 = Status(name='Rechazado',classification='Candidato')
        ob4 = Status(name='En evaluación',classification='Candidato')
        ob5 = Status(name='Aprobado',classification='Candidato')

        obs6 = Category(name='Finanzas')
        obs7 = Category(name='RRHH')
        obs8 = Category(name='Educación')
        obs9 = Category(name='Psicología')

        type_1 = Type(nametype='Candidato')
        type_2 = Type(nametype='Administrador')
        type_3 = Type(nametype='Usuario')

        admin = User(name='admin', password='admin', username='admin_username', type=type_2.id)
        #email_admin = E_mail(name = 'administrador@gmail.com', user_id=admin.id)


        db.session.add_all([ob1,ob2, ob3, ob4, ob5, obs6, obs7, obs8, obs9, type_1, type_2, type_3, admin])
        print('Inserción inicial realizada')
        db.session.commit()
    else:
        print("Ya existen elementos iniciales")

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    classification = db.Column(db.String(50), nullable=False)
    #Foreign key (1,N) Estado - Oferta
    offers = db.relationship('Offer', backref='status') #fk
    #Foreign key (1, N) Estado - Candidato
    candidates_status = db.relationship('Candidate', backref='status', lazy='dynamic')
    #Similar al to_string()
    def __repr__(self): 
        return f"Status ('{self.name}', '{self.classification}' )"



class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    #Foreign key (1, N) Categoria - Ofertas
    offers = db.relationship('Offer', backref='category', lazy='dynamic') #fk
    #Foreign key (1, N) Categoria - Candidato
    candidates_cat = db.relationship('Candidate', backref='category', lazy='dynamic')

    def __repr__(self): ##como nuestro objeto es impreso
        return f"Category ('{self.name}', '{self.id}')"


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #type = db.Column(db.String(50), nullable = False)
    type = db.Column(db.Integer, db.ForeignKey('type.id'))
    name = db.Column(db.String(50), nullable=False)
    file = db.Column(db.String(20), nullable=False, unique=True, default='default.jpg')
    description = db.Column(db.String(50), nullable=False)
    #email = db.Column(db.String(50), nullable=True)
    # phone = db.Column(db.Integer, nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    #Foreign key (1, N) Candidato - Email
    emails = db.relationship('E_mail', backref='candidate', lazy='dynamic', passive_deletes=True) #fk
    phones = db.relationship('Phone', backref='candidate', lazy='dynamic', passive_deletes=True) #fk

    def __repr__(self): ##como nuestro objeto es impreso
        return f"Candidate ('{self.id}', '{self.name}', '{self.file}', '{self.description}', '{self.creation_date}'. '{self.type}')"

category_user = db.Table('category_user',
                            db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                            db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
                            )

candidate_user = db.Table('candidate_user',
                            db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                            db.Column('candidate_id', db.Integer, db.ForeignKey('candidate.id'))
                            )
                            
offer_candidate = db.Table('offer_candidate',
                            db.Column('offer_id', db.Integer, db.ForeignKey('offer.id')),
                            db.Column('candidate_id', db.Integer, db.ForeignKey('candidate.id'))
                            )

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    username = db.Column(db.Integer, unique=True, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    candidates = db.relationship('Candidate', secondary=candidate_user, backref='users')
    categories = db.relationship('Category', secondary=category_user, backref='users')

    email = db.Column(db.String(50), db.ForeignKey('e_mail.id'))
    type = db.Column(db.Integer, db.ForeignKey('type.id'))

    def __repr__(self): ##como nuestro objeto es impreso
        return f"User('{self.id}', '{self.name}', '{self.password}', '{self.email}', '{self.username}', '{self.creation_date}', '{self.type}')"


class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id')) #
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #creador del empleo
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    description = db.Column(db.String(50), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    candidates = db.relationship('Candidate', secondary=offer_candidate, backref='offers')

    def __repr__(self):
        return f"Offer('{self.id}', '{self.name}', '{self.category_id}', '{self.user_id}', '{self.status_id}', '{self.description}', '{self.creation_date}')"

class E_mail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id')) #fk
    #status_id = db.Column(db.Integer, db.ForeignKey('status.id', ondelete='CASCADE'))
    user_id = db.relationship('User', backref='e_mail', lazy='dynamic') #fk

    def __repr__(self):
        return f"Email('{self.id}', '{self.name}', '{self.candidate_id}')"

class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nametype = db.Column(db.String(50), nullable=False, unique=True)
    users = db.relationship('User', backref='type_user', lazy='dynamic')
    candidates = db.relationship('Candidate', backref='type_candidate', lazy='dynamic')

    def __repr__(self):
        return f"Type('{self.id}', '{self.nametype}')"


class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, nullable=False, unique=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id')) #

    def __repr__(self):
        return f"Phone('{self.id}', '{self.name}', '{self.candidate_id}')"
