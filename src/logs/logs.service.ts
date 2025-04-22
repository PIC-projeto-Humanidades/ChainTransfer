/*
https://docs.nestjs.com/providers#services
*/
import * as fs from "fs";
import * as path from "path";
import { Injectable } from '@nestjs/common';
import { InjectModel } from "@nestjs/sequelize";
import { Log } from "./models/logsDonwload.entity";

@Injectable()
export class LogsService { 

    private readonly logFilePath = path.resolve(__dirname, "./../../logs/download_logs.txt");
    constructor(@InjectModel(Log) private logModel: typeof Log) {}

    async logDownload({ fileName,sessao,node }:{fileName: string, sessao: string, node: string}) {
        await this.logModel.create({ fileName, sessao, node, date: new Date() });
    }

    async getLogsBySession(sessao: string) {
        return this.logModel.findAll({ where: { sessao } });
    }
}
