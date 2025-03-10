import * as fs from "fs";
import * as path from "path";
import { Injectable, NotFoundException } from '@nestjs/common';
import { StorageRepository } from "./storage.repositories";
import { LogsService } from "src/logs/logs.service";

@Injectable()
export class StorageService {
    constructor(private readonly storageRepository: StorageRepository, private readonly logsService: LogsService ) {}

    async getFile({ fileName,sessao,node }:{ fileName:string,sessao:string ,node:string }) {
        let filesHasDownloaded = await this.logsService.getLogsBySession(sessao)
        let hasFile = filesHasDownloaded.filter((e)=>e.sessao==sessao && e.node==node && e.fileName==fileName)
        if(hasFile.length>0){
            return ""
        }
        this.logsService.logDownload({ fileName,sessao,node })
        return this.storageRepository.getFile(fileName);
    }

    listFiles() {
        return this.storageRepository.listFiles();
    }
}
