
class Config:

    SECRET_KEY = '76e0456a45472c9cc0b9af2e3a881297'
    UPLOAD_FOLDER = 'static/files'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db' #path, /// para ppth relativo debe estar en la carpeta de este proyecto
    SQLALCHEMY_TRACK_MODIFICATIONS = False