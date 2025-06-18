# 🌀 Módulo **Routines**

> **Responsabilidade:**  
> Gerenciar e executar rotinas periódicas de detecção de nós na rede local e replicação automática de arquivos ausentes.

---

## 📦 Imports & Configuração

```ts
import { Module } from '@nestjs/common';
import { NetworkModule } from 'src/network/network.module';
import { StorageModule } from 'src/storage/storage.module';
import { RoutinesService } from './routines.service';

@Module({
  imports: [ NetworkModule, StorageModule ],
  providers: [ RoutinesService ],
  exports: [ RoutinesService ],
})
export class RoutinesModule {}
```

- **NetworkModule**: fornece `NetworkService` para varredura de dispositivos.  
- **StorageModule**: fornece `StorageService` para checagem e gravação de arquivos.

---

## 🔧 Service: `routines.service.ts`

```ts
import { Injectable, OnModuleInit } from '@nestjs/common';
import { NetworkService }       from 'src/network/network.service';
import { StorageService }       from 'src/storage/storage.service';
import * as fs                  from 'fs';
import * as path                from 'path';
import { v4 as uuidv4 }         from 'uuid';
import fetch                    from 'node-fetch';

@Injectable()
export class RoutinesService implements OnModuleInit {
  private readonly mediaPath = path.resolve(__dirname, '../../media_data');

  constructor(
    private readonly networkService: NetworkService,
    private readonly storageService: StorageService,
  ) {}

  /** 
   * Disparado automaticamente pelo NestJS após a injeção de dependências.
   * - Renomeia arquivos sem UID
   * - Inicia rotina periódica
   */
  async onModuleInit() {
    console.log('✅ Rotina inicializada!');
    await this.checkAndRenameFiles();
    this.startRoutine();
  }
```

### Métodos Principais

| Método                              | Descrição                                                                                                 |
|-------------------------------------|-----------------------------------------------------------------------------------------------------------|
| `startRoutine()`                    | Inicia um `setInterval` (a cada 2 segundos) que varre a rede para encontrar dispositivos ativos.         |
| `routine_foundDevice(foundDevices)` | Processa nós detectados:                                                                             |
|                                     | 1. Consulta arquivos disponíveis no nó remoto via `GET /ndn/files`.                                       |
|                                     | 2. Compara com `StorageService.listFiles()` para filtrar arquivos ausentes.                               |
|                                     | 3. Baixa cada arquivo (via `POST /ndn/file`) e salva em `media_data/`.                                    |
|                                     | 4. Envia feedback para `/monitoring/feedback` quando necessário.                                          |
| `checkAndRenameFiles()`             | Renomeia arquivos em `media_data/` adicionando UUID a nomes sem UID.                                      |

---

## 🏗️ Fluxo de Execução

1. **Inicialização** (`onModuleInit`)  
   - Renomeia arquivos antigos sem UID  
   - Chama `startRoutine()`

2. **Loop Periódico** (`startRoutine`)  
   - Varre dispositivos (`NetworkService.getConnectedDevices()`)  
   - Filtra pelos nós conhecidos (`NetworkService.getNamedDevices()`)  
   - Se encontrar, chama `routine_foundDevice(...)`

3. **Transferência** (`routine_foundDevice`)  
   - Busca lista de arquivos remotos  
   - Compara com arquivos locais  
   - Para cada arquivo ausente:  
     - Download via HTTP → salva em disco  
     - Registra download com `LogsService` através do endpoint de feedback  

4. **Reenvio**  
   - Em caso de falhas, tenta reenviar arquivos pendentes

---

## ⚙️ Exemplos de Log no Console

```
✅ Rotina inicializada!
🔄 Iniciando rotina recorrente a cada 2 segundos...
🌐 Dispositivo encontrado: node-A (MAC: a4:63:a1:5a:9d:95)
⬇️ Download de "foto1.jpg" concluído!
📊 Feedback enviado para node-A
✅ Rotina concluída para este ciclo.
```

---
