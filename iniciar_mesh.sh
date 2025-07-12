#!/bin/bash

: '
📡 Script: iniciar_mesh.sh
🧠 Inicia uma rede mesh Wi-Fi (modo Ad-Hoc/IBSS) em Linux, atribuindo IP manual ou com base no MAC.

📋 Requisitos:
  - Interface Wi-Fi compatível com modo Ad-Hoc
  - Pacotes: wireless-tools, iw, net-tools
'

SSID="RedeMeshDTN"
CHANNEL="6"
PACOTES=("wireless-tools" "iw" "net-tools")
BASE="10.0.0"
IP_FIXO=""
CONFIG_PATH="$(dirname "$(realpath "$0")")/network_config.json"

verificar_pacotes() {
  FALTANDO=()
  for pacote in "${PACOTES[@]}"; do
    if ! dpkg -s "$pacote" &>/dev/null; then
      FALTANDO+=("$pacote")
    fi
  done
  if [ ${#FALTANDO[@]} -gt 0 ]; then
    echo "📦 Instalando pacotes ausentes: ${FALTANDO[*]}"
    sudo apt update
    sudo apt install -y "${FALTANDO[@]}"
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
  echo "🔍 Interface Wi-Fi detectada: $INTERFACE"
}

verificar_ibss() {
  if ! iw list | grep -q "IBSS"; then
    echo "❌ A interface $INTERFACE não suporta modo Ad-Hoc (IBSS)."
    exit 1
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

carregar_ip_do_json() {
  if [ -f "$CONFIG_PATH" ]; then
    IP_JSON=$(jq -r '.meu_ip' "$CONFIG_PATH")
    if [ -n "$IP_JSON" ] && [ "$IP_JSON" != "null" ]; then
      IP_FIXO="$IP_JSON"
      echo "📡 IP carregado do JSON: $IP_FIXO"
    else
      echo "⚠️ 'meu_ip' ausente no JSON. IP será gerado automaticamente."
    fi
  else
    echo "⚠️ Arquivo de configuração não encontrado: $CONFIG_PATH. IP será gerado automaticamente."
  fi
}

iniciar_mesh() {
  IP=$(gerar_ip)
  echo "🔑 IP atribuído: $IP"

  echo "📴 Desativando NetworkManager e limpando interface $INTERFACE..."
  sudo systemctl stop NetworkManager &>/dev/null || true
  sudo nmcli dev disconnect "$INTERFACE" &>/dev/null || true
  sudo ip addr flush dev "$INTERFACE"
  sudo ip link set "$INTERFACE" down

  echo "🔧 Configurando $INTERFACE para rede Mesh ($SSID)..."
  sudo iwconfig "$INTERFACE" mode ad-hoc
  sudo iwconfig "$INTERFACE" essid "$SSID"
  sudo iwconfig "$INTERFACE" channel "$CHANNEL"
  sudo ip link set "$INTERFACE" up
  sudo ip addr add "$IP/24" dev "$INTERFACE"

  echo "✅ Mesh ativa na interface $INTERFACE com IP $IP"
}

# Execução principal
verificar_pacotes
carregar_ip_do_json
detectar_interface
verificar_ibss
iniciar_mesh
