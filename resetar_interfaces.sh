#!/bin/bash

echo "🧹 Limpando todas interfaces mesh..."

# 1. Remover interfaces mesh criadas (como mesh0, mesh1, etc)
iw dev | awk '/Interface/ {print $2}' | grep '^mesh' | while read iface; do
  echo "❌ Removendo interface $iface..."
  sudo iw dev "$iface" del
done

# 2. Detectar interface Wi-Fi padrão
IFACE=$(iw dev | awk '$1=="Interface"{print $2}' | grep -v '^mesh' | head -n1)
if [ -z "$IFACE" ]; then
  echo "❌ Nenhuma interface Wi-Fi padrão detectada."
  exit 1
fi
echo "🔄 Restaurando interface $IFACE..."

# 3. Resetar interface principal
sudo ip addr flush dev "$IFACE"
sudo ip link set "$IFACE" down
sudo iwconfig "$IFACE" mode managed
sudo ip link set "$IFACE" up

# 4. Reiniciar NetworkManager
sudo systemctl restart NetworkManager

echo "✅ Estado limpo. Interface $IFACE pronta para uso normal ou mesh."
