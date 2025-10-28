import os
from flask import send_file, abort

METRICS_FILE = os.path.join(os.path.dirname(__file__), '../logs/metrics_envio.csv')

def get_metrics_file_path():
    return METRICS_FILE

def download_metrics():
    if not os.path.isfile(METRICS_FILE):
        abort(404, description='Arquivo de métricas não encontrado.')
    return send_file(METRICS_FILE, as_attachment=True, download_name='metrics_envio.csv')
