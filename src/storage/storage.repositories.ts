/*
https://docs.nestjs.com/providers#services
*/
import * as fs from "fs";
import * as path from "path";
import { Injectable, NotFoundException } from '@nestjs/common';

@Injectable()
export class StorageRepository {
    private readonly basePath = path.resolve(__dirname, "./../../media_data");

    getFile(fileName: string): string {
        const filePath = path.resolve(this.basePath, fileName);
        if (!fs.existsSync(filePath)) {
            throw new NotFoundException("Arquivo não encontrado");
        }
        return filePath;
    }

    listFiles(): string[] {
        if (!fs.existsSync(this.basePath)) {
            throw new NotFoundException("Diretório não encontrado");
        }
        return fs.readdirSync(this.basePath);
    }
}