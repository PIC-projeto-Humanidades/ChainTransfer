import { RoutinesModule } from './routines/routines.module';
import { LogsModule } from './logs/logs.module';
import { MonitoringModule } from './monitoring/monitoring.module';
import { NetworkModule } from './network/network.module';
import { IdentifyModule } from './identify/identify.module';
import { StorageModule } from './storage/storage.module';
import { NdnModule } from './ndn/ndn.module';
import { NdnController } from './ndn/ndn.controller';
import { Module } from '@nestjs/common';
import { SequelizeModule } from '@nestjs/sequelize';

@Module({
  imports: [
    RoutinesModule,
    LogsModule,
    MonitoringModule,
    NetworkModule,
    IdentifyModule,
    StorageModule,
    NdnModule,
    SequelizeModule.forRoot({
      dialect: 'sqlite',
      storage: './media.db',
      autoLoadModels: true,
      synchronize: true, // Sincroniza automaticamente as tabelas
    }),
  ],
  controllers: [
    NdnController,],
  providers: [],
})
export class AppModule { }
