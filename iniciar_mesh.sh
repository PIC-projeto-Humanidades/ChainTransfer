#!/bin/bash

: '
📡 Script: iniciar_mesh.sh
🧠 Propósito:
  Inicia uma rede mesh Wi-Fi (modo Ad-Hoc/IBSS) em Linux,
  atribuindo o IP fixo definido em network_config.json.
  Logs de debug vão para stderr; stdout só retorna o IP.
'

SSID="RedeMeshDTN"
CHANNEL="6"

# Detecta o diretório onde o script está
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/network_config.json"

# Pacotes necessários (batctl traz o módulo batman_adv)
PACOTES=("wireless-tools" "iw" "net-tools" "jq" "batctl")

# Função de log -> stderr
log() { echo -e "[$(date '+%H:%M:%S')] $*" >&2; }

verificar_pacotes() {
  local missing=()
  for pkg in "${PACOTES[@]}"; do
    if ! dpkg -s "$pkg" &>/dev/null; then
      missing+=("$pkg")
    fi
  done
  if [ ${#missing[@]} -gt 0 ]; then
    log "📦 Instalando: ${missing[*]}"
    sudo apt update
    sudo apt install -y "${missing[@]}"
  else
    log "✅ Pacotes OK"
  fi
}

detectar_interface() {
  INTERFACE=$(iw dev | awk '$1=="Interface"{print $2}' | head -n1)
  [ -z "$INTERFACE" ] && { log "❌ Sem interface Wi-Fi"; exit 1; }
  log "🔍 Wi-Fi: $INTERFACE"
}

verificar_ibss() {
  iw list | grep -q "IBSS" || { log "❌ IBSS não suportado"; exit 1; }
}

# Lê somente o IP (stdout) e envia debug para stderr
gerar_ip() {
  log "🔎 CONFIG_FILE = $CONFIG_FILE"
  [ ! -f "$CONFIG_FILE" ] && { log "❌ Arquivo não existe"; exit 1; }

  log "📄 Conteúdo de $CONFIG_FILE:"
  sed -e 's/^/    /' "$CONFIG_FILE" >&2

  local ip
  ip=$(jq -r '.meu_ip // empty' "$CONFIG_FILE") || {
    log "❌ jq falhou"; exit 1;
  }
  [ -z "$ip" ] && { log "❌ campo 'meu_ip' vazio"; exit 1; }

  log "🖧 Meu IP do JSON: $ip"
  echo "$ip"
}

iniciar_mesh() {
  local IP
  IP=$(gerar_ip)

  log "📴 Limpando $INTERFACE"
  nmcli dev disconnect "$INTERFACE" &>/dev/null || true
  sudo systemctl stop NetworkManager &>/dev/null || true
  sudo ip link set "$INTERFACE" down
  sudo ip addr flush dev "$INTERFACE"

  log "🔧 Montando IBSS em $INTERFACE (SSID=$SSID, canal=$CHANNEL)"
  sudo iwconfig "$INTERFACE" mode ad-hoc
  sudo iwconfig "$INTERFACE" essid "$SSID"
  sudo iwconfig "$INTERFACE" channel "$CHANNEL"
  sudo ip link set "$INTERFACE" up

  log "🛠️  Configurando batman-adv"
  sudo modprobe batman_adv
  sudo batctl if del "$INTERFACE" &>/dev/null || true
  sudo batctl if add "$INTERFACE"
  sudo ip link set up dev bat0

  log "📡 Habilitando ip_forward e limpando iptables"
  sudo sysctl -w net.ipv4.ip_forward=1 &>/dev/null
  sudo iptables -F

  log "📌 Atribuindo IP $IP/24 em bat0"
  sudo ip addr add "$IP"/24 dev bat0

  log "✅ Mesh pronta em bat0 com IP $IP"
}

# Execução
verificar_pacotes
detectar_interface
verificar_ibss
iniciar_mesh
