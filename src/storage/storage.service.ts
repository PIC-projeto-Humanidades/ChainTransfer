import * as fs from "fs";
import * as path from "path";
import { Injectable } from '@nestjs/common';
import { LogsService } from "../logs/logs.service";

@Injectable()
export class StorageService {
    private readonly storagePath = path.resolve(__dirname, "../../media_data");

    constructor(private readonly logsService: LogsService) {
        this.ensureDirectoryExists();
    }

    private ensureDirectoryExists() {
        if (!fs.existsSync(this.storagePath)) {
            fs.mkdirSync(this.storagePath, { recursive: true });
        }
    }

    async saveFile({ filename, buffer, sessionId, node }: { 
        filename: string, 
        buffer: Buffer, 
        sessionId: string,
        node: string 
    }) {
        const filePath = path.join(this.storagePath, filename);
        fs.writeFileSync(filePath, buffer);
        
        await this.logsService.logDownload({
            fileName: filename,
            sessao: sessionId,
            node: node
        });
        
        return filePath;
    }

    async renameFile(oldName: string, newName: string) {
        const oldPath = path.join(this.storagePath, oldName);
        const newPath = path.join(this.storagePath, newName);
        fs.renameSync(oldPath, newPath);
        return newPath;
    }

    async getFileBuffer(filename: string): Promise<Buffer> {
        const filePath = path.join(this.storagePath, filename);
        return fs.readFileSync(filePath);
    }

    async listFiles(): Promise<string[]> {
        return fs.readdirSync(this.storagePath)
            .filter(file => fs.lstatSync(path.join(this.storagePath, file)).isFile());
    }

    async fileExists(filename: string): Promise<boolean> {
        return fs.existsSync(path.join(this.storagePath, filename));
    }
}