#!/bin/bash

: '
🧹 Script: desfazer_mesh.sh
🧠 Propósito:
  Desativa a configuração Ad-Hoc/Mesh da interface Wi-Fi e restaura o modo gerenciado (managed).

📋 Requisitos:
  - Pacotes: wireless-tools, net-tools, iw
'

# Detecta a interface Wi-Fi usada
INTERFACE=$(iw dev | awk '$1=="Interface"{print $2}' | head -n1)

if [ -z "$INTERFACE" ]; then
  echo "❌ Nenhuma interface Wi-Fi detectada."
  exit 1
fi

echo "🛑 Desfazendo configuração da interface $INTERFACE..."

# Limpa IPs e desativa interface
sudo ip addr flush dev "$INTERFACE"
sudo ip link set "$INTERFACE" down

# Tenta restaurar modo gerenciado
echo "🔁 Restaurando modo gerenciado..."
sudo iwconfig "$INTERFACE" mode managed
sudo iwconfig "$INTERFACE" essid off
sudo iwconfig "$INTERFACE" ap off

# Reativa interface e NetworkManager
sudo ip link set "$INTERFACE" up
sudo systemctl start NetworkManager &>/dev/null || true

# Exibe estado final
echo "✅ Interface $INTERFACE restaurada ao modo gerenciado."
echo ""
echo "📊 iwconfig atual:"
iwconfig "$INTERFACE" | grep -E "ESSID|Mode|Freq|Cell"
