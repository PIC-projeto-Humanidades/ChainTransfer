import { NetworkModule } from 'src/network/network.module';
import { MonitoringController } from './monitoring.controller';
/*
https://docs.nestjs.com/modules
*/

import { Module } from '@nestjs/common';
import { LogsModule } from 'src/logs/logs.module';

@Module({
    imports: [NetworkModule,LogsModule],
    controllers: [
        MonitoringController,],
    providers: [],
})
export class MonitoringModule { }
