# Módulo Monitoring

Exposição de endpoints para feedback e consulta de status de downloads e descoberta de dispositivos.

## Controller (monitoring.controller.ts)

- **GET /monitoring/devices**: Retorna lista de dispositivos conectados (NetworkService).
- **GET /monitoring/status/:sessao**: Retorna logs de downloads de uma sessão (LogsService).
- **POST /monitoring/feedback**: Recebe feedback de download e registra log via LogsService.

