from pathlib import Path
import os
import stat

LOG_FILE = Path.cwd() / "logs" / "app.txt"

def log_f(msg: str):
    # 1) Garante que a pasta exista (com permissão 775)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True, mode=0o775)

    # 2) Se o arquivo não existe, cria-o e ajusta permissões
    if not LOG_FILE.exists():
        LOG_FILE.touch()
        # leitura e escrita para dono, grupo e outros (0666)
        os.chmod(LOG_FILE, 0o666)

    # 3) Append normalmente
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{msg}\n")
