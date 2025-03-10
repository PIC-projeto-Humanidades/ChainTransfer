/*
https://docs.nestjs.com/controllers#controllers
*/

import { Controller, Get, Param } from '@nestjs/common';
import { LogsService } from 'src/logs/logs.service';
import { NetworkService } from 'src/network/network.service';

@Controller("monitoring")
export class MonitoringController {
    constructor(private readonly networkService: NetworkService,private readonly logsService: LogsService) {}

    @Get('devices')
    async getConnectedDevices() {
        return this.networkService.getConnectedDevices();
    }

    
    
    @Get('status/:sessao')
    async statusDownload(
        @Param('sessao') sessao: string,
    ) {
        return this.logsService.getLogsBySession(sessao)
    }
}
