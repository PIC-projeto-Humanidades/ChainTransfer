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
# -----------------------------------------------------------------------
#                             Rede mesh
# -----------------------------------------------------------------------
SSID="RedeMeshDTN"
CHANNEL="6"
PACOTES=("wireless-tools" "iw" "net-tools")
BASE="10.0.0"
IP_FIXO="" 
CONFIG_PATH="$(dirname "$(realpath "$0")")/network_config.json"

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

carregar_ip_do_json() {
  if [ ! -f "$CONFIG_PATH" ]; then
    echo "❌ Arquivo de configuração não encontrado: $CONFIG_PATH"
    exit 1
  fi

  IP_FIXO=$(jq -r '.meu_ip' "$CONFIG_PATH")
  if [ -z "$IP_FIXO" ] || [ "$IP_FIXO" == "null" ]; then
    echo "⚠️ 'meu_ip' ausente ou inválido no JSON. IP será gerado automaticamente."
    IP_FIXO=""
  else
    echo "📡 IP carregado do JSON: $IP_FIXO"
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

# -----------------------------------------------------------------------
#                              Python
# -----------------------------------------------------------------------
verificar_python() {
  if ! command -v python3 >/dev/null 2>&1; then
    echo "🐍 Python 3 não encontrado. Instalando..."
    sudo apt update
    sudo apt install -y python3
  else
    echo "✅ Python 3 está instalado."
  fi

  if ! command -v pip3 >/dev/null 2>&1; then
    echo "📦 pip3 não encontrado. Instalando..."
    sudo apt install -y python3-pip
  else
    echo "✅ pip3 está instalado."
  fi
}

instalar_dependencias_python() {
  REQ_PATH="$(dirname "$(realpath "$0")")/requirements.txt"
  if [ -f "$REQ_PATH" ]; then
    echo "📦 Instalando dependências do Python a partir de: $REQ_PATH"
    pip3 install -r "$REQ_PATH"
  else
    echo "⚠️ Arquivo requirements.txt não encontrado: $REQ_PATH"
  fi
}

iniciar_python() {
  SCRIPT_PATH="$(dirname "$(realpath "$0")")/app.py"
  if [ -f "$SCRIPT_PATH" ]; then
    echo "🚀 Iniciando aplicação Python: $SCRIPT_PATH"
    python3 "$SCRIPT_PATH"
  else
    echo "❌ Script Python não encontrado: $SCRIPT_PATH"
    exit 1
  fi
}
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
# Execução principal sem python
verificar_pacotes
carregar_ip_do_json
detectar_interface
verificar_ibss
iniciar_mesh



# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
# Execução principal sem python
# verificar_pacotes
# carregar_ip_do_json
# detectar_interface
# verificar_ibss
# iniciar_mesh
# verificar_python
# instalar_dependencias_python
# iniciar_python