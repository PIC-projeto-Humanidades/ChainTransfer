from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from pathlib import Path
import shutil
from logs.log_f import log_f as logger  
import hashlib    
from services.network_service import meu_ip
from services.metrics_service import log_envio
from time import time

files_bp = Blueprint("files", __name__)

# Defina os caminhos
BASE_PATH      = Path(__file__).resolve().parent.parent
UPLOAD_PATH    = BASE_PATH / "upload_files"
MEDIA_PATH     = BASE_PATH / "media_data"

# Assegura que as pastas existam
for p in (UPLOAD_PATH, MEDIA_PATH):
    p.mkdir(parents=True, exist_ok=True)

@files_bp.route("/upload", methods=["POST"])
def upload_file():
    """
    Recebe um arquivo via form-data (campo 'file') e salva em upload_files.
    Aceita qualquer tipo/mime (vídeo, áudio, binário, etc.).
    """
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    f = request.files["file"]
    filename = secure_filename(f.filename)

    upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
    upload_dir.mkdir(parents=True, exist_ok=True)

    dest_path = upload_dir / filename
    # Usa stream do werkzeug, em chunks, para não estourar memória
    with open(dest_path, "wb") as out_f:
        chunk_size = 4096
        while True:
            chunk = f.stream.read(chunk_size)
            if not chunk:
                break
            out_f.write(chunk)

    return jsonify({"filename": filename, "status": "uploaded"}), 201

@files_bp.route("/files", methods=["GET"])
def list_files():
    """
    Lista arquivos em:
      - upload_files  (query param ?type=upload)
      - media_data    (query param ?type=media)
      - ambos (sem param)
    """
    tipo = request.args.get("type", "").lower()
    result = {}
    if tipo in ("upload", ""):
        result["upload_files"] = [p.name for p in UPLOAD_PATH.iterdir() if p.is_file()]
    if tipo in ("media", ""):
        result["media_data"] = [p.name for p in MEDIA_PATH.iterdir() if p.is_file()]
    return jsonify(result), 200

@files_bp.route("/files/approve", methods=["POST"])
def approve_file():
    """
    Aprova ou recusa um arquivo em upload_files.
    Se aprovar, antes de mover para media_data,
    renomeia acrescentando um hash baseado no IP do servidor.
    JSON esperado:
      {
        "filename": "nome.ext",
        "approve": true|false
      }
    """
    data = request.get_json(force=True)
    filename = data.get("filename")
    approve  = data.get("approve")

    if not filename or approve is None:
        return jsonify({"error": "Parâmetros 'filename' e 'approve' são obrigatórios"}), 400

    src = UPLOAD_PATH / filename
    if not src.exists() or not src.is_file():
        return jsonify({"error": "Arquivo não encontrado em upload_files"}), 404

    if approve:
        stem   = src.stem
        suffix = src.suffix
        ip_servidor = meu_ip()
        to_hash = f"{stem}-{ip_servidor}".encode('utf-8')
        full_hash = hashlib.sha256(to_hash).hexdigest()
        short_hash = full_hash[:8]
        new_name = f"{stem}-{short_hash}{suffix}"
        dest     = MEDIA_PATH / new_name
        t_inicio = time()
        try:
            shutil.move(str(src), str(dest))
            t_fim = time()
            # Registra métrica de envio
            log_envio(
                arquivo=new_name,
                tamanho_bytes=dest.stat().st_size if dest.exists() else 0,
                destino=ip_servidor,
                tentativa=1,
                resultado="sucesso",
                motivo_falha="",
                timestamp_inicio=str(t_inicio),
                timestamp_fim=str(t_fim)
            )
            logger(f"✅ Arquivo aprovado e movido: {filename} → {new_name}")
            return jsonify({
                "original": filename,
                "new_name": new_name,
                "status": "moved to media_data"
            }), 200
        except Exception as e:
            t_fim = time()
            log_envio(
                arquivo=new_name,
                tamanho_bytes=0,
                destino=ip_servidor,
                tentativa=1,
                resultado="falha",
                motivo_falha=str(e),
                timestamp_inicio=str(t_inicio),
                timestamp_fim=str(t_fim)
            )
            logger(f"❌ Erro ao mover {filename}: {e}")
            return jsonify({"error": f"Falha ao mover arquivo: {e}"}), 500

    else:
        # recusar → deletar
        try:
            src.unlink()
            logger(f"🗑️ Arquivo recusado e deletado: {filename}")
            return jsonify({
                "filename": filename,
                "status": "deleted from upload_files"
            }), 200
        except Exception as e:
            logger(f"❌ Erro ao deletar {filename}: {e}")
            return jsonify({"error": f"Falha ao deletar arquivo: {e}"}), 500