import argparse
from flask import Flask
from controllers.bundle_controller import bundle_bp
from controllers.file_controller import file_bp
import threading
from database.migrator import create_tables   
from services.routines import start_routines   
from services.network_service import meu_ip

def create_app(start_background_routines=True):
    app = Flask(__name__)
    app.register_blueprint(bundle_bp)
    app.register_blueprint(file_bp)

    if start_background_routines:
        # Executa as rotinas DTN em thread paralela
        threading.Thread(target=start_routines, daemon=True).start()

    return app

if __name__ == '__main__':
    create_tables()
    parser = argparse.ArgumentParser()
    parser.add_argument('--only-api', action='store_true', help='Inicia apenas o servidor Flask.')
    parser.add_argument('--only-routine', action='store_true', help='Inicia apenas a rotina DTN.')
    args = parser.parse_args()
    host_ip = meu_ip()                # retorna o IP cujo MAC é seu meu_mac
    if args.only_api:
        app = create_app(start_background_routines=False)
        app.run(host=host_ip, port=3000, debug=True)
    elif args.only_routine:
        start_routines()
    else:
        app = create_app(start_background_routines=True)
        app.run(host=host_ip, port=3000, debug=True)
