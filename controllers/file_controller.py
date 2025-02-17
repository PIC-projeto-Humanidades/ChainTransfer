from flask import Blueprint, request, jsonify, send_from_directory
from services.file_service import save_file, list_files, get_file
import os

file_bp = Blueprint('files', __name__)
UPLOAD_FOLDER = './medias'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

@file_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    file = request.files['file']
    filename, file_id = save_file(file, UPLOAD_FOLDER, ALLOWED_EXTENSIONS)
    if filename:
        return jsonify({'message': f'Arquivo {filename} salvo com sucesso', 'file_id': file_id}), 200
    return jsonify({'error': 'Tipo de arquivo não permitido'}), 400

@file_bp.route('/', methods=['GET'])
def list_all_files():
    files = list_files(UPLOAD_FOLDER)
    return jsonify({'files': files}), 200

@file_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    if get_file(filename, UPLOAD_FOLDER):
        return send_from_directory(UPLOAD_FOLDER, filename)
    return jsonify({'error': 'Arquivo não encontrado'}), 404