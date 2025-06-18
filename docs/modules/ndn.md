# Módulo NDN

APIs HTTP para listagem e transferência de arquivos entre nós.

## Service (ndn.service.ts)


_Note: Serviço vazio, a lógica principal está no controller._

## Controller (ndn.controller.ts)

- **POST /ndn/file**: Realiza download de arquivo: verifica duplicidade via StorageService e retorna 201 ou 200.
- **GET /ndn/files**: Lista arquivos disponíveis localmente via StorageService.

