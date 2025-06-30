import * as fs from "fs";
import * as path from "path";
import { Injectable, Logger } from '@nestjs/common';
import { LogsService } from "../logs/logs.service";

@Injectable()
export class StorageService {
    private readonly logger = new Logger(StorageService.name);
    private readonly storagePath: string;

    constructor(private readonly logsService: LogsService) {
        this.storagePath = path.resolve(process.cwd(), "media_data");
        this.ensureDirectoryExists();
    }

    private ensureDirectoryExists() {
        try {
            if (!fs.existsSync(this.storagePath)) {
                this.logger.log(`Creating storage directory: ${this.storagePath}`);
                fs.mkdirSync(this.storagePath, { recursive: true });
            }
        } catch (error) {
            this.logger.error('Failed to create storage directory:', error);
            throw error;
        }
    }

    async saveFile({ filename, buffer, sessionId, node }: { 
        filename: string, 
        buffer: Buffer, 
        sessionId: string,
        node: string 
    }) {
        const filePath = path.join(this.storagePath, filename);
        try {
            await fs.promises.writeFile(filePath, buffer);
            await this.logsService.logDownload({
                fileName: filename,
                sessao: sessionId,
                node: node
            });
            return filePath;
        } catch (error) {
            this.logger.error(`Failed to save file ${filename}:`, error);
            throw error;
        }
    }

    async renameFile(oldName: string, newName: string): Promise<string> {
        const oldPath = path.join(this.storagePath, oldName);
        const newPath = path.join(this.storagePath, newName);
        
        try {
            // Verifica se o arquivo original existe
            if (!await this.fileExists(oldName)) {
                throw new Error(`Original file does not exist: ${oldName}`);
            }

            await fs.promises.rename(oldPath, newPath);
            this.logger.log(`File renamed successfully: ${oldName} -> ${newName}`);
            return newPath;
        } catch (error) {
            this.logger.error(`Error renaming file ${oldName}:`, error);
            throw error;
        }
    }

    async getFileBuffer(filename: string): Promise<Buffer> {
        try {
            return await fs.promises.readFile(path.join(this.storagePath, filename));
        } catch (error) {
            this.logger.error(`Error reading file ${filename}:`, error);
            throw error;
        }
    }

    async listFiles(): Promise<string[]> {
        try {
            const files = await fs.promises.readdir(this.storagePath);
            const filteredFiles = await Promise.all(
                files.map(async file => {
                    const stat = await fs.promises.lstat(path.join(this.storagePath, file));
                    return stat.isFile() ? file : null;
                })
            );
            return filteredFiles.filter(Boolean) as string[];
        } catch (error) {
            this.logger.error('Error listing files:', error);
            throw error;
        }
    }

    async fileExists(filename: string): Promise<boolean> {
        try {
            await fs.promises.access(path.join(this.storagePath, filename), fs.constants.F_OK);
            return true;
        } catch {
            return false;
        }
    }
}