#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CFG="$BASE_DIR/network_config.json"

# Extrai do JSON
SSID=$(jq -r '.ssid'       "$CFG")
PASSWORD=$(jq -r '.password' "$CFG")
MEU_IP=$(jq -r '.meu_ip'    "$CFG")
PREFIXO=$(jq -r '.prefixo'  "$CFG")
GATEWAY=$(jq -r '.gateway'  "$CFG")
DNS1=$(jq -r '.dns[0]'      "$CFG")

# Detecta interface wifi
WIFI_IF=$(nmcli -t -f DEVICE,TYPE dev status \
            | awk -F: '$2=="wifi"{print $1; exit}')
[[ -n "$WIFI_IF" ]] || { echo "❌ Sem iface wifi"; exit 1; }

echo "Interface: $WIFI_IF"
echo "SSID alvo: $SSID"

# 1) Loop de scan / associação
while true; do
  echo "[$(date +'%H:%M:%S')] escaneando por '$SSID'..."
  if nmcli -t -f SSID dev wifi list | grep -qx "$SSID"; then
    echo ">>> Rede '$SSID' encontrada. Associando..."
    # Faz a associação WPA2 via nmcli (cria profile temporário)
    if nmcli device wifi connect "$SSID" password "$PASSWORD" ifname "$WIFI_IF"; then
      break
    else
      echo "*** Falhou na associação, retry em 5s..."
      sleep 5
    fi
  else
    echo "    não encontrou '$SSID', retry em 5s..."
    sleep 5
  fi
done

# 2) Limpa qualquer IP antigo na interface
echo ">>> Limpando IP antigo em $WIFI_IF..."
sudo ip addr flush dev "$WIFI_IF"

# 3) Configura IP estático
echo ">>> Atribuindo IP estático $MEU_IP/$PREFIXO..."
sudo ip addr add "$MEU_IP"/"$PREFIXO" dev "$WIFI_IF"

# 4) Ajusta rota padrão
echo ">>> Definindo gateway $GATEWAY..."
sudo ip route replace default via "$GATEWAY" dev "$WIFI_IF"

# 5) Seta DNS
echo ">>> Configurando DNS $DNS1..."
echo "nameserver $DNS1" | sudo tee /etc/resolv.conf >/dev/null

echo "+++ Conectado em '$SSID' com IP $MEU_IP/$PREFIXO via $WIFI_IF"
exit 0
