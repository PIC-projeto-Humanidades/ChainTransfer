#!/bin/bash
set -euo pipefail

: '
🧹 Script: desfazer_mesh.sh
🧠 Restaura a interface Wi-Fi e limpa Batman-adv
'

# Detecta interface física
PHY=$(iw dev | awk '$1=="Interface"{print $2}' | grep -Ev '^(bat|mesh)' | head -n1)
[[ -n "$PHY" ]] || { echo "❌ Sem interface Wi-Fi"; exit 1; }

# Tira IP e modo IBSS
ip addr flush dev "$PHY"
ip link set "$PHY" down
iwconfig "$PHY" mode managed
ip link set "$PHY" up

# Remove bat0
ip link show bat0 &>/dev/null && {
  batctl if del "$PHY" || true
  ip link set down dev bat0
  ip link delete bat0
}

# Descarrega módulo
lsmod | grep -q batman_adv && modprobe -r batman_adv

# Restaura NetworkManager
systemctl start NetworkManager &>/dev/null || true

echo "✅ $PHY restaurada ao modo gerenciado."
