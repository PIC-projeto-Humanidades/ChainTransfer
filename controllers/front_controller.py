from flask import Blueprint, send_from_directory, current_app
from pathlib import Path

frontend_bp = Blueprint('frontend', __name__, url_prefix='')  

@frontend_bp.route('/', defaults={'path': ''})
@frontend_bp.route('/<path:path>')
def serve_frontend(path):
    """
    Serve arquivos estáticos do frontend gerado pelo Next.js.
    Se o arquivo existir, retorna-o; caso contrário, retorna index.html para permitir roteamento no cliente.
    """
    # Define o diretório do build estático dinamicamente
    static_dir = Path(current_app.root_path) / 'static_frontend'

    # Se o caminho for para um arquivo existente, retorna-o diretamente
    target = static_dir / path
    if path and target.exists() and target.is_file():
        return send_from_directory(str(static_dir), path)

    # Caso contrário, serve o index.html para permitir o roteamento do SPA
    return send_from_directory(str(static_dir), 'index.html')
