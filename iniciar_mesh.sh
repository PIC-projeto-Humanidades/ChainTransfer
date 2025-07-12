#!/bin/bash
set -euo pipefail

: '
📡 Script: iniciar_mesh.sh
🧠 Propósito:
  Inicia uma rede mesh Wi-Fi (modo Ad-Hoc/IBSS) com IP fixo ou baseado no MAC.

📋 Requisitos:
  - Interface compatível com modo Ad-Hoc (IBSS)
  - Pacotes: wireless-tools, iw, net-tools, jq
'

SSID="RedeMeshDTN"
CHANNEL="6"
CELL_ID="02:CA:FE:BA:BE:01"
BASE="10.0.0"
PACOTES=("wireless-tools" "iw" "net-tools" "jq")
CONFIG_PATH="$(dirname "$(realpath "$0")")/network_config.json"
IP_FIXO=""

verificar_pacotes() {
  local FALTANDO=()
  for p in "${PACOTES[@]}"; do
    if ! dpkg -s "$p" &>/dev/null; then
      FALTANDO+=("$p")
    fi
  done

  if [ ${#FALTANDO[@]} -gt 0 ]; then
    echo "📦 Instalando pacotes: ${FALTANDO[*]}"
    sudo apt update && sudo apt install -y "${FALTANDO[@]}"
  else
    echo "✅ Todos os pacotes estão instalados."
  fi
}

detectar_interface() {
  INTERFACE=$(iw dev | awk '$1=="Interface"{print $2}' | grep -v '^mesh' | head -n1 || true)
  if [ -z "${INTERFACE:-}" ]; then
    echo "❌ Nenhuma interface Wi-Fi detectada."
    exit 1
  fi
  echo "🔍 Interface detectada: $INTERFACE"
}

verificar_ibss() {
  if ! iw list | grep -A10 "Supported interface modes" | grep -q "IBSS"; then
    echo "❌ A interface $INTERFACE não suporta modo IBSS (Ad-Hoc)."
    exit 1
  fi
}

carregar_ip_do_json() {
  if [[ -f "$CONFIG_PATH" ]]; then
    IP_JSON=$(jq -r '.meu_ip // empty' "$CONFIG_PATH")
    if [[ -n "$IP_JSON" ]]; then
      IP_FIXO="$IP_JSON"
      echo "📡 IP carregado do JSON: $IP_FIXO"
    fi
  else
    echo "⚠️ Arquivo $CONFIG_PATH não encontrado."
  fi
}

gerar_ip() {
  if [[ -n "$IP_FIXO" ]]; then
    echo "$IP_FIXO"
  else
    local MAC HASH NUM
    MAC=$(cat /sys/class/net/"$INTERFACE"/address)
    HASH=$(echo "$MAC" | md5sum | cut -c1-2)
    NUM=$(( 0x$HASH % 100 + 100 ))
    echo "${BASE}.${NUM}"
  fi
}

iniciar_mesh() {
  local IP
  IP=$(gerar_ip)
  echo "🔑 IP atribuído: $IP"

  echo "📴 Limpando interface $INTERFACE..."
  sudo nmcli dev disconnect "$INTERFACE" &>/dev/null || true
  sudo systemctl stop NetworkManager &>/dev/null || true
  sudo ip addr flush dev "$INTERFACE"
  sudo ip link set "$INTERFACE" down

  echo "🔧 Configurando $INTERFACE como Mesh Ad-Hoc..."
  sudo iwconfig "$INTERFACE" mode ad-hoc
  sudo iwconfig "$INTERFACE" essid "$SSID"
  sudo iwconfig "$INTERFACE" channel "$CHANNEL"
  sudo iwconfig "$INTERFACE" ap "$CELL_ID"
  sudo iwconfig "$INTERFACE" power off &>/dev/null || true
  sudo ip link set "$INTERFACE" up
  sudo ip addr add "$IP/24" dev "$INTERFACE"

  echo "✅ Mesh IBSS ativa em $INTERFACE com IP $IP e Cell $CELL_ID"
  echo ""
  echo "📊 iwconfig $INTERFACE:"
  iwconfig "$INTERFACE" | grep -E "ESSID|Mode|Frequency|Cell"
  echo ""
  echo "🌐 IP atual:"
  ip -4 addr show "$INTERFACE" | grep inet | awk '{print $2}'
}

# Execução
verificar_pacotes
carregar_ip_do_json
detectar_interface
verificar_ibss
iniciar_mesh
