import { Controller, Get, Post, Body, Res, Param, Logger } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';
import { Response } from 'express';

@Controller('ndn')
export class NdnController {
  private readonly logger = new Logger(NdnController.name);
  private readonly storagePath = path.resolve(__dirname, '../../storage');
  private readonly bundlesPath = path.resolve(this.storagePath, 'bundles');

  constructor() {
    this.ensureDirectoriesExist();
  }

  private ensureDirectoriesExist() {
    if (!fs.existsSync(this.storagePath)) {
      fs.mkdirSync(this.storagePath, { recursive: true });
    }
    if (!fs.existsSync(this.bundlesPath)) {
      fs.mkdirSync(this.bundlesPath, { recursive: true });
    }
  }

  @Get('bundles')
  async listBundles() {
    try {
      if (!fs.existsSync(this.bundlesPath)) {
        return [];
      }
      
      const bundles = fs.readdirSync(this.bundlesPath)
        .filter(file => file.endsWith('.json'))
        .map(file => path.basename(file, '.json'));
      
      return bundles;
    } catch (error) {
      this.logger.error('Erro ao listar bundles:', error);
      throw error;
    }
  }

  @Get('bundle/:id')
  async getBundle(@Param('id') id: string, @Res() res: Response) {
    try {
      const bundlePath = path.join(this.bundlesPath, `${id}.json`);
      
      if (!fs.existsSync(bundlePath)) {
        return res.status(404).send('Bundle não encontrado');
      }

      const bundleData = JSON.parse(fs.readFileSync(bundlePath, 'utf-8'));
      return res.json(bundleData);
    } catch (error) {
      this.logger.error(`Erro ao recuperar bundle ${id}:`, error);
      return res.status(500).send('Erro interno do servidor');
    }
  }

  @Get('file/:filename')
  async getFile(@Param('filename') filename: string, @Res() res: Response) {
    try {
      const filePath = path.join(this.storagePath, filename);
      
      if (!fs.existsSync(filePath)) {
        return res.status(404).send('Arquivo não encontrado');
      }

      return res.sendFile(filePath);
    } catch (error) {
      this.logger.error(`Erro ao recuperar arquivo ${filename}:`, error);
      return res.status(500).send('Erro interno do servidor');
    }
  }

  @Post('receive-bundle')
  async receiveBundle(@Body() body: any, @Res() res: Response) {
    try {
      const { bundle, file } = body;
      
      if (!bundle || !bundle.id || !file) {
        return res.status(400).send('Dados do bundle inválidos');
      }

      // Salva o bundle
      const bundlePath = path.join(this.bundlesPath, `${bundle.id}.json`);
      fs.writeFileSync(bundlePath, JSON.stringify(bundle, null, 2));

      // Salva o arquivo
      const fileBuffer = Buffer.from(file, 'base64');
      const filePath = path.join(this.storagePath, bundle.filename);
      fs.writeFileSync(filePath, fileBuffer);

      this.logger.log(`Bundle ${bundle.id} recebido e armazenado`);
      return res.status(200).send('Bundle recebido com sucesso');
    } catch (error) {
      this.logger.error('Erro ao receber bundle:', error);
      return res.status(500).send('Erro ao processar bundle');
    }
  }

  @Get('files')
  async listFiles(@Res() res: Response) {
    try {
      if (!fs.existsSync(this.storagePath)) {
        return res.json([]);
      }
      
      const files = fs.readdirSync(this.storagePath)
        .filter(file => fs.lstatSync(path.join(this.storagePath, file)).isFile());
      
      return res.json(files);
    } catch (error) {
      this.logger.error('Erro ao listar arquivos:', error);
      return res.status(500).send('Erro interno do servidor');
    }
  }

  @Post('file')
  async receiveFile(@Body() body: any, @Res() res: Response) {
    try {
      const { fileName, sessao, node } = body;
      
      if (!fileName) {
        return res.status(400).send('Nome do arquivo é obrigatório');
      }

      // Aqui você pode processar o arquivo recebido
      // Exemplo: salvar metadados ou registrar a transferência
      this.logger.log(`Arquivo ${fileName} recebido de ${node}, sessão ${sessao}`);
      
      return res.status(201).send('Arquivo recebido com sucesso');
    } catch (error) {
      this.logger.error('Erro ao receber arquivo:', error);
      return res.status(500).send('Erro ao processar arquivo');
    }
  }
}