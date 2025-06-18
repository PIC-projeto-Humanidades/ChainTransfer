# Módulo Network

Implementa varredura de rede local por ARP e descoberta de nós via ping e nslookup.

## Service (network.service.ts)

- **getNamedDevices()**: Retorna lista estática de mapeamentos mac→node.
- **getConnectedDevices()**: Executa ping sweep e arp -a, processa saída para lista de dispositivos ativos.
- **getHostname(ip)**: Resolve hostname via nslookup.

