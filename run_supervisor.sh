#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONNECT_SCRIPT="$BASE_DIR/mesh_connect.sh"
APP_SCRIPT="$BASE_DIR/app.py"
CFG_FILE="$BASE_DIR/network_config.json"
REQ_FILE="$BASE_DIR/requirements.txt"

# Função: verifica porta e mata qualquer processo que esteja escutando nela
free_port() {
  local port=$1
  # Obtém PIDs escutando na porta
  pids=$(lsof -ti :"$port" || true)
  if [[ -n "$pids" ]]; then
    echo ">>> Porta $port está em uso pelos PIDs: $pids. Finalizando-os..."
    kill -9 $pids
    echo ">>> Porta $port liberada."
  fi
}

# 1) python3 + pip3
if ! command -v python3 &>/dev/null || ! command -v pip3 &>/dev/null; then
  echo "❯ Instalando python3 e pip3..."
  sudo apt update
  sudo apt install -y python3 python3-pip
fi

# 2) libs Python
if [[ -f "$REQ_FILE" ]]; then
  echo "❯ Instalando dependências Python..."
  pip3 install --user -r "$REQ_FILE"
fi

# 3) valida arquivos
for f in "$CONNECT_SCRIPT" "$APP_SCRIPT" "$CFG_FILE"; do
  [[ -e "$f" ]] || { echo "❌ Arquivo $f não encontrado"; exit 1; }
done
[[ -x "$CONNECT_SCRIPT" ]] || chmod +x "$CONNECT_SCRIPT"

# 4) ativa autoconnect NM
nmcli con modify mesh-auto connection.autoconnect yes connection.autoconnect-retries 0 &>/dev/null || true

echo "=== Supervisor de Mesh + App iniciado ==="
echo "Pressione Ctrl+C para encerrar."

while true; do
  echo ">>> Estabelecendo mesh..."
  "$CONNECT_SCRIPT"

  # Antes de subir o Flask, libera a porta 3000
  free_port 3000

  echo "+++ Mesh OK. Iniciando app.py na porta 3000..."
  python3 "$APP_SCRIPT" &
  APP_PID=$!

  # MONITORAMENTO: verifica se 'mesh-auto' continua ativa
  echo ">>> Monitorando conexão mesh-auto..."
  while nmcli -t -f NAME,DEVICE con show --active | grep -q '^mesh-auto:'; do
    sleep 5
  done

  echo "*** Mesh perdeu o active-connection. Finalizando app.py (PID=$APP_PID)..."
  kill "$APP_PID" 2>/dev/null || true
  wait "$APP_PID" 2>/dev/null || true

  echo ">>> Mesh caiu. Reiniciando em 2s..."
  sleep 2
done
