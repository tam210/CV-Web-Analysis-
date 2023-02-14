from main import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.ext.associationproxy import association_proxy


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def inicialize():
    if Status.query.all()== []:
        #-------------------------------------------
        # Ingreso los tipos independientes (estados, categorías y tipos)
        #-------------------------------------------
        ob1 = Status(name='Activo',classification='Trabajo')
        ob2 = Status(name='Finalizado',classification='Trabajo')

        ob3 = Status(name='Rechazado',classification='Candidato')
        ob4 = Status(name='En evaluación',classification='Candidato')
        ob5 = Status(name='Aprobado',classification='Candidato')

        obs6 = Category(name='Finanzas')
        obs7 = Category(name='RRHH')
        obs8 = Category(name='Educación')
        obs9 = Category(name='Psicología')

        #ob5 = Status(name='Indefinido',classification='Candidato')
        #ob2 = Status(name='Indefinido',classification='Trabajo')


        type_1 = Type(nametype='Candidato')
        type_2 = Type(nametype='Administrador')
        type_3 = Type(nametype='Usuario')
        db.session.add_all([ob1,ob2, ob3, ob4, ob5, obs6, obs7, obs8, obs9, type_1, type_2, type_3])
        db.session.commit()
        #-------------------------------------------
        # Ingreso un administrador a BD
        #-------------------------------------------

        #-------------------------------------------
        # Le asocio un email una vez ingresado el admin en el sistema vía commit
        # (ya que si no está en el sistema su id es None, por lo tanto
        # al hacer user_id=admin.id estaría en None)
        #-------------------------------------------


        print('Inserción inicial')

    else:
        print("Ya existen elementos iniciales")

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    offers = db.relationship('Offer', backref='category', lazy='dynamic') #fk
    candidates_cat = db.relationship('Candidate', backref='category', lazy='dynamic')

    def __repr__(self): ##como nuestro objeto es impreso
        return f"Category ('{self.name}', '{self.id}')"



class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    classification = db.Column(db.String(50), nullable=False)
    offers = db.relationship('Offer', backref='status') #fk
    candidates = db.relationship('Postulation', back_populates="status")

    def __repr__(self): 
        return f"Status ('{self.name}', '{self.classification}' )"


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, db.ForeignKey('type.id'))
    name = db.Column(db.String(50), nullable=False)
    file = db.Column(db.String(20))
    description = db.Column(db.String(50), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    emails = db.relationship('E_mail', backref='candidate', lazy='dynamic', cascade='save-update, merge, delete') #fk
    phones = db.relationship('Phone', backref='candidate', lazy='dynamic', cascade='save-update, merge, delete') #fk
    offers = db.relationship('Postulation', back_populates="candidate", lazy='dynamic', cascade='save-update, merge, delete')

    def __repr__(self): ##como nuestro objeto es impreso
        return f"Candidate ('{self.id}', '{self.name}', '{self.file}', '{self.description}', '{self.creation_date}'. '{self.type}','{self.category_id}')"

category_user = db.Table('category_user',
                            db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                            db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
                            )

candidate_user = db.Table('candidate_user',
                            db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                            db.Column('candidate_id', db.Integer, db.ForeignKey('candidate.id'))
                            )

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id')) #
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #creador del empleo
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    description = db.Column(db.String(50), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    candidates = db.relationship('Postulation', back_populates="offer", lazy='dynamic', cascade='save-update, merge, delete')
    def __repr__(self):
        return f"Offer('{self.id}', '{self.name}', '{self.category_id}', '{self.user_id}', '{self.status_id}', '{self.description}', '{self.creation_date}','{self.category_id}','{self.status_id}')"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    username = db.Column(db.Integer, unique=True, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.Integer, db.ForeignKey('type.id'))
    candidates = db.relationship('Candidate', secondary=candidate_user, backref='users')
    categories = db.relationship('Category', secondary=category_user, backref='users')
    offers = db.relationship('Offer', backref='user', lazy='dynamic') #fk
    email = db.relationship('E_mail', uselist=False, cascade='all,delete', backref='user')

    def __repr__(self): ##como nuestro objeto es impreso
        return f"User('Id: {self.id}', Name: '{self.name}', Password: '{self.password}', Email: '{self.email}', Username: '{self.username}', Date: '{self.creation_date}', Type'{self.type}')"



class E_mail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id', ondelete='CASCADE'), nullable=True) #fk
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    extracted_y_n = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        return f"Email('{self.id}', '{self.name}')"


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
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id', ondelete='CASCADE')) #
    extracted_y_n = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        return f"Phone('{self.id}', '{self.name}', '{self.candidate_id}')"


class Postulation(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    offer_id = db.Column(db.Integer, db.ForeignKey('offer.id', ondelete='CASCADE'))
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id', ondelete='CASCADE'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id', ondelete='CASCADE'))
    offer = db.relationship('Offer', backref='postulations')
    candidate = db.relationship('Candidate', backref='postulations')
    status = db.relationship('Status', backref='postulations')
    def __repr__(self):
        return f"Postulation('ID: '{self.id}', Offer_id: {self.offer_id}', Candidate_id: '{self.candidate_id}', Status_id: '{self.status_id}')"