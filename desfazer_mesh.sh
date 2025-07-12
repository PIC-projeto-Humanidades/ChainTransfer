#!/bin/bash
set -euo pipefail

: '
📡 Script: iniciar_mesh_batman.sh
🧠 Propósito:
  Cria uma rede mesh usando Batman-adv sobre um enlace IBSS mínimo.

📋 Requisitos:
  - Interface Wi-Fi com suporte IBSS
  - Pacotes: batctl, wireless-tools, iw, iproute2, jq
  - kernel com módulo batman_adv disponível
'

SSID="RedeMeshDTN"
CHANNEL="6"
BASE_IP="10.0.0"
CONFIG_PATH="$(dirname "$(realpath "$0")")/network_config.json"
PACOTES=("batctl" "wireless-tools" "iw" "iproute2" "jq")

# 1. Instalação de pacotes
install_pkgs() {
  local miss=()
  for p in "${PACOTES[@]}"; do
    dpkg -s "$p" &>/dev/null || miss+=("$p")
  done
  if [ ${#miss[@]} -gt 0 ]; then
    echo "📦 Instalando: ${miss[*]}"
    sudo apt update
    sudo apt install -y "${miss[@]}"
  else
    echo "✅ Pacotes batctl, iw, iproute2, wireless-tools e jq presentes."
  fi
}

# 2. Detecta interface física
detect_iface() {
  IFACE=$(iw dev | awk '$1=="Interface"{print $2}' | grep -v '^mesh' | head -n1)
  [ -n "${IFACE:-}" ] || { echo "❌ Nenhuma interface Wi-Fi detectada"; exit 1; }
  echo "🔍 Interface: $IFACE"
}

# 3. Carrega IP fixo se houver
load_ip() {
  IP_FIXED=""
  if [[ -f "$CONFIG_PATH" ]]; then
    IP_FIXED=$(jq -r '.meu_ip // empty' "$CONFIG_PATH")
    [[ -n "$IP_FIXED" ]] && echo "📡 IP fixo: $IP_FIXED"
  fi
}

# 4. Gera IP baseado no MAC
gen_ip() {
  if [[ -n "$IP_FIXED" ]]; then
    echo "$IP_FIXED"
  else
    local mac h num
    mac=$(cat /sys/class/net/"$IFACE"/address)
    h=$(echo "$mac" | md5sum | cut -c1-2)
    num=$((0x$h % 100 + 100))
    echo "${BASE_IP}.${num}"
  fi
}

# 5. Configura IBSS mínimo
setup_ibss() {
  echo "📴 Limpando $IFACE..."
  sudo nmcli dev disconnect "$IFACE" &>/dev/null || true
  sudo systemctl stop NetworkManager &>/dev/null || true
  sudo ip addr flush dev "$IFACE"
  sudo ip link set "$IFACE" down

  echo "🔧 Configurando IBSS ($SSID @ channel $CHANNEL)..."
  sudo iwconfig "$IFACE" mode ad-hoc
  sudo iwconfig "$IFACE" essid "$SSID"
  sudo iwconfig "$IFACE" channel "$CHANNEL"
  sudo ip link set "$IFACE" up
}

# 6. Inicia batman-adv e cria bat0
start_batman() {
  echo "🧩 Carregando batman_adv..."
  sudo modprobe batman_adv

  echo "➕ Adicionando $IFACE ao batman..."
  sudo batctl if add "$IFACE"

  echo "🔛 Ligando bat0..."
  sudo ip link set up dev bat0
  local ip
  ip=$(gen_ip)
  sudo ip addr add "$ip/24" dev bat0
  echo "🔑 IP bat0: $ip"
}

# 7. Diagnóstico final
diagnose() {
  echo ""
  echo "✅ Rede Batman-adv configurada!"
  echo "🌐 bat0 status:"
  ip -4 addr show bat0 | grep inet
  echo ""
  echo "🛰️ Peers batman:"
  batctl o
}

# Execução
install_pkgs
detect_iface
load_ip
setup_ibss
start_batman
diagnose
