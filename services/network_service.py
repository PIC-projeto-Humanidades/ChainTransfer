import json
from pathlib import Path

# Caminho para o arquivo de configuração
CONFIG_PATH = Path(__file__).resolve().parent.parent / "network_config.json"

# Carrega o conteúdo do JSON uma vez
with open(CONFIG_PATH, "r") as f:
    config_data = json.load(f)

def meu_ip():
    """Retorna o IP da própria máquina."""
    return config_data.get("meu_ip")

def routes():
    """Retorna os nós da rede, exceto o próprio IP."""
    all_nodes = config_data.get("routes", [])
    return [node for node in all_nodes if node["ip"] != meu_ip()]
