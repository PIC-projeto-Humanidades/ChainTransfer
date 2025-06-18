# 🗄️ Módulo **Storage**

> **Responsabilidade:**  
> Abstração para acesso e listagem de arquivos locais, garantindo controle de duplicidade via logs.

---

## 📦 Imports & Configuração

```ts
import { Module } from '@nestjs/common';
import { LogsModule } from 'src/logs/logs.module';
import { StorageService } from './storage.service';
import { StorageRepository } from './storage.repositories';

@Module({
  imports: [ LogsModule ],
  providers: [ StorageService, StorageRepository ],
  exports: [ StorageService ],
})
export class StorageModule {}
```

- **LogsModule**: disponibiliza `LogsService` para verificação de downloads.  
- **StorageRepository**: encapsula acesso ao sistema de arquivos.

---

## 📚 Repository: `storage.repositories.ts`

```ts
import * as fs from 'fs';
import * as path from 'path';
import { Injectable, NotFoundException } from '@nestjs/common';

@Injectable()
export class StorageRepository {
  private readonly basePath = path.resolve(__dirname, '../../media_data');

  /**
   * Retorna o caminho completo de um arquivo local.
   * @param fileName Nome do arquivo
   * @throws NotFoundException se o arquivo não existir
   */
  getFile(fileName: string): string {
    const filePath = path.join(this.basePath, fileName);
    if (!fs.existsSync(filePath)) {
      throw new NotFoundException(`Arquivo '${fileName}' não encontrado`);
    }
    return filePath;
  }

  /**
   * Lista todos os arquivos presentes no diretório base.
   * @returns Array de nomes de arquivos
   * @throws NotFoundException se o diretório não existir
   */
  listFiles(): string[] {
    if (!fs.existsSync(this.basePath)) {
      throw new NotFoundException(`Diretório '${this.basePath}' não encontrado`);
    }
    return fs.readdirSync(this.basePath);
  }
}
```

---

## 🔧 Service: `storage.service.ts`

```ts
import { Injectable, NotFoundException } from '@nestjs/common';
import { StorageRepository } from './storage.repositories';
import { LogsService } from 'src/logs/logs.service';

@Injectable()
export class StorageService {
  constructor(
    private readonly storageRepository: StorageRepository,
    private readonly logsService: LogsService,
  ) {}

  /**
   * Retorna o path do arquivo se ainda não tiver sido baixado nesta sessão.
   * @param fileName Nome do arquivo
   * @param sessao Identificador da sessão
   * @param node ID do nó solicitante
   * @returns Path completo ou string vazia se já tiver sido baixado
   */
  async getFile({ fileName, sessao, node }: {
    fileName: string;
    sessao: string;
    node: string;
  }): Promise<string> {
    const downloaded = await this.logsService.getLogsBySession(sessao);
    const exists = downloaded.some(log => log.fileName === fileName);
    if (exists) {
      return '';
    }
    return this.storageRepository.getFile(fileName);
  }

  /**
   * Lista arquivos disponíveis no diretório base.
   * @returns Array de nomes de arquivos
   */
  listFiles(): string[] {
    return this.storageRepository.listFiles();
  }
}
```

---

## 📝 Exemplos de Uso

```ts
// No controller...
const filePath = await storageService.getFile({ fileName: 'dados.txt', sessao: 'sessao-123', node: 'node-A' });
if (filePath) {
  res.status(201).download(filePath);
} else {
  res.status(200).json({ message: 'Download já realizado' });
}
```

---
