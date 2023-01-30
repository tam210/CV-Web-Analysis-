from main import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    
    candidatos_cat = db.relationship('Candidato', backref='categoria', lazy='dynamic')


    def __repr__(self): ##como nuestro objeto es impreso
        return f"Categoria('{self.name}')"


class Candidato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id')) #
    #categoria = db.Column(db.Integer, nullable=False) #
    # category =db.relationship('Categoria')
    nombre = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    cargo_postulante = db.Column(db.String(50), nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    #usuarios = db.relationship('Usuario', backref='author', lazy=True)

    def __repr__(self): ##como nuestro objeto es impreso
        return f"Candidato('{self.id}', '{self.categoria_id}', '{self.nombre}', '{self.estado}', '{self.image_file}', '{self.cargo_postulante}')"



categoria_usuario = db.Table('categoria_usuario',
                            db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id')),
                            db.Column('categoria', db.Integer, db.ForeignKey('categoria.name'))
                            )

candidato_usuario = db.Table('candidato_usuario',
                            db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id')),
                            db.Column('candidato_id', db.Integer, db.ForeignKey('candidato.id'))
                            )

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    clave = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    username = db.Column(db.Integer, unique=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    #relacion con post, 'agrega' columna a Candidato llamada 'author'que seria este user
    #categorias es una consulta corriendo, no es que se agrege como columna a Usuario
    #lazy: true= sql alchemy carga la info necesaria al tiro
    #categorias = db.relationship('Categoria', backref='author', lazy=True)
    #candidatos = db.relationship('Candidato', backref='author', lazy=True)
    
    candidatos = db.relationship('Candidato', secondary=candidato_usuario, backref='usuarios')
    categorias = db.relationship('Categoria', secondary=categoria_usuario, backref='usuarios')

    def __repr__(self): ##como nuestro objeto es impreso
        return f"Usuario('{self.id}', '{self.nombre}', '{self.clave}', '{self.email}', '{self.username}')"