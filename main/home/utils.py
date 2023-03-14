from main.models import Category, Status, Type
from main import db


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
