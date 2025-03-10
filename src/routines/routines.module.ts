import { NetworkModule } from 'src/network/network.module';
import { RoutinesService } from './routines.service';
/*
https://docs.nestjs.com/modules
*/

import { Module } from '@nestjs/common';
import { StorageModule } from 'src/storage/storage.module';

@Module({
    imports: [NetworkModule,StorageModule],
    controllers: [],
    providers: [
        RoutinesService,],
        exports:[RoutinesService]
})
export class RoutinesModule { }
