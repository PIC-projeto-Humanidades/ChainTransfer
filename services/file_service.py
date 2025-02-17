import os
from werkzeug.utils import secure_filename
from repositories.log_repository import save_log
import uuid

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, upload_folder, allowed_extensions):
    if file and allowed_file(file.filename, allowed_extensions):
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        file_id = str(uuid.uuid4())
        file.save(filepath)
        save_log(file_id, f"Arquivo {filename} salvo.")
        return filename, file_id
    return None, None

def list_files(upload_folder):
    files = os.listdir(upload_folder)
    for file in files:
        file_id = str(uuid.uuid4())  # Gerando um ID único para cada arquivo listado
        save_log(file_id, f"Arquivo {file} listado.")
    return files

def get_file(filename, upload_folder):
    if filename in os.listdir(upload_folder):
        return filename
    return None