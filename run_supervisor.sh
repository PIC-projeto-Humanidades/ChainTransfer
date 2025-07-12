#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONNECT_SCRIPT="$BASE_DIR/mesh_connect.sh"
APP_SCRIPT="$BASE_DIR/app.py"
CFG_FILE="$BASE_DIR/network_config.json"
REQ_FILE="$BASE_DIR/requirements.txt"

# Carrega SSID e porta do JSON
SSID=$(jq -r '.ssid' "$CFG_FILE")
MEU_PORT=${PORT:-3000}

# Detecta interface Wi-Fi (uma vez)
WIFI_IF=$(nmcli -t -f DEVICE,TYPE dev status | awk -F: '$2=="wifi"{print $1; exit}')
[[ -n "$WIFI_IF" ]] || { echo "❌ Sem interface Wi-Fi"; exit 1; }

# Função: libera a porta, matando quem estiver nela
free_port() {
  local port=$1
  local pids
  pids=$(lsof -ti :"$port" || true)
  if [[ -n "$pids" ]]; then
    echo ">>> Porta $port ocupada pelos PIDs: $pids. Matando..."
    kill -9 $pids
    echo ">>> Porta $port liberada."
  fi
}

# 1) Garante python3 + pip3
if ! command -v python3 &>/dev/null || ! command -v pip3 &>/dev/null; then
  echo "❯ Instalando python3/pip3..."
  sudo apt update && sudo apt install -y python3 python3-pip
fi

# 2) Instala dependências Python
if [[ -f "$REQ_FILE" ]]; then
  echo "❯ Instalando dependências Python..."
  pip3 install --user -r "$REQ_FILE"
fi

# 3) Verifica scripts e config
for f in "$CONNECT_SCRIPT" "$APP_SCRIPT" "$CFG_FILE"; do
  [[ -e "$f" ]] || { echo "❌ $f não encontrado"; exit 1; }
done
[[ -x "$CONNECT_SCRIPT" ]] || chmod +x "$CONNECT_SCRIPT"

echo "=== Supervisor Mesh + Flask ==="
echo "SSID: $SSID, Interface: $WIFI_IF, Porta: $MEU_PORT"
echo "Pressione Ctrl+C para encerrar."

while true; do
  echo ">>> (Re)associando ao SSID '$SSID'…"
  "$CONNECT_SCRIPT" "$SSID"

  echo "+++ Associação OK. Liberando porta $MEU_PORT e iniciando Flask…"
  free_port "$MEU_PORT"
  # Chama o app sem flags indesejadas
  python3 "$APP_SCRIPT" &
  FLASK_PID=$!

  echo ">>> Monitorando estado da interface '$WIFI_IF'…"
  # Enquanto a interface estiver CONNECTED, mantém o Flask
  while nmcli -t -f DEVICE,STATE dev status | grep -q "^${WIFI_IF}:connected$"; do
    sleep 5
  done

  echo "*** Interface '$WIFI_IF' saiu do state connected! Matando Flask (PID=$FLASK_PID)…"
  kill "$FLASK_PID" 2>/dev/null || true
  wait "$FLASK_PID" 2>/dev/null || true

  echo ">>> Aguardando 2s antes de tentar reconectar…"
  sleep 2
done
