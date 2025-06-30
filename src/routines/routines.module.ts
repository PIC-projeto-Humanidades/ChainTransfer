// src/routines/routines.module.ts
import { Module } from '@nestjs/common';
import { RoutinesService } from './routines.service';
import { NetworkModule } from '../network/network.module';
import { StorageModule } from '../storage/storage.module';
import { LogsModule } from '../logs/logs.module';

@Module({
  imports: [
    NetworkModule,
    StorageModule,
    LogsModule,
  ],
  providers: [RoutinesService],
  exports: [RoutinesService],
})
export class RoutinesModule {}