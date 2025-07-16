import os
import argparse
import threading
from flask import Flask
from flask_cors import CORS   
from controllers.files_manager_controller import files_bp
from controllers.bundle_controller import bundle_bp
from controllers.file_controller import file_bp
from controllers.front_controller import frontend_bp
from database.migrator import create_tables
from services.network_service import meu_ip
from services.routines import start_routines
from logs.log_f import log_f as logger 
from pathlib import Path
MEDIA_PATH = Path(os.getcwd()) / "upload_files"

def create_app(start_background_routines=True):
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2 GiB
    app.config['UPLOAD_FOLDER'] = MEDIA_PATH
    CORS(app)
    app.register_blueprint(bundle_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(frontend_bp)

    # Evita iniciar rotinas duas vezes no reloader do Flask
    if start_background_routines and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=start_routines, daemon=True).start()

    return app

if __name__ == '__main__':
    logger("\n\n")
    logger("=======================================================================")
    logger("                         inciando o chainTransfer")
    logger("=======================================================================")
    create_tables()
    parser = argparse.ArgumentParser()
    parser.add_argument('--only-api', action='store_true', help='Inicia apenas o servidor Flask.')
    parser.add_argument('--only-routine', action='store_true', help='Inicia apenas a rotina DTN.')
    args = parser.parse_args()

    host_ip = meu_ip()
    # host_ip = "0.0.0.0"

    if args.only_api:
        app = create_app(start_background_routines=False)
        app.run(host=host_ip, port=3000, debug=True)
    elif args.only_routine:
        start_routines()
    else:
        app = create_app(start_background_routines=True)
        app.run(host=host_ip, port=3000, debug=True)
