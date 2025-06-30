/*
https://docs.nestjs.com/modules
*/

import { Module } from '@nestjs/common';
import { HealthController } from './controller.health';

@Module({
    imports: [],
    controllers: [HealthController],
    providers: [],
})
export class HealthModule { }
