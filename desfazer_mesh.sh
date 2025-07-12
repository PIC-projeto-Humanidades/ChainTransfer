#!/bin/bash

: '
🧹 Script: desfazer_mesh.sh
🧠 Propósito:
  Remove interface mesh criada via 802.11s (modo MP) e restaura interface Wi-Fi ao modo gerenciado.

📋 Requisitos:
  - Pacotes: iw, iproute2
'

# Detecta interfaces mesh criadas
MESH_IFACE=$(iw dev | awk '/Interface/ {print $2}' | grep '^mesh' | head -n1)
BASE_IFACE=$(iw dev | awk '/Interface/ {print $2}' | grep -v '^mesh' | head -n1)

if [ -z "$BASE_IFACE" ]; then
  echo "❌ Nenhuma interface Wi-Fi detectada."
  exit 1
fi

echo "🛑 Desfazendo configuração da interface mesh..."

# Remove interface mesh, se existir
if [ -n "$MESH_IFACE" ]; then
  echo "➖ Removendo interface mesh $MESH_IFACE..."
  sudo ip link set "$MESH_IFACE" down
  sudo iw dev "$MESH_IFACE" del
fi

# Restaura interface principal
echo "🔁 Restaurando $BASE_IFACE ao modo gerenciado..."
sudo ip addr flush dev "$BASE_IFACE"
sudo ip link set "$BASE_IFACE" down
sudo iwconfig "$BASE_IFACE" mode managed
sudo ip link set "$BASE_IFACE" up

# Reativa o NetworkManager (opcional)
sudo systemctl start NetworkManager >/dev/null 2>&1 || true

echo "✅ Interface $BASE_IFACE restaurada ao modo gerenciado."
