#!/bin/bash

: '
📡 Script: iniciar_mesh.sh
🧠 Propósito:
  Inicia uma rede mesh Wi-Fi (modo Ad-Hoc/IBSS) em Linux, atribuindo IP manual ou exclusivo por MAC.

📋 Requisitos:
  - Interface Wi-Fi compatível com modo Ad-Hoc (IBSS)
  - Pacotes: wireless-tools, iw, net-tools, jq

⚙️ Configurações:
  - CONFIG_FILE: caminho para o JSON com a definição de IP (sempre ao lado do script)
'

SSID="RedeMeshDTN"
CHANNEL="6"

# Detecta o diretório onde o script está e usa para encontrar o JSON
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/network_config.json"

PACOTES=("wireless-tools" "iw" "net-tools" "jq")

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

# Lê o IP fixo do JSON; se falhar, sai com erro
gerar_ip() {
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Arquivo de configuração $CONFIG_FILE não encontrado."
    exit 1
  fi

  IP=$(jq -r '.meu_ip // empty' "$CONFIG_FILE")
  if [[ -z "$IP" || "$IP" == "null" ]]; then
    echo "❌ Campo 'meu_ip' não definido em $CONFIG_FILE."
    exit 1
  fi

  echo "$IP"
}

iniciar_mesh() {
  IP=$(gerar_ip)
  echo "🔑 IP atribuído: $IP"

  echo "📴 Liberando interface $INTERFACE de conexões ativas..."
  nmcli dev disconnect "$INTERFACE" >/dev/null 2>&1 || true
  sudo systemctl stop NetworkManager >/dev/null 2>&1 || true
  sudo ip addr flush dev "$INTERFACE"
  sudo ip link set "$INTERFACE" down

  echo "🔧 Configurando $INTERFACE como mesh ($SSID)..."
  sudo iwconfig "$INTERFACE" mode ad-hoc
  sudo iwconfig "$INTERFACE" essid "$SSID"
  sudo iwconfig "$INTERFACE" channel "$CHANNEL"
  sudo ip link set "$INTERFACE" up
  sudo ip addr add "$IP"/24 dev "$INTERFACE"

  echo "✅ Mesh ativa na interface $INTERFACE com IP $IP"
}

# Execução principal
verificar_pacotes
detectar_interface
verificar_ibss
iniciar_mesh
