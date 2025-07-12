import json
from pathlib import Path

# Caminho para o arquivo de configuração
CONFIG_PATH = Path(__file__).resolve().parent.parent / "network_config.json"

# Carrega o conteúdo do JSON uma vez
with open(CONFIG_PATH, "r") as f:
    config_data = json.load(f)

# services/network_service.py

import json
from pathlib import Path

def meu_ip() -> str:
    """
    Lê o campo 'meu_ip' de network_config.json no root do projeto.
    """
    # Ajuste o path conforme a estrutura do seu projeto
    config_path = Path(__file__).resolve().parent.parent / "network_config.json"
    with open(config_path, "r") as f:
        cfg = json.load(f)
    ip = cfg.get("meu_ip")
    if not ip:
        raise ValueError(f"'meu_ip' não encontrado em {config_path}")
    return ip


def routes():
    """Retorna os nós da rede, exceto o próprio IP."""
    all_nodes = config_data.get("routes", [])
    return [node for node in all_nodes if node["ip"] != meu_ip()]
