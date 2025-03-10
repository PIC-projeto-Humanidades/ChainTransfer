import { NdnService } from './ndn.service';
/*
https://docs.nestjs.com/modules
*/

import { Module } from '@nestjs/common';
import { NdnController } from './ndn.controller';
import { StorageModule } from 'src/storage/storage.module';
import { NetworkModule } from 'src/network/network.module';

@Module({
    imports: [StorageModule,NetworkModule],
    controllers: [NdnController],
    providers: [
        NdnService,],
})
export class NdnModule { }
