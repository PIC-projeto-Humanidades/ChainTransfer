from pathlib import Path
import os
import stat

LOG_FILE = Path.cwd() / "logs" / "app.txt"

def log_f(msg: str):
    # 1) Garante que a pasta exista
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 2) Se o arquivo não existe, cria-o e ajusta permissões
    if not LOG_FILE.exists():
        # cria o arquivo vazio
        LOG_FILE.touch()
        # dá permissão de leitura/escrita para todos os usuários do grupo e dono
        os.chmod(LOG_FILE, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)

    # 3) Abre em modo append (já cria se por algum motivo não existisse)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{msg}\n")
