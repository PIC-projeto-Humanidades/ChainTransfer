from flask import Flask
from modules.database import db
from controllers.file_controller import file_bp
import os
UPLOAD_FOLDER = './medias'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Criando as tabelas
with app.app_context():
    db.create_all()

# Registrando Blueprints
app.register_blueprint(file_bp, url_prefix='/files')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)