#!/bin/bash

: '
📡 Script: iniciar_mesh.sh
🧠 Inicia uma rede mesh Wi-Fi usando 802.11s (modo Mesh Point "mp") em Linux.

📋 Requisitos:
  - Placa Wi-Fi compatível com 802.11s (ex: ath9k, ath10k)
  - Pacotes: iw, iproute2, wireless-tools (opcional), jq (para ler IP do JSON)
'

SSID="RedeMeshDTN"
CHANNEL="6"
PACOTES=("iw" "iproute2" "jq")
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
  MESH_IFACE="mesh0"
  IP=$(gerar_ip)

  echo "📴 Desativando NetworkManager e limpando interface $INTERFACE..."
  sudo systemctl stop NetworkManager &>/dev/null || true
  sudo nmcli dev disconnect "$INTERFACE" &>/dev/null || true
  sudo ip link set "$INTERFACE" down

  echo "🧼 Removendo interfaces mesh antigas (se houver)..."
  sudo iw dev "$MESH_IFACE" del &>/dev/null || true

  echo "➕ Criando interface $MESH_IFACE em modo mesh (802.11s)..."
  sudo iw dev "$INTERFACE" interface add "$MESH_IFACE" type mp
  sudo ip link set "$MESH_IFACE" down
  sudo iw dev "$MESH_IFACE" set channel "$CHANNEL"
  sudo iw dev "$MESH_IFACE" mesh join "$SSID"
  sudo ip link set "$MESH_IFACE" up
  sudo ip addr add "$IP/24" dev "$MESH_IFACE"

  echo "✅ Mesh 802.11s ativa na interface $MESH_IFACE com IP $IP"

  echo ""
  echo "📊 Estado da interface $MESH_IFACE:"
  iw dev "$MESH_IFACE" info | grep -E "interface|type|ssid|channel"
  echo ""
  echo "🌐 IP atual:"
  ip addr show "$MESH_IFACE" | grep 'inet ' | awk '{print $2}'
  echo ""
}

# Execução principal
verificar_pacotes
carregar_ip_do_json
detectar_interface
iniciar_mesh
