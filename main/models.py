from main import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Estado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    classification = db.Column(db.String(50), nullable=False)
    #Foreign key (1,N) Estado - Oferta
    ofertas = db.relationship('Oferta', backref='estado') #fk
    #Foreign key (1, N) Estado - Candidato
    candidatos_est = db.relationship('Candidato', backref='estado', lazy='dynamic')
    #Similar al to_string()
    def __repr__(self): 
        return f"Estado('{self.name}')"



class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    #Foreign key (1, N) Categoria - Ofertas
    ofertas = db.relationship('Oferta', backref='categoria') #fk
    #Foreign key (1, N) Categoria - Candidato
    candidatos_cat = db.relationship('Candidato', backref='categoria', lazy='dynamic')

    def __repr__(self): ##como nuestro objeto es impreso
        return f"Categoria('{self.name}', '{self.id}')"


class Candidato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    cargo_postulante = db.Column(db.String(50), nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'))

    def __repr__(self): ##como nuestro objeto es impreso
        return f"Candidato('{self.id}', '{self.categoria_id}', '{self.nombre}', '{self.estado_id}', '{self.image_file}', '{self.cargo_postulante}')"



categoria_usuario = db.Table('categoria_usuario',
                            db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id')),
                            db.Column('categoria', db.Integer, db.ForeignKey('categoria.name'))
                            )

candidato_usuario = db.Table('candidato_usuario',
                            db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id')),
                            db.Column('candidato_id', db.Integer, db.ForeignKey('candidato.id'))
                            )
                            
oferta_candidato = db.Table('oferta_candidato',
                            db.Column('oferta_id', db.Integer, db.ForeignKey('oferta.id')),
                            db.Column('candidato_id', db.Integer, db.ForeignKey('candidato.id'))
                            )

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    clave = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    username = db.Column(db.Integer, unique=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    candidatos = db.relationship('Candidato', secondary=candidato_usuario, backref='usuarios')
    categorias = db.relationship('Categoria', secondary=categoria_usuario, backref='usuarios')

    def __repr__(self): ##como nuestro objeto es impreso
        return f"Usuario('{self.id}', '{self.nombre}', '{self.clave}', '{self.email}', '{self.username}')"

class Oferta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id')) #
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id')) #creador del empleo
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'))
    descripcion = db.Column(db.String(50), nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    candidatos = db.relationship('Candidato', secondary=oferta_candidato, backref='ofertas')


    def __repr__(self): ##como nuestro objeto es impreso
        return f"Oferta('{self.id}', '{self.nombre}', '{self.categoria_id}', '{self.usuario_id}', '{self.estado_id}', '{self.descripcion}', '{self.fecha_creacion}')"
