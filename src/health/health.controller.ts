/*
https://docs.nestjs.com/controllers#controllers
*/

import { Body, Controller, Get, Param, Post } from '@nestjs/common';
import { LogsService } from 'src/logs/logs.service';
import { NetworkService } from 'src/network/network.service';

@Controller("health")
export class HealthController {
    constructor() {}

    @Get()
    async status() {
        return {status:200};
    }

   
}


// this.logsService.logDownload({ fileName,sessao,node })