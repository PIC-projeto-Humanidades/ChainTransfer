#!/bin/bash
set -euo pipefail

: '
📡 Script: iniciar_mesh_batman.sh
🧠 Propósito:
  Cria uma rede mesh usando Batman-adv sobre um enlace IBSS mínimo.
'

# Só funciona como root
if (( EUID != 0 )); then
  echo "❌ Execute este script como root: sudo $0"
  exit 1
fi

SSID="RedeMeshDTN"
CHANNEL="6"
BASE_IP="10.0.0"
CONFIG_PATH="$(dirname "$(realpath "$0")")/network_config.json"
PACOTES=("batctl" "wireless-tools" "iw" "iproute2" "jq")

# 1) Instala pacotes faltantes
install_pkgs() {
  local miss=()
  for p in "${PACOTES[@]}"; do
    dpkg -s "$p" &>/dev/null || miss+=("$p")
  done
  if [ ${#miss[@]} -gt 0 ]; then
    echo "📦 Instalando pacotes: ${miss[*]}"
    apt update
    apt install -y "${miss[@]}"
  else
    echo "✅ Pacotes necessários presentes."
  fi
}

# 2) Detecta interface Wi-Fi não-mesh
detect_iface() {
  IFACE=$(iw dev | awk '$1=="Interface"{print $2}' | grep -Ev '^(mesh|bat)' | head -n1)
  [[ -n "$IFACE" ]] || { echo "❌ Nenhuma interface Wi-Fi detectada."; exit 1; }
  echo "🔍 Interface física: $IFACE"
}

# 3) Carrega IP fixo se existir
load_ip() {
  IP_FIXED=""
  if [[ -f "$CONFIG_PATH" ]]; then
    IP_FIXED=$(jq -r '.meu_ip // empty' "$CONFIG_PATH")
    [[ -n "$IP_FIXED" ]] && echo "📡 IP fixo: $IP_FIXED"
  fi
}

# 4) Gera IP baseado no MAC
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

# 5) Configura IBSS mínimo
setup_ibss() {
  echo "📴 Limpando $IFACE..."
  ip addr flush dev "$IFACE"
  ip link set "$IFACE" down

  echo "🔧 Configurando IBSS: SSID=$SSID, canal=$CHANNEL..."
  iwconfig "$IFACE" mode ad-hoc
  iwconfig "$IFACE" essid "$SSID"
  iwconfig "$IFACE" channel "$CHANNEL"
  ip link set "$IFACE" up
}

# 6) Limpa bat0 antigo
cleanup_bat0() {
  if ip link show bat0 &>/dev/null; then
    echo "❌ Bat0 existe — removendo..."
    batctl if del "$IFACE" || true
    ip link set down dev bat0 2>/dev/null || true
    ip link delete bat0 2>/dev/null || true
  fi
}

# 7) Inicia batman-adv
start_batman() {
  echo "🧩 Carregando batman_adv..."
  modprobe batman_adv || { echo "❌ Módulo batman_adv não disponível"; exit 1; }

  echo "➕ Adicionando $IFACE ao batman..."
  batctl if add "$IFACE"

  echo "🔛 Subindo bat0..."
  ip link set up dev bat0

  local ip
  ip=$(gen_ip)
  echo "🔑 Atribuindo IP $ip/24 a bat0..."
  ip addr add "$ip/24" dev bat0 || true

  echo ""
  echo "🌐 bat0 configurada com IP:"
  ip -4 addr show bat0 | grep inet
}

# 8) Mostra peers
show_peers() {
  echo ""
  echo "🛰️ Peers conhecidos (batctl o):"
  batctl o || echo "❌ falha ao listar peers"
}

# Execução
install_pkgs
detect_iface
load_ip
setup_ibss
cleanup_bat0
start_batman
show_peers
