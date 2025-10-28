from flask import Blueprint, send_file, abort
import os
from services.metrics_download_service import download_metrics

METRICS_FILE = os.path.join(os.path.dirname(__file__), '../logs/metrics_envio.csv')
metrics_bp = Blueprint('metrics', __name__)

def get_metrics_file():
    if not os.path.isfile(METRICS_FILE):
        return None
    return METRICS_FILE

@metrics_bp.route('/metrics/download', methods=['GET'])
def download_metrics():
    file_path = get_metrics_file()
    if not file_path:
        abort(404, 'Arquivo de métricas não encontrado.')
    return send_file(
        file_path,
        as_attachment=True,
        download_name='metrics_envio.csv',
        mimetype='text/csv',
        max_age=0
    )

@metrics_bp.route('/download', methods=['GET'])
def download_metrics_route():
    return download_metrics()
