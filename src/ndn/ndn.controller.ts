import { Body, Controller, Get, NotFoundException, Param, Post, Query, Req, Res } from '@nestjs/common';
import { Response } from 'express';
import { StorageService } from 'src/storage/storage.service';
import * as fs from "fs";
import { NetworkService } from 'src/network/network.service';

@Controller('ndn')
export class NdnController {
    constructor(
        private readonly storageService: StorageService,
        private readonly networkService: NetworkService 
    ) {}

    @Post('/file')
    async downloadFile(  
    @Body() body: { sessao: string, node: string,fileName: string },
    @Res() res: Response) {
        const { fileName,sessao,node } = body;
        const filePath =await this.storageService.getFile({ fileName,sessao,node });
        
        if (!filePath) {
            console.log(`Download JÁ FOI realizado: Arquivo: ${fileName}, Sessão: ${sessao}`);
            return res.status(200).json({ status: "OK", message: "Download já realizado" });
        }
        res.download(filePath);
    }
    @Get('files')
    async listFiles(@Res() res: Response) {
        const list = this.storageService.listFiles();

        res.status(200).json(list);
    }
}