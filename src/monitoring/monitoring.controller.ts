/*
https://docs.nestjs.com/controllers#controllers
*/

import { Body, Controller, Get, Param, Post } from '@nestjs/common';
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
    @Post('feedback')
    async receiveFeedback(@Body() feedbackData: { node: string, fileName: string,sessao: string, }) {
        const { fileName,sessao,node } = feedbackData;

        if (!node || !sessao) {
            return { error: "Dados inválidos. É necessário informar o node e os arquivos recebidos." };
        }

        console.log(`Feedback recebido do nó ${node}:`, fileName);

        // Registra os arquivos recebidos no log
        await this.logsService.logDownload({ fileName,sessao,node })

        return { message: "Feedback processado com sucesso!", node, fileName };
    }
}


// this.logsService.logDownload({ fileName,sessao,node })