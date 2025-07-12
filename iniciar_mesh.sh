#!/bin/bash

: '
📡 Script: iniciar_mesh.sh
🧠 Propósito:
  Inicia uma rede mesh Wi-Fi (modo Ad-Hoc/IBSS) com IP fixo ou baseado no MAC.

📋 Requisitos:
  - Interface compatível com modo Ad-Hoc (IBSS)
  - Pacotes: wireless-tools, iw, net-tools
'

SSID="RedeMeshDTN"
CHANNEL="6"
CELL_ID="02:CA:FE:BA:BE:01"  # ID comum a todos
BASE="10.0.0"
PACOTES=("wireless-tools" "iw" "net-tools")
CONFIG_PATH="$(dirname "$(realpath "$0")")/network_config.json"
IP_FIXO=""

verificar_pacotes() {
  FALTANDO=()
  for p in "${PACOTES[@]}"; do
    dpkg -s "$p" &>/dev/null || FALTANDO+=("$p")
  done
  if [ ${#FALTANDO[@]} -gt 0 ]; then
    echo "📦 Instalando: ${FALTANDO[*]}"
    sudo apt update && sudo apt install -y "${FALTANDO[@]}"
  else
    echo "✅ Todos os pacotes necessários estão instalados."
  fi
}

detectar_interface() {
  INTERFACE=$(iw dev | awk '$1=="Interface"{print $2}' | head -n1)
  if [ -z "$INTERFACE" ]; then
    echo "❌ Nenhuma interface Wi-Fi detectada."
    exit 1
  fi
  echo "🔍 Interface detectada: $INTERFACE"
}

verificar_ibss() {
  iw list | grep -q "IBSS" || {
    echo "❌ Interface não suporta modo IBSS (Ad-Hoc)"
    exit 1
  }
}

carregar_ip_do_json() {
  if [ -f "$CONFIG_PATH" ]; then
    IP_JSON=$(jq -r '.meu_ip' "$CONFIG_PATH")
    [ "$IP_JSON" != "null" ] && IP_FIXO="$IP_JSON"
    echo "📡 IP do JSON: $IP_FIXO"
  fi
}

gerar_ip() {
  if [ -n "$IP_FIXO" ]; then
    echo "$IP_FIXO"
  else
    MAC=$(cat /sys/class/net/"$INTERFACE"/address)
    HASH=$(echo "$MAC" | md5sum | cut -c1-2)
    NUM=$(( 0x$HASH % 100 + 100 ))
    echo "${BASE}.${NUM}"
  fi
}

iniciar_mesh() {
  IP=$(gerar_ip)
  echo "🔑 IP atribuído: $IP"

  echo "📴 Limpando $INTERFACE..."
  sudo nmcli dev disconnect "$INTERFACE" &>/dev/null || true
  sudo systemctl stop NetworkManager &>/dev/null || true
  sudo ip addr flush dev "$INTERFACE"
  sudo ip link set "$INTERFACE" down

  echo "🔧 Configurando $INTERFACE para Ad-Hoc Mesh..."
  sudo iwconfig "$INTERFACE" mode ad-hoc
  sudo iwconfig "$INTERFACE" essid "$SSID"
  sudo iwconfig "$INTERFACE" channel "$CHANNEL"
  sudo iwconfig "$INTERFACE" ap "$CELL_ID"
  sudo iwconfig "$INTERFACE" power off &>/dev/null || true
  sudo ip link set "$INTERFACE" up
  sudo ip addr add "$IP/24" dev "$INTERFACE"

  echo "✅ Mesh IBSS ativa em $INTERFACE com IP $IP e Cell $CELL_ID"
  echo ""
  echo "📊 iwconfig:"
  iwconfig "$INTERFACE" | grep -E "ESSID|Mode|Freq|Cell"
  echo ""
  echo "🌐 IP atual:"
  ip addr show "$INTERFACE" | grep 'inet ' | awk '{print $2}'
}

# Execução
verificar_pacotes
carregar_ip_do_json
detectar_interface
verificar_ibss
iniciar_mesh
