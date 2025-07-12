#!/bin/bash
set -euo pipefail

: '
🧹 Script: desfazer_mesh.sh
🧠 Propósito:
  Restaura a interface Wi-Fi usada na rede mesh Ad-Hoc (IBSS) para modo gerenciado.

📋 Requisitos:
  - Interface compatível com modo managed
  - Pacotes: wireless-tools, net-tools
'

# Detecta a interface Wi-Fi principal (ignora "mesh" virtuais)
INTERFACE=$(iw dev | awk '$1=="Interface"{print $2}' | grep -v '^mesh' | head -n1 || true)

if [ -z "${INTERFACE:-}" ]; then
  echo "❌ Nenhuma interface Wi-Fi detectada."
  exit 1
fi

echo "🛑 Restaurando estado da interface: $INTERFACE"

# Libera e reseta a interface
sudo ip addr flush dev "$INTERFACE"
sudo ip link set "$INTERFACE" down
sudo iwconfig "$INTERFACE" mode managed
sudo ip link set "$INTERFACE" up

# Remove possíveis interfaces virtuais mesh criadas manualmente
for iface in $(ip link show | grep -oE '^.*mesh[0-9]*:' | sed 's/://g'); do
  echo "🧹 Removendo interface virtual: $iface"
  sudo ip link delete "$iface" type wlan || true
done

# Reativa o NetworkManager
sudo systemctl start NetworkManager >/dev/null 2>&1 || true

echo "✅ Interface $INTERFACE restaurada ao modo gerenciado."
