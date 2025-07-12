#!/usr/bin/env bash
set -euo pipefail

# checa dependências
for cmd in jq nmcli; do
  command -v $cmd >/dev/null || { echo "❌ instale $cmd"; exit 1; }
done

CFG="$(dirname "$0")/network_config.json"
[[ -f $CFG ]] || { echo "❌ $CFG não achado"; exit 1; }

SSID=$(jq -r '.ssid'     $CFG)
PASSWORD=$(jq -r '.password' $CFG)
MEU_IP=$(jq -r '.meu_ip'    $CFG)
PREFIXO=$(jq -r '.prefixo'  $CFG)
GATEWAY=$(jq -r '.gateway'  $CFG)
DNS=$(jq -r '.dns | join(",")' $CFG)

# detecta wifi iface
WIFI_IF=$(nmcli -t -f DEVICE,TYPE dev status | awk -F: '$2=="wifi"{print $1; exit}')
[[ $WIFI_IF ]] || { echo "❌ Sem iface wifi"; exit 1; }
echo "Interface: $WIFI_IF"

STATIC="${MEU_IP}/${PREFIXO}"

while true; do
  echo "[$(date +'%H:%M:%S')] procurando $SSID..."
  if nmcli -t -f SSID dev wifi list | grep -qx "$SSID"; then
    echo ">>> Encontrou — associando..."
    # associa (cria temporariamente um profile com nome igual ao SSID)
    if ! nmcli device wifi connect "$SSID" password "$PASSWORD" ifname "$WIFI_IF"; then
      echo "*** falhou ao associar, retry em 5s"; sleep 5; continue
    fi

    # pega o nome exato do connection profile que acabou de subir
    CONN=$(nmcli -t -f GENERAL.CONNECTION dev show "$WIFI_IF" | cut -d: -f2)
    echo ">>> Usando profile: $CONN"

    # modifica só essa conexão para IP manual
    nmcli connection modify "$CONN" \
      ipv4.method manual \
      ipv4.addresses "$STATIC" \
      ipv4.gateway "$GATEWAY" \
      ipv4.dns "$DNS" \
      connection.autoconnect no

    # reinicia a conexão já com o static
    nmcli connection down "$CONN"
    nmcli connection up   "$CONN"

    echo "+++ Conectado em $SSID com IP $STATIC"
    exit 0
  else
    echo "não achou, aguardando 5s..."
    sleep 5
  fi
done
