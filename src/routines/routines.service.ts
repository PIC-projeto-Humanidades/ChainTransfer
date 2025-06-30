import { Injectable, OnModuleInit, OnApplicationBootstrap, Logger } from '@nestjs/common';
import { NetworkService } from '../network/network.service';
import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { StorageService } from '../storage/storage.service';
import fetch from 'node-fetch';

@Injectable()
export class RoutinesService implements OnModuleInit, OnApplicationBootstrap {
  private readonly logger = new Logger(RoutinesService.name);
  private readonly mediaPath = path.resolve(__dirname, "../../media_data");
  private readonly dtnStoragePath = path.resolve(this.mediaPath, "dtn_storage");
  private readonly pendingTransfersFile = path.resolve(this.dtnStoragePath, "pending_transfers.json");
  private readonly bundlesPath = path.resolve(this.dtnStoragePath, "bundles");
  private intervalId: NodeJS.Timeout;
  private fileCheckInterval: NodeJS.Timeout;
  private processedFiles = new Set<string>();

  constructor(
    private readonly networkService: NetworkService,
    private readonly storageService: StorageService,
  ) {}

  async onModuleInit() {
    this.logger.log('Inicializando rotina DTN...');
    await this.ensureDirectoriesExist();
    await this.initialFileProcessing();
  }

  onApplicationBootstrap() {
    this.startDTNRoutine();
    this.startFileMonitor();
  }

  startDTNRoutine() {
    this.logger.log('Iniciando rotina DTN principal (intervalo de 30 segundos)');
    
    // Limpa qualquer intervalo existente
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }

    this.intervalId = setInterval(async () => {
      try {
        await this.dtnSyncCycle();
        await this.processPendingTransfers();
      } catch (error) {
        this.logger.error('Erro no ciclo DTN:', error);
      }
    }, 30000);

    // Executa imediatamente o primeiro ciclo
    this.dtnSyncCycle();
  }

  private startFileMonitor() {
    this.logger.log('Iniciando monitoramento de arquivos (intervalo de 5 segundos)');
    
    if (this.fileCheckInterval) {
      clearInterval(this.fileCheckInterval);
    }

    this.fileCheckInterval = setInterval(async () => {
      try {
        await this.processNewFiles();
      } catch (error) {
        this.logger.error('Erro ao monitorar arquivos:', error);
      }
    }, 5000);
  }

  private async initialFileProcessing() {
    try {
      const files = fs.readdirSync(this.mediaPath);
      for (const file of files) {
        await this.processFile(file);
      }
    } catch (error) {
      this.logger.error('Erro no processamento inicial de arquivos:', error);
    }
  }

  private async processNewFiles() {
    try {
      const files = fs.readdirSync(this.mediaPath);
      for (const file of files) {
        if (!this.processedFiles.has(file)) {
          await this.processFile(file);
          this.processedFiles.add(file);
        }
      }
    } catch (error) {
      this.logger.error('Erro ao processar novos arquivos:', error);
    }
  }

  private async processFile(filename: string) {
    const filePath = path.join(this.mediaPath, filename);
    
    try {
      if (!fs.lstatSync(filePath).isFile()) return;

      const regex = /^(.+)-([a-f0-9\-]+)\.\w+$/;
      if (regex.test(filename)) return;

      const fileExt = path.extname(filename);
      const fileName = path.basename(filename, fileExt);
      const newFilename = `${fileName}-${uuidv4()}${fileExt}`;
      const newFilePath = path.join(this.mediaPath, newFilename);

      fs.renameSync(filePath, newFilePath);
      this.logger.log(`Arquivo renomeado: ${filename} -> ${newFilename}`);

      // Cria bundle DTN para o novo arquivo
      await this.createBundleFromFile(newFilename);
    } catch (error) {
      this.logger.error(`Erro ao processar arquivo ${filename}:`, error);
    }
  }

  private async createBundleFromFile(filename: string) {
    const bundleId = `bundle-${uuidv4()}`;
    const bundlePath = path.join(this.bundlesPath, `${bundleId}.json`);
    
    const bundle = {
      id: bundleId,
      filename,
      originalPath: path.join(this.mediaPath, filename),
      status: 'pending',
      createdAt: new Date().toISOString(),
      attempts: 0
    };

    try {
      fs.writeFileSync(bundlePath, JSON.stringify(bundle, null, 2));
      this.logger.log(`Bundle criado para arquivo ${filename}`);
    } catch (error) {
      this.logger.error(`Erro ao criar bundle para ${filename}:`, error);
    }
  }

  private async ensureDirectoriesExist() {
    try {
      if (!fs.existsSync(this.mediaPath)) {
        fs.mkdirSync(this.mediaPath, { recursive: true });
        this.logger.log(`Diretório ${this.mediaPath} criado com sucesso`);
      }
      if (!fs.existsSync(this.dtnStoragePath)) {
        fs.mkdirSync(this.dtnStoragePath, { recursive: true });
        this.logger.log(`Diretório ${this.dtnStoragePath} criado com sucesso`);
      }
      if (!fs.existsSync(this.bundlesPath)) {
        fs.mkdirSync(this.bundlesPath, { recursive: true });
        this.logger.log(`Diretório ${this.bundlesPath} criado com sucesso`);
      }
      if (!fs.existsSync(this.pendingTransfersFile)) {
        fs.writeFileSync(this.pendingTransfersFile, JSON.stringify([], null, 2));
        this.logger.log(`Arquivo ${this.pendingTransfersFile} criado com sucesso`);
      }
    } catch (error) {
      this.logger.error('Erro ao criar diretórios:', error);
      throw error;
    }
  }

  private async dtnSyncCycle() {
    this.logger.log('Iniciando ciclo de sincronização DTN');
    const availableNodes = await this.checkAvailableNodes();
    
    if (availableNodes.length === 0) {
      this.logger.log('Nenhum nó disponível para sincronização');
      return;
    }

    for (const node of availableNodes) {
      try {
        await this.syncWithNode(node);
      } catch (error) {
        this.logger.error(`Erro ao sincronizar com nó ${node.node}:`, error);
      }
    }
  }

  private async checkAvailableNodes() {
    const devices = this.networkService.getNamedDevices();
    const availabilityChecks = devices.map(async (device) => {
      try {
        const response = await fetch(`http://${device.ip}/health`, { 
          timeout: 5000 
        });
        return response.ok ? device : null;
      } catch {
        return null;
      }
    });

    return (await Promise.all(availabilityChecks)).filter(node => node !== null);
  }

  private async syncWithNode(node: any) {
    this.logger.log(`Sincronizando com nó ${node.node} (${node.ip})`);
    
    // 1. Obter lista de bundles disponíveis no nó remoto
    let remoteBundles: string[];
    try {
      const response = await fetch(`http://${node.ip}:3000/ndn/bundles`);
      remoteBundles = await response.json();
    } catch (error) {
      this.logger.error(`Erro ao obter bundles de ${node.node}:`, error);
      return;
    }

    // 2. Obter lista de bundles locais
    const localBundles = fs.readdirSync(this.bundlesPath)
      .filter(file => file.endsWith('.json'))
      .map(file => path.basename(file, '.json'));

    // 3. Determinar bundles para transferência
    const bundlesToDownload = remoteBundles.filter(bundle => !localBundles.includes(bundle));
    
    if (bundlesToDownload.length > 0) {
      this.logger.log(`Bundles para baixar de ${node.node}: ${bundlesToDownload.length}`);
      await this.downloadBundles(bundlesToDownload, node.ip);
    } else {
      this.logger.log(`Nenhum novo bundle para baixar de ${node.node}`);
    }
  }

  private async downloadBundles(bundleIds: string[], nodeIp: string) {
    for (const bundleId of bundleIds) {
      try {
        const response = await fetch(`http://${nodeIp}:3000/ndn/bundle/${bundleId}`);
        if (!response.ok) throw new Error(`Status ${response.status}`);
        
        const bundleData = await response.json();
        const fileResponse = await fetch(`http://${nodeIp}:3000/ndn/file/${bundleData.filename}`);
        
        if (!fileResponse.ok) throw new Error(`Status ${fileResponse.status}`);
        
        const fileBuffer = await fileResponse.buffer();
        const filePath = path.join(this.mediaPath, bundleData.filename);
        
        fs.writeFileSync(filePath, fileBuffer);
        this.logger.log(`Arquivo ${bundleData.filename} baixado com sucesso`);

        // Salva o bundle localmente
        const localBundlePath = path.join(this.bundlesPath, `${bundleId}.json`);
        fs.writeFileSync(localBundlePath, JSON.stringify(bundleData, null, 2));
        
      } catch (error) {
        this.logger.error(`Erro ao baixar bundle ${bundleId}:`, error);
        await this.addPendingTransfer(bundleId, nodeIp, 'download');
      }
    }
  }

  private async addPendingTransfer(bundleId: string, nodeIp: string, type: 'download' | 'upload') {
    try {
      const pendingTransfers = JSON.parse(fs.readFileSync(this.pendingTransfersFile, 'utf-8'));
      pendingTransfers.push({
        bundleId,
        nodeIp,
        type,
        timestamp: new Date().toISOString(),
        attempts: 0
      });
      fs.writeFileSync(this.pendingTransfersFile, JSON.stringify(pendingTransfers, null, 2));
    } catch (error) {
      this.logger.error('Erro ao adicionar transferência pendente:', error);
    }
  }

  private async processPendingTransfers() {
    try {
      const pendingTransfers = JSON.parse(fs.readFileSync(this.pendingTransfersFile, 'utf-8'));
      if (pendingTransfers.length === 0) return;

      this.logger.log(`Processando ${pendingTransfers.length} transferências pendentes`);
      
      const updatedPendingTransfers = [];
      const currentDate = new Date();

      for (const transfer of pendingTransfers) {
        try {
          transfer.attempts = (transfer.attempts || 0) + 1;
          
          if (transfer.type === 'download') {
            await this.downloadBundles([transfer.bundleId], transfer.nodeIp);
          } else {
            await this.uploadBundle(transfer.bundleId, transfer.nodeIp);
          }
          
          this.logger.log(`Transferência ${transfer.bundleId} concluída com sucesso`);
        } catch (error) {
          this.logger.error(`Falha na transferência ${transfer.bundleId}:`, error);
          updatedPendingTransfers.push(transfer);
        }
      }

      fs.writeFileSync(this.pendingTransfersFile, JSON.stringify(updatedPendingTransfers, null, 2));
    } catch (error) {
      this.logger.error('Erro ao processar transferências pendentes:', error);
    }
  }

  private async uploadBundle(bundleId: string, nodeIp: string) {
    try {
      const bundlePath = path.join(this.bundlesPath, `${bundleId}.json`);
      const bundleData = JSON.parse(fs.readFileSync(bundlePath, 'utf-8'));
      const filePath = path.join(this.mediaPath, bundleData.filename);
      
      const fileBuffer = fs.readFileSync(filePath);
      
      const response = await fetch(`http://${nodeIp}:3000/ndn/receive-bundle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bundle: bundleData,
          file: fileBuffer.toString('base64')
        })
      });

      if (!response.ok) throw new Error(`Status ${response.status}`);
      
      this.logger.log(`Bundle ${bundleId} enviado com sucesso para ${nodeIp}`);
    } catch (error) {
      this.logger.error(`Erro ao enviar bundle ${bundleId}:`, error);
      throw error;
    }
  }
}