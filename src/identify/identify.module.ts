import { IdentifyController } from './identify.controller';
/*
https://docs.nestjs.com/modules
*/

import { Module } from '@nestjs/common';

@Module({
    imports: [],
    controllers: [
        IdentifyController,],
    providers: [],
})
export class IdentifyModule { }
