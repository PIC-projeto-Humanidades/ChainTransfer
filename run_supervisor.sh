#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Define RUN_USER globalmente para uso em qualquer função
RUN_USER="${SUDO_USER:-$USER}"
[[ "$RUN_USER" == "root" ]] && RUN_USER="$USER"

CONNECT_SCRIPT="$BASE_DIR/mesh_connect.sh"
APP_SCRIPT="$BASE_DIR/app.py"
CFG_FILE="$BASE_DIR/network_config.json"
REQ_FILE="$BASE_DIR/requirements.txt"

PID_FILE="$BASE_DIR/supervisor.pid"
LOG_FILE="$BASE_DIR/logs/supervisor.log"
APP_LOG_DIR="$BASE_DIR/logs"
APP_LOG_FILE="$APP_LOG_DIR/app.txt"

# Garante diretório logs e permissões corretas
LOGS_DIR="$BASE_DIR/logs"
METRICS_FILE="$LOGS_DIR/metrics_envio.csv"

mkdir -p "$LOGS_DIR"
chown "$RUN_USER" "$LOGS_DIR"
chmod 755 "$LOGS_DIR"

if [[ -f "$METRICS_FILE" ]]; then
  chown "$RUN_USER" "$METRICS_FILE"
  chmod 644 "$METRICS_FILE"
fi

# ------------------------------------------------------------------
# Subcomando interno: loop principal
if [[ "${1:-}" == "__run" ]]; then
  shift
  WIFI_IF=$(nmcli -t -f DEVICE,TYPE dev status | awk -F: '$2=="wifi"{print $1; exit}')
  [[ -n "$WIFI_IF" ]] || { echo "❌ Sem interface Wi-Fi"; exit 1; }
  SSID=$(jq -r '.ssid' "$CFG_FILE")
  MEU_PORT=${PORT:-3000}

  mkdir -p "$APP_LOG_DIR"
  mkdir -p "$BASE_DIR/download_processamento"
  mkdir -p "$BASE_DIR/media_data"
  mkdir -p "$BASE_DIR/upload_files"
  if [[ ! -f "$APP_LOG_FILE" ]]; then
    touch "$APP_LOG_FILE"
    chown "$RUN_USER" "$APP_LOG_FILE"
  elif [[ ! -w "$APP_LOG_FILE" ]]; then
    rm -f "$APP_LOG_FILE"
    touch "$APP_LOG_FILE"
    chown "$RUN_USER" "$APP_LOG_FILE"
  else
    chown "$RUN_USER" "$APP_LOG_FILE"
  fi
  CRITICAL_LOG_FILE="$APP_LOG_DIR/critical_errors.txt"
  if [[ ! -f "$CRITICAL_LOG_FILE" ]]; then
    touch "$CRITICAL_LOG_FILE"
    chown "$RUN_USER" "$CRITICAL_LOG_FILE"
  elif [[ ! -w "$CRITICAL_LOG_FILE" ]]; then
    rm -f "$CRITICAL_LOG_FILE"
    touch "$CRITICAL_LOG_FILE"
    chown "$RUN_USER" "$CRITICAL_LOG_FILE"
  else
    chown "$RUN_USER" "$CRITICAL_LOG_FILE"
  fi
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
  if [[ -n "${2:-}" ]]; then
    case "${2}" in
      -start)
        echo "-start: Inicia o supervisor em background, gerenciando a associação à rede mesh e o servidor Flask."
        ;;
      -stop)
        echo "-stop: Para o supervisor em execução, encerrando todos os processos relacionados."
        ;;
      -restart)
        echo "-restart: Reinicia o supervisor (executa stop seguido de start)."
        ;;
      -status)
        echo "-status: Exibe se o supervisor está rodando e mostra o PID do processo."
        ;;
      -logs)
        echo "-logs [--supervisor|--app|--all]: Mostra os logs em tempo real. --supervisor exibe apenas o log do supervisor, --app apenas o log da aplicação, --all ambos em paralelo."
        ;;
      -init)
        echo "-init: Cria e habilita o serviço systemd para inicializar o supervisor automaticamente junto ao sistema."
        ;;
      -rminit)
        echo "-rminit: Remove e desabilita o serviço systemd de inicialização automática do supervisor."
        ;;
      -help|--help)
        echo "-help, --help: Exibe esta ajuda geral ou detalhes de um comando específico."
        ;;
      *)
        echo "Comando não reconhecido. Use '$0 -help' para ver os comandos disponíveis."
        ;;
    esac
    return
  fi
  cat <<EOF
Uso: $0 <comando> [opções]

Comandos disponíveis:
  -start                Inicia o supervisor em background
  -stop                 Para o supervisor em execução
  -restart              Reinicia o supervisor (stop + start)
  -status               Exibe se o supervisor está rodando (PID)
  -logs [opção]         Mostra os logs:
    --supervisor          Exibe apenas o log do supervisor
    --app                 Exibe apenas o log da aplicação
    --all (padrão)        Exibe ambos os logs em paralelo
  -init                 Configura inicialização automática do supervisor (systemd)
  -rminit               Remove a inicialização automática do supervisor (systemd)
  -help, --help         Exibe esta ajuda ou detalhes de um comando

Exemplos de uso:
  $0 -start
  $0 -init
  $0 -stop
  $0 -logs --all
  $0 -logs --app
  $0 -status
  $0 -rminit
  $0 -help
  $0 --help -start

Observações:
- O comando -init cria e habilita o serviço systemd para inicializar o supervisor automaticamente junto ao sistema.
- O comando -rminit remove o serviço systemd criado para inicialização automática.
- Os logs são exibidos em tempo real (tail -f).
- Use '$0 --help <comando>' para detalhes de um comando específico.
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

function init() {
  SERVICE_FILE="/etc/systemd/system/chaintransfer-supervisor.service"
  if [[ ! -f "$SERVICE_FILE" ]]; then
    echo "[Unit]" | sudo tee "$SERVICE_FILE" > /dev/null
    echo "Description=ChainTransfer Supervisor" | sudo tee -a "$SERVICE_FILE" > /dev/null
    echo "After=network.target" | sudo tee -a "$SERVICE_FILE" > /dev/null
    echo "[Service]" | sudo tee -a "$SERVICE_FILE" > /dev/null
    echo "Type=simple" | sudo tee -a "$SERVICE_FILE" > /dev/null
    echo "User=$RUN_USER" | sudo tee -a "$SERVICE_FILE" > /dev/null
    echo "WorkingDirectory=$BASE_DIR" | sudo tee -a "$SERVICE_FILE" > /dev/null
    echo "ExecStart=$BASE_DIR/run_supervisor.sh -start" | sudo tee -a "$SERVICE_FILE" > /dev/null
    echo "Restart=always" | sudo tee -a "$SERVICE_FILE" > /dev/null
    echo "[Install]" | sudo tee -a "$SERVICE_FILE" > /dev/null
    echo "WantedBy=multi-user.target" | sudo tee -a "$SERVICE_FILE" > /dev/null
    sudo systemctl daemon-reload
    sudo systemctl enable chaintransfer-supervisor.service
    echo "Serviço chaintransfer-supervisor.service criado e habilitado para inicializar junto ao sistema."
  else
    echo "Serviço chaintransfer-supervisor.service já está configurado."
  fi
}

function rminit() {
  SERVICE_FILE="/etc/systemd/system/chaintransfer-supervisor.service"
  if [[ -f "$SERVICE_FILE" ]]; then
    echo "Removendo serviço chaintransfer-supervisor.service..."
    sudo systemctl disable chaintransfer-supervisor.service
    sudo systemctl stop chaintransfer-supervisor.service
    sudo rm -f "$SERVICE_FILE"
    sudo systemctl daemon-reload
    echo "Serviço removido e desabilitado."
  else
    echo "Serviço chaintransfer-supervisor.service não está configurado."
  fi
}

# ------------------------------------------------------------------
# Dispatch
case "${1:-}" in
  -start)   start ;;
  -stop)    stop ;;
  -restart) restart ;;
  -status)  status ;;
  -logs)
    case "${2:-}" in
      --supervisor) logs supervisor ;;
      --app)        logs app ;;
      --all | "")   logs all ;;
      *)            logs all ;;
    esac
    ;;
  -init)   init ;;
  -rminit)  rminit ;;
  -help|--help) help "$@" ;;
  *) echo "Comando inválido. Use '$0 -help' para ver os comandos disponíveis." >&2; exit 1 ;;
esac
