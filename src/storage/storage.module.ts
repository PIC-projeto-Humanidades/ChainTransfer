import { LogsModule } from 'src/logs/logs.module';
import { StorageRepository } from './storage.repositories';
import { StorageService } from './storage.service';
/*
https://docs.nestjs.com/modules
*/

import { Module } from '@nestjs/common';

@Module({
    imports: [LogsModule],
    controllers: [],
    providers: [
        StorageService,StorageRepository],
        exports:[StorageService]
})
export class StorageModule { }
