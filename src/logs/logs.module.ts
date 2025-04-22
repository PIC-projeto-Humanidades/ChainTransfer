import { SequelizeModule } from '@nestjs/sequelize';
import { LogsService } from './logs.service';
/*
https://docs.nestjs.com/modules
*/

import { Module } from '@nestjs/common';
import { Log } from './models/logsDonwload.entity';

@Module({
    imports: [SequelizeModule.forFeature([Log])],
    controllers: [],
    providers: [
        LogsService,],
        exports:[LogsService]
})
export class LogsModule { }
