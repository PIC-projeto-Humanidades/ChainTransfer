from utils.is_uuid import is_uuid
import uuid
from pathlib import Path
import os
MEDIA_PATH = Path(os.getcwd()) / "media_data"


def check_and_rename_files():
    if not MEDIA_PATH.exists():
        MEDIA_PATH.mkdir(parents=True)
    for file in MEDIA_PATH.iterdir():
        if not file.is_file():
            continue
        if not '-' in file.stem or not is_uuid(file.stem.split('-')[-1]):
            new_name = f"{file.stem}-{uuid.uuid4()}{file.suffix}"
            new_path = MEDIA_PATH / new_name
            file.rename(new_path)
            print(f"Arquivo renomeado: {file.name} -> {new_name}")
    print("Verificação de nomenclatura de arquivos concluída.")
