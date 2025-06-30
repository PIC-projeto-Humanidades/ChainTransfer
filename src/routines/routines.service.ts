import { Injectable, OnModuleInit, OnApplicationBootstrap, Logger } from '@nestjs/common';
import { NetworkService } from '../network/network.service';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { StorageService } from '../storage/storage.service';
import fetch from 'node-fetch';
import { LogsService } from '../logs/logs.service';
import * as fs from 'fs';

@Injectable()
export class RoutinesService implements OnModuleInit, OnApplicationBootstrap {
  private readonly logger = new Logger(RoutinesService.name);
  private readonly mediaPath = path.resolve(process.cwd(), "media_data");
  private readonly dtnStoragePath = path.resolve(this.mediaPath, "dtn_storage");
  private readonly pendingTransfersFile = path.resolve(this.dtnStoragePath, "pending_transfers.json");
  private readonly bundlesPath = path.resolve(this.dtnStoragePath, "bundles");
  private readonly syncStatsFile = path.resolve(this.dtnStoragePath, "sync_stats.json");
  private intervalId: NodeJS.Timeout;
  private fileCheckInterval: NodeJS.Timeout;
  private processedFiles = new Set<string>();

  constructor(
    private readonly networkService: NetworkService,
    private readonly storageService: StorageService,
    private readonly logsService: LogsService,
  ) {}

  async onModuleInit() {
    this.logger.log('Initializing DTN routine...');
    await this.ensureDirectoriesExist();
    await this.initialFileProcessing();
  }

  onApplicationBootstrap() {
    this.startDTNRoutine();
    this.startFileMonitor();
  }

  startDTNRoutine() {
    this.logger.log('Starting main DTN routine (30s interval)');
    
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }

    this.intervalId = setInterval(async () => {
      try {
        await this.dtnSyncCycle();
        await this.processPendingTransfers();
      } catch (error) {
        this.logger.error('Error in DTN cycle:', error);
      }
    }, 30000);

    this.dtnSyncCycle();
  }

  private startFileMonitor() {
    this.logger.log('Starting file monitoring (5s interval)');
    
    if (this.fileCheckInterval) {
      clearInterval(this.fileCheckInterval);
    }

    this.fileCheckInterval = setInterval(async () => {
      try {
        await this.processNewFiles();
      } catch (error) {
        this.logger.error('Error monitoring files:', error);
      }
    }, 5000);
  }

  private async ensureDirectoriesExist() {
    try {
        this.logger.log(`Checking/creating directories at: ${this.mediaPath}`);
        
        // Create media_data directory if it doesn't exist
        if (!fs.existsSync(this.mediaPath)) {
            this.logger.log(`Creating media directory: ${this.mediaPath}`);
            fs.mkdirSync(this.mediaPath, { recursive: true });
            this.logger.log(`Media directory created successfully`);
        }

        // Create dtn_storage directory
        if (!fs.existsSync(this.dtnStoragePath)) {
            this.logger.log(`Creating DTN storage directory: ${this.dtnStoragePath}`);
            fs.mkdirSync(this.dtnStoragePath, { recursive: true });
        }

        // Create bundles directory
        if (!fs.existsSync(this.bundlesPath)) {
            this.logger.log(`Creating bundles directory: ${this.bundlesPath}`);
            fs.mkdirSync(this.bundlesPath, { recursive: true });
        }

        // Initialize pending transfers file
        if (!fs.existsSync(this.pendingTransfersFile)) {
            this.logger.log(`Initializing pending transfers file`);
            fs.writeFileSync(this.pendingTransfersFile, JSON.stringify([], null, 2));
        }

        // Initialize sync stats file
        if (!fs.existsSync(this.syncStatsFile)) {
            this.logger.log(`Initializing sync stats file`);
            fs.writeFileSync(this.syncStatsFile, JSON.stringify({}, null, 2));
        }

        this.logger.log('All directories and files verified/created');
    } catch (error) {
        this.logger.error('Error creating directories:', error);
        throw new Error(`Failed to initialize storage directories: ${error.message}`);
    }
}

  private async initialFileProcessing() {
    try {
      const files = await this.storageService.listFiles();
      for (const file of files) {
        await this.processFile(file);
      }
    } catch (error) {
      this.logger.error('Error in initial file processing:', error);
    }
  }

  private async processNewFiles() {
    try {
      this.logger.debug('Checking for new files...');
      const files = await this.storageService.listFiles();
      this.logger.debug(`Found files: ${JSON.stringify(files)}`);
      
      for (const file of files) {
        if (!this.processedFiles.has(file)) {
          this.logger.debug(`Processing new file: ${file}`);
          await this.processFile(file);
          this.processedFiles.add(file);
        }
      }
    } catch (error) {
      this.logger.error('Error processing new files:', error);
    }
}

private async processFile(filename: string) {
    try {
      this.logger.debug(`Starting to process file: ${filename}`);
      const filePath = path.join(this.mediaPath, filename);
      
      if (!fs.existsSync(filePath)) {
        this.logger.warn(`File does not exist: ${filePath}`);
        return;
      }
      
      if (!fs.lstatSync(filePath).isFile()) {
        this.logger.warn(`Path is not a file: ${filePath}`);
        return;
      }

      const regex = /^(.+)-([a-f0-9\-]{36})\.\w+$/;
      if (regex.test(filename)) {
        this.logger.debug(`File already has UUID: ${filename}`);
        return;
      }

      const fileExt = path.extname(filename);
      const fileName = path.basename(filename, fileExt);
      const newFilename = `${fileName}-${uuidv4()}${fileExt}`;

      this.logger.debug(`Renaming file to: ${newFilename}`);
      await this.storageService.renameFile(filename, newFilename);
      this.logger.log(`File renamed: ${filename} -> ${newFilename}`);

      await this.createBundleFromFile(newFilename);
    } catch (error) {
      this.logger.error(`Error processing file ${filename}:`, error);
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
      attempts: 0,
      sessionId: `session-${new Date().getTime()}`,
      node: this.networkService.getSelfNodeName()
    };

    try {
      fs.writeFileSync(bundlePath, JSON.stringify(bundle, null, 2));
      this.logger.log(`Bundle created for file ${filename}`);
    } catch (error) {
      this.logger.error(`Error creating bundle for ${filename}:`, error);
    }
  }

  private async dtnSyncCycle() {
    this.logger.log('Starting DTN sync cycle');
    const availableNodes = await this.checkAvailableNodes();
    
    if (availableNodes.length === 0) {
      this.logger.log('No nodes available for synchronization');
      return;
    }

    for (const node of availableNodes) {
      try {
        await this.syncWithNode(node);
      } catch (error) {
        this.logger.error(`Error syncing with node ${node.node}:`, error);
      }
    }
  }

  private async checkAvailableNodes() {
    const devices = this.networkService.getNamedDevices();
    
    const availabilityChecks = devices.map(async (device) => {
      if (device.selfhosted) {
        this.logger.debug(`Ignoring selfhosted node: ${device.ip}`);
        return null;
      }

      try {
        const response = await fetch(`http://${device.ip}:3000/health`, { 
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
    try {
      // Skip sync with self using network service
      if (this.networkService.isSelfHosted(node.ip)) {
        this.logger.log(`Skipping sync with self node (${node.ip})`);
        return;
      }
  
      this.logger.log(`Starting sync with node ${node.node} (${node.ip})`);
      
      let remoteBundles: string[];
      try {
        const response = await fetch(`http://${node.ip}:3000/ndn/bundles`, {
          timeout: 10000
        });
        
        if (!response.ok) {
          throw new Error(`HTTP status ${response.status}`);
        }
        
        remoteBundles = await response.json();
      } catch (error) {
        this.logger.error(`Failed to get bundles from ${node.node}:`, error);
        throw error;
      }
  
      const localBundles = fs.existsSync(this.bundlesPath) 
        ? fs.readdirSync(this.bundlesPath)
            .filter(file => file.endsWith('.json'))
            .map(file => path.basename(file, '.json'))
        : [];
  
      const bundlesToDownload = remoteBundles.filter(bundle => 
        !localBundles.includes(bundle) &&
        !this.isBundlePending(bundle)
      );
  
      if (bundlesToDownload.length > 0) {
        this.logger.log(`Found ${bundlesToDownload.length} new bundles in ${node.node}`);
        await this.downloadBundles(bundlesToDownload, node.ip);
        await this.updateSyncStats(node.node, bundlesToDownload.length);
      } else {
        this.logger.debug(`No new bundles available in ${node.node}`);
      }
  
      this.logger.log(`Sync with ${node.node} completed successfully`);
    } catch (error) {
      this.logger.error(`Error during sync with ${node.node}:`, error);
      throw error;
    }
  }
  
  private async downloadBundles(bundleIds: string[], nodeIp: string) {
    for (const bundleId of bundleIds) {
      try {
        const response = await fetch(`http://${nodeIp}:3000/ndn/bundle/${bundleId}`);
        if (!response.ok) throw new Error(`Status ${response.status}`);
        
        const bundleData = await response.json();
        
        const localFiles = await this.storageService.listFiles();
        if (localFiles.includes(bundleData.filename)) {
          this.logger.log(`File ${bundleData.filename} already exists locally`);
          continue;
        }

        const fileResponse = await fetch(`http://${nodeIp}:3000/ndn/file/${bundleData.filename}`);
        if (!fileResponse.ok) throw new Error(`Status ${fileResponse.status}`);
        
        const fileBuffer = await fileResponse.buffer();
        
        await this.storageService.saveFile({
          filename: bundleData.filename,
          buffer: fileBuffer,
          sessionId: bundleData.sessionId || 'default-session',
          node: bundleData.node || 'unknown'
        });

        await this.logsService.logDownload({
          fileName: bundleData.filename,
          sessao: bundleData.sessionId || 'default-session',
          node: bundleData.node || 'unknown'
        });

        const localBundlePath = path.join(this.bundlesPath, `${bundleId}.json`);
        fs.writeFileSync(localBundlePath, JSON.stringify(bundleData, null, 2));
        
      } catch (error) {
        this.logger.error(`Error downloading bundle ${bundleId}:`, error);
        await this.addPendingTransfer(bundleId, nodeIp, 'download');
      }
    }
  }

  private async addPendingTransfer(bundleId: string, nodeIp: string, type: 'download' | 'upload') {
    try {
      const pendingTransfers = JSON.parse(fs.readFileSync(this.pendingTransfersFile, 'utf-8'));
      
      const existingTransfer = pendingTransfers.find((t: any) => 
        t.bundleId === bundleId && t.nodeIp === nodeIp && t.type === type
      );
      
      if (!existingTransfer) {
        pendingTransfers.push({
          bundleId,
          nodeIp,
          type,
          timestamp: new Date().toISOString(),
          attempts: 0
        });
        fs.writeFileSync(this.pendingTransfersFile, JSON.stringify(pendingTransfers, null, 2));
      }
    } catch (error) {
      this.logger.error('Error adding pending transfer:', error);
    }
  }

  private async processPendingTransfers() {
    try {
      const pendingTransfers = JSON.parse(fs.readFileSync(this.pendingTransfersFile, 'utf-8'));
      if (pendingTransfers.length === 0) return;

      this.logger.log(`Processing ${pendingTransfers.length} pending transfers`);
      
      const updatedPendingTransfers = [];

      for (const transfer of pendingTransfers) {
        try {
          transfer.attempts = (transfer.attempts || 0) + 1;
          
          if (transfer.type === 'download') {
            await this.downloadBundles([transfer.bundleId], transfer.nodeIp);
          } else {
            await this.uploadBundle(transfer.bundleId, transfer.nodeIp);
          }
        } catch (error) {
          this.logger.error(`Failed transfer ${transfer.bundleId}:`, error);
          
          if (transfer.attempts < 5) {
            updatedPendingTransfers.push(transfer);
          } else {
            this.logger.warn(`Removing transfer ${transfer.bundleId} after 5 failed attempts`);
          }
        }
      }

      fs.writeFileSync(this.pendingTransfersFile, JSON.stringify(updatedPendingTransfers, null, 2));
    } catch (error) {
      this.logger.error('Error processing pending transfers:', error);
    }
  }

  private async uploadBundle(bundleId: string, nodeIp: string) {
    try {
      const bundlePath = path.join(this.bundlesPath, `${bundleId}.json`);
      const bundleData = JSON.parse(fs.readFileSync(bundlePath, 'utf-8'));
      
      const fileBuffer = await this.storageService.getFileBuffer(bundleData.filename);
      
      const response = await fetch(`http://${nodeIp}:3000/ndn/receive-bundle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bundle: bundleData,
          file: fileBuffer.toString('base64')
        })
      });

      if (!response.ok) throw new Error(`Status ${response.status}`);
      
      this.logger.log(`Bundle ${bundleId} successfully sent to ${nodeIp}`);
    } catch (error) {
      this.logger.error(`Error sending bundle ${bundleId}:`, error);
      throw error;
    }
  }

  private isBundlePending(bundleId: string): boolean {
    try {
      const pendingTransfers = JSON.parse(fs.readFileSync(this.pendingTransfersFile, 'utf-8'));
      return pendingTransfers.some((t: any) => t.bundleId === bundleId);
    } catch {
      return false;
    }
  }
  
  private async updateSyncStats(nodeName: string, newBundles: number) {
    try {
      const stats = JSON.parse(fs.readFileSync(this.syncStatsFile, 'utf-8')) || {};
      
      if (!stats[nodeName]) {
        stats[nodeName] = { syncCount: 0, totalBundles: 0 };
      }
      
      stats[nodeName].syncCount = (stats[nodeName].syncCount || 0) + 1;
      stats[nodeName].totalBundles = (stats[nodeName].totalBundles || 0) + newBundles;
      stats[nodeName].lastSync = new Date().toISOString();
      
      fs.writeFileSync(this.syncStatsFile, JSON.stringify(stats, null, 2));
    } catch (error) {
      this.logger.error('Error updating sync stats:', error);
    }
  }
}