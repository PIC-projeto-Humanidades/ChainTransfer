#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONNECT_SCRIPT="$BASE_DIR/mesh_connect.sh"
APP_SCRIPT="$BASE_DIR/app.py"
CFG_FILE="$BASE_DIR/network_config.json"
REQ_FILE="$BASE_DIR/requirements.txt"

PID_FILE="$BASE_DIR/supervisor.pid"
LOG_FILE="$BASE_DIR/logs/supervisor.log"
APP_LOG_DIR="$BASE_DIR/logs"
APP_LOG_FILE="$APP_LOG_DIR/app.txt"

# ------------------------------------------------------------------
# Subcomando interno: loop principal
if [[ "${1:-}" == "__run" ]]; then
  shift
  WIFI_IF=$(nmcli -t -f DEVICE,TYPE dev status | awk -F: '$2=="wifi"{print $1; exit}')
  [[ -n "$WIFI_IF" ]] || { echo "❌ Sem interface Wi-Fi"; exit 1; }
  RUN_USER="${SUDO_USER:-$USER}"
  [[ "$RUN_USER" == "root" ]] && RUN_USER="$USER"
  SSID=$(jq -r '.ssid' "$CFG_FILE")
  MEU_PORT=${PORT:-3000}

  mkdir -p "$APP_LOG_DIR"
  trap 'echo; echo "🛑 Supervisor recebeu sinal de saída."; exit 0' EXIT INT TERM

  if ! command -v python3 &>/dev/null || ! command -v pip3 &>/dev/null; then
    echo "❯ Instalando python3/pip3..."
    sudo apt update && sudo apt install -y python3 python3-pip
  fi
  [[ -f "$REQ_FILE" ]] && sudo -u "$RUN_USER" pip3 install --user -r "$REQ_FILE"

  echo "=== Supervisor Mesh + Flask ===" >>"$LOG_FILE"
  echo "Usuário: $RUN_USER • SSID: $SSID • IF: $WIFI_IF • Porta: $MEU_PORT" >>"$LOG_FILE"
  echo >>"$LOG_FILE"

  while true; do
    echo ">>> (Re)associando a '$SSID'…" >>"$LOG_FILE"
    "$CONNECT_SCRIPT" "$SSID"

    echo "+++ Associação OK. Liberando porta $MEU_PORT…" >>"$LOG_FILE"
    pids=$(lsof -ti :"$MEU_PORT" || true)
    [[ -n "$pids" ]] && kill -9 $pids

    echo ">>> Iniciando Flask como $RUN_USER…" >>"$LOG_FILE"
    sudo -u "$RUN_USER" python3 "$APP_SCRIPT" >>"$APP_LOG_FILE" 2>&1 &
    FLASK_PID=$!

    echo ">>> Monitorando interface $WIFI_IF…" >>"$LOG_FILE"
    while nmcli -t -f DEVICE,STATE dev status | grep -q "^${WIFI_IF}:connected$" \
      && nmcli -t -f SSID,DEVICE dev wifi | grep -q "^${SSID}:${WIFI_IF}$"
    do
      sleep 5
    done

    echo "*** Interface desconectou! Matando Flask (PID=$FLASK_PID)…" >>"$LOG_FILE"
    kill "$FLASK_PID" || true

    echo ">>> Aguardando 2s antes de reconectar…" >>"$LOG_FILE"
    sleep 2
  done
fi

# ------------------------------------------------------------------
# Funções de controle

function help() {
  cat <<EOF
Uso: $0 <comando> [args]

Comandos:
  start            Inicia o supervisor em background
  stop             Para o supervisor em execução
  restart          Reinicia o supervisor (stop + start)
  status           Exibe se o supervisor está rodando (PID)
  logs [modo]      Mostra os logs:
                     supervisor  – apenas supervisor.log
                     app         – apenas logs/app.txt
                     all (padrão)– ambos em paralelo
  help, -h, --help Exibe esta ajuda
EOF
}

function start() {
  if [[ -f "$PID_FILE" && -d /proc/$(<"$PID_FILE") ]]; then
    echo "Supervisor já está em execução (PID=$(<"$PID_FILE"))"
    return 1
  fi
  echo "Iniciando supervisor em background..."
  nohup bash "$0" __run >>"$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  echo "Supervisor iniciado (PID=$(<"$PID_FILE"))"
}

function stop() {
  if [[ ! -f "$PID_FILE" ]]; then
    echo "Supervisor não está em execução."
    return 1
  fi

  PID=$(<"$PID_FILE")
  # obtém o process group id
  PGID=$(ps -o pgid= "$PID" | tr -d ' ')

  echo "Parando supervisor (PID=$PID, PGID=$PGID)…"
  # mata todo o session/process group
  kill -TERM -"${PGID}" 2>/dev/null || true
  # garantia extra: mata quaisquer filhos diretos restantes
  pkill -TERM -P "$PID" 2>/dev/null || true

  sleep 1
  rm -f "$PID_FILE"
  echo "Supervisor parado."
}



function status() {
  if [[ -f "$PID_FILE" && -d /proc/$(<"$PID_FILE") ]]; then
    echo "Supervisor em execução (PID=$(<"$PID_FILE"))"
  else
    echo "Supervisor não está em execução."
    return 1
  fi
}

function logs() {
  mode=${2:-all}
  case "$mode" in
    supervisor)
      [[ -f "$LOG_FILE" ]] || { echo "Nenhum log do supervisor."; return 1; }
      tail -n50 -f "$LOG_FILE"
      ;;
    app)
      [[ -f "$APP_LOG_FILE" ]] || { echo "Nenhum log da aplicação."; return 1; }
      tail -n50 -f "$APP_LOG_FILE"
      ;;
    all)
      [[ -f "$LOG_FILE" ]] || echo "[sem logs supervisor]"
      [[ -f "$APP_LOG_FILE" ]] || echo "[sem logs app]"
      tail -n50 -f "$LOG_FILE" "$APP_LOG_FILE"
      ;;
    *)
      echo "Uso: $0 logs {supervisor|app|all}"
      return 1
      ;;
  esac
}

function restart() {
  echo "Reiniciando supervisor..."
  stop
  start
}

# ------------------------------------------------------------------
# Dispatch
case "${1:-}" in
  start)   start ;;
  stop)    stop ;;
  restart) restart ;;
  status)  status ;;
  logs)    logs "$@" ;;
  help|-h|--help) help ;;
  *) echo "Comando inválido. Use '$0 help' para ver os comandos disponíveis." >&2; exit 1 ;;
esac
