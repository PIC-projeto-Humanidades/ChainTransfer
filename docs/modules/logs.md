# Módulo Logs

Registra e consulta logs de downloads para evitar transferências duplicadas.

## Service (logs.service.ts)

- **logDownload({ fileName, sessao, node })**: Cria registro no banco (Sequelize) com data e informações do download.
- **getLogsBySession(sessao)**: Recupera todos os logs de uma sessão específica.

