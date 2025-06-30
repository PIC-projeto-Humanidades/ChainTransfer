import { RoutinesModule } from './routines/routines.module';
import { LogsModule } from './logs/logs.module';
import { MonitoringModule } from './monitoring/monitoring.module';
import { NetworkModule } from './network/network.module';
import { IdentifyModule } from './identify/identify.module';
import { StorageModule } from './storage/storage.module';
import { NdnModule } from './ndn/ndn.module';
import { NdnController } from './ndn/ndn.controller';
import { Module, OnModuleInit } from '@nestjs/common';
import { SequelizeModule } from '@nestjs/sequelize';
import { RoutinesService } from './routines/routines.service';
import { HealthModule } from 'health/health.module';

@Module({
  imports: [
    RoutinesModule,
    LogsModule,
    MonitoringModule,
    NetworkModule,
    IdentifyModule,
    StorageModule,
    NdnModule,
    HealthModule,
    SequelizeModule.forRoot({
      dialect: 'sqlite',
      storage: './media.db',
      autoLoadModels: true,
      synchronize: true,
    }),
  ],
  controllers: [NdnController],
  providers: [],
})
export class AppModule implements OnModuleInit {
  constructor(private readonly routineService: RoutinesService) {}

  onModuleInit() {
    console.log('AppModule inicializado!');
    this.routineService.startDTNRoutine(); 
  }
}