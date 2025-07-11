#!/bin/bash

: '
🧹 Script: desfazer_mesh.sh
🧠 Propósito:
  Desativa a rede mesh e restaura o estado da interface Wi-Fi.

📋 Requisitos:
  - Pacotes: wireless-tools, net-tools
'

# Detecta interface Wi-Fi automaticamente
INTERFACE=$(iw dev | awk '$1=="Interface"{print $2}' | head -n1)

if [ -z "$INTERFACE" ]; then
  echo "❌ Nenhuma interface Wi-Fi detectada."
  exit 1
fi

echo "🛑 Desfazendo configuração da interface $INTERFACE..."

# Tenta restaurar o estado anterior
sudo ip addr flush dev "$INTERFACE"
sudo ip link set "$INTERFACE" down
sudo iwconfig "$INTERFACE" mode managed
sudo ip link set "$INTERFACE" up

# Reativa o NetworkManager (opcional)
sudo systemctl start NetworkManager >/dev/null 2>&1 || true

echo "✅ Interface $INTERFACE restaurada ao modo gerenciado."
