#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONNECT_SCRIPT="$BASE_DIR/mesh_connect.sh"
APP_SCRIPT="$BASE_DIR/app.py"
CFG_FILE="$BASE_DIR/network_config.json"
REQ_FILE="$BASE_DIR/requirements.txt"

# Descobre usuário não-root (quem invocou sudo)
# Se não estiver usando sudo, cai para $USER
if [[ -n "${SUDO_USER-}" && "$SUDO_USER" != "root" ]]; then
  RUN_USER="$SUDO_USER"
else
  RUN_USER="$USER"
fi

# Detecta interface Wi-Fi
WIFI_IF=$(nmcli -t -f DEVICE,TYPE dev status | awk -F: '$2=="wifi"{print $1; exit}')
[[ -n "$WIFI_IF" ]] || { echo "❌ Sem interface Wi-Fi"; exit 1; }

FLASK_PID=""

cleanup() {
  echo
  echo "🛑 Supervisor encerrando…"
  if [[ -n "$FLASK_PID" ]]; then
    echo "  → Matando Flask (PID=$FLASK_PID)…"
    kill "$FLASK_PID" 2>/dev/null || true
    wait "$FLASK_PID" 2>/dev/null || true
  fi
  exit 0
}
trap cleanup EXIT INT TERM

# Libera porta (mantém em root)
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

# Garante python3 + pip3 (aqui pode continuar como root)
if ! command -v python3 &>/dev/null || ! command -v pip3 &>/dev/null; then
  echo "❯ Instalando python3/pip3…"
  sudo apt update && sudo apt install -y python3 python3-pip
fi

# Instala dependências no home do RUN_USER
if [[ -f "$REQ_FILE" ]]; then
  echo "❯ Instalando dependências Python como $RUN_USER…"
  sudo -u "$RUN_USER" pip3 install --user -r "$REQ_FILE"
fi

# Verifica arquivos
for f in "$CONNECT_SCRIPT" "$APP_SCRIPT" "$CFG_FILE"; do
  [[ -e "$f" ]] || { echo "❌ $f não encontrado"; exit 1; }
done
[[ -x "$CONNECT_SCRIPT" ]] || chmod +x "$CONNECT_SCRIPT"

echo "=== Supervisor Mesh + Flask ==="
echo "Usuário Flask: $RUN_USER — SSID: $SSID, IF: $WIFI_IF, Porta: $MEU_PORT"
echo "Pressione Ctrl+C para encerrar."

while true; do
  echo ">>> (Re)associando ao SSID '$SSID'…"
  "$CONNECT_SCRIPT" "$SSID"

  echo "+++ Associação OK. Liberando porta $MEU_PORT e iniciando Flask como $RUN_USER…"
  free_port "$MEU_PORT"

  # Inicia o Flask COMO usuário normal
  sudo -u "$RUN_USER" python3 "$APP_SCRIPT" &
  FLASK_PID=$!
  echo "    Flask iniciado com PID=$FLASK_PID (usuário: $RUN_USER)"

  echo ">>> Monitorando estado da interface '$WIFI_IF'…"
  # Enquanto continuar conectado, mantém o Flask
  while nmcli -t -f DEVICE,STATE dev status | grep -q "^${WIFI_IF}:connected$"; do
    sleep 5
  done

  echo "*** Interface saiu do estado connected! Matando Flask…"
  kill "$FLASK_PID" 2>/dev/null || true
  wait "$FLASK_PID" 2>/dev/null || true
  FLASK_PID=""

  echo ">>> Aguardando 2s antes de tentar reconectar…"
  sleep 2
done
