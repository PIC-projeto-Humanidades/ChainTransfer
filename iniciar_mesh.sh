#!/bin/bash
set -euo pipefail

: '
📡 Script: iniciar_mesh_batman.sh
🧠 Cria uma rede mesh usando Batman-adv sobre um enlace IBSS mínimo
'

# 1) Checa root
(( EUID == 0 )) || { echo "❌ Rode como root"; exit 1; }

SSID="RedeMeshDTN"
CHANNEL="6"
BASE_IP="10.0.0"
CONFIG_PATH="$(dirname "$(realpath "$0")")/network_config.json"
PACOTES=("batctl" "wireless-tools" "iw" "iproute2" "jq")

install_pkgs() {
  local miss=()
  for p in "${PACOTES[@]}"; do
    dpkg -s "$p" &>/dev/null || miss+=("$p")
  done
  (( ${#miss[@]} )) && apt update && apt install -y "${miss[@]}"
}

detect_iface() {
  IFACE=$(iw dev | awk '$1=="Interface"{print $2}' | grep -Ev '^(bat|mesh)' | head -n1)
  [[ -n "$IFACE" ]] || { echo "❌ Sem interface Wi-Fi"; exit 1; }
}

load_ip() {
  IP_FIXED=""
  [[ -f "$CONFIG_PATH" ]] && IP_FIXED=$(jq -r '.meu_ip // empty' "$CONFIG_PATH")
}

gen_ip() {
  [[ -n "$IP_FIXED" ]] && echo "$IP_FIXED" && return
  local mac h num
  mac=$(cat /sys/class/net/"$IFACE"/address)
  h=$(echo "$mac" | md5sum | cut -c1-2)
  num=$((0x$h % 100 + 100))
  echo "${BASE_IP}.${num}"
}

setup_ibss() {
  echo "📴 Desconectando $IFACE do NM…"
  nmcli dev disconnect "$IFACE" &>/dev/null || true
  echo "📴 Parando NetworkManager…"
  systemctl stop NetworkManager &>/dev/null || true

  echo "📴 Limpando $IFACE (IP e status)…"
  ip addr flush dev "$IFACE"
  ip link set "$IFACE" down

  echo "🔧 Configurando IBSS: SSID=$SSID, canal=$CHANNEL"
  iwconfig "$IFACE" mode ad-hoc
  iwconfig "$IFACE" essid "$SSID"
  iwconfig "$IFACE" channel "$CHANNEL"
  ip link set "$IFACE" up
}

cleanup_bat0() {
  ip link show bat0 &>/dev/null && {
    batctl if del "$IFACE" || true
    ip link set down dev bat0 || true
    ip link delete bat0 || true
  }
}

start_batman() {
  modprobe batman_adv
  batctl if add "$IFACE"
  ip link set up dev bat0
  local ip; ip=$(gen_ip)
  ip addr add "$ip/24" dev bat0 || true
}

show_peers() {
  batctl o
}

install_pkgs
detect_iface
load_ip
setup_ibss
cleanup_bat0
start_batman
show_peers

echo "✅ bat0 up with IP: $(ip -4 addr show bat0 | grep inet)"
