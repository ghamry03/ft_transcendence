import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { ServeStaticModule} from '@nestjs/serve-static'; // New
import { join } from 'path'; // New
import { TypeOrmModule } from '@nestjs/typeorm';

@Module({
  imports: [
ServeStaticModule.forRoot({ // New
      rootPath: join(__dirname, '..', '../ft_transcendence/dist'), // New
    }),
TypeOrmModule.forRoot({
      type: 'postgres',
      host: 'localhost',
      port: 6000,
      password: 'basicPass',
      username: 'user',
      entities: [],
      database: 'pingpong',
      synchronize: true,
      logging: true,
    })
],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
