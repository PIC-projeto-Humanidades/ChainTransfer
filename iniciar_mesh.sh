#!/bin/bash

: '
📡 Script: iniciar_mesh.sh
🧠 Propósito:
  Inicia uma rede mesh Wi-Fi (modo Ad-Hoc/IBSS) em Linux, atribuindo IP manual ou exclusivo por MAC.

📋 Requisitos:
  - Interface Wi-Fi compatível com modo Ad-Hoc (IBSS)
  - Pacotes: wireless-tools, iw, net-tools

⚙️ Configurações:
  - IP_FIXO: deixe vazio para gerar IP automaticamente com base no MAC
'

SSID="RedeMeshDTN"
CHANNEL="6"
PACOTES=("wireless-tools" "iw" "net-tools")
BASE="10.0.0"
IP_FIXO="10.0.0.102"  # Exemplo: "10.0.0.123"

verificar_pacotes() {
  FALTANDO=()
  for pacote in "${PACOTES[@]}"; do
    if ! dpkg -s "$pacote" >/dev/null 2>&1; then
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
    NUM=$(( 0x$HASH % 100 + 100 ))  # IP entre 100 e 199
    echo "${BASE}.${NUM}"
  fi
}

iniciar_mesh() {
  IP=$(gerar_ip)
  echo "🔑 IP atribuído: $IP"

  echo "📴 Liberando interface $INTERFACE de conexões ativas..."
  nmcli dev disconnect "$INTERFACE" >/dev/null 2>&1 || true
  sudo systemctl stop NetworkManager >/dev/null 2>&1 || true
  sudo ip addr flush dev $INTERFACE
  sudo ip link set $INTERFACE down

  echo "🔧 Configurando $INTERFACE como mesh ($SSID)..."
  sudo iwconfig $INTERFACE mode ad-hoc
  sudo iwconfig $INTERFACE essid "$SSID"
  sudo iwconfig $INTERFACE channel "$CHANNEL"
  sudo ip link set $INTERFACE up
  sudo ip addr add $IP/24 dev $INTERFACE

  echo "✅ Mesh ativa na interface $INTERFACE com IP $IP"
}

# Execução principal
verificar_pacotes
detectar_interface
verificar_ibss
iniciar_mesh
