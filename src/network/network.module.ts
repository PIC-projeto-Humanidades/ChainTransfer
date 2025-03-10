import { NetworkService } from './network.service';
/*
https://docs.nestjs.com/modules
*/

import { Module } from '@nestjs/common';

@Module({
    imports: [],
    controllers: [],
    providers: [
        NetworkService,],
        exports:[NetworkService]
})
export class NetworkModule { }
