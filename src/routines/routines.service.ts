import { Injectable, OnModuleInit } from '@nestjs/common';
import e from 'express';
import { NetworkService } from 'src/network/network.service';
import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid'; // Para gerar UID caso necessário
import { StorageService } from 'src/storage/storage.service';
import fetch from 'node-fetch';

@Injectable()
export class RoutinesService implements OnModuleInit {
  private readonly mediaPath = path.resolve(__dirname, "./../../media_data");

    constructor(
        private readonly networkService: NetworkService ,
        private readonly storageService: StorageService ,
    ) {}
    async onModuleInit() {
    console.log('Rotina inicializada!');
    await this.checkAndRenameFiles();
    this.startRoutine();
  }

  startRoutine() {
    console.log('Iniciando rotina recorrente a cada 2 segundos...');
    
    setInterval(async () => {
        try {
            let res = await this.networkService.getConnectedDevices();
            const nodesToCheck = this.networkService.getNamedDevices();
            const macToNodeMap = new Map(nodesToCheck.map(device => [device.mac, device.node]));

            const foundDevices = res
                .filter(device => macToNodeMap.has(device.mac))
                .map(device => ({
                    node: macToNodeMap.get(device.mac),
                    mac: device.mac,
                    ip: device.ip
                }));

            if (foundDevices.length > 0) {
                this.routine_foundDevice(foundDevices);
            } else {
                console.log("Nenhum dispositivo correspondente encontrado.");
            }
        } catch (error) {
            console.error("Erro ao obter dispositivos conectados:", error);
        }
    }, 2000);
}


  async routine_foundDevice(foundDevices: any[]) {
    const currentDate = new Date();
    const formattedDate = `${currentDate.getDate()}-${currentDate.getMonth() + 1}-${currentDate.getFullYear()}`;
    const sessionId = `sessao-${formattedDate}`;

    const { node, mac, ip } = foundDevices[0];
    console.log("Dispositivo - IP:", ip);
    console.log("Dispositivo - MAC:", mac);
    console.log("Dispositivo - Node:", node);
    console.log("\n");

    let res: any;
    let remoteFiles: string[] = [];
    let localFiles: string[] = [];

    try {
        const res = await fetch(`http://${ip}:3000/ndn/files`);
        remoteFiles = await res.json();
    } catch (error) {
        console.error("Erro ao obter lista de arquivos remotos:", error);
        return; // Sai da função se não conseguir obter os arquivos
    }

    try {
        localFiles = await this.storageService.listFiles();
    } catch (error) {
        console.error("Erro ao obter lista de arquivos locais:", error);
        return;
    }

    // Filtra os arquivos que não existem localmente
    const filesToDownload = remoteFiles.filter(file => !localFiles.includes(file));
    let failedFiles: string[] = [];

    for (let fileName of filesToDownload) {
        try {
            let responseDownloadFile = await fetch(`http://${ip}:3000/ndn/file`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    fileName: fileName,
                    sessao: sessionId,
                    node: node
                })
            });

            if (responseDownloadFile.status === 200 || responseDownloadFile.status === 201) {
                console.log(`Arquivo ${fileName} enviado com sucesso (status ${responseDownloadFile.status}).`);
                
                if(responseDownloadFile.status === 201){
                  // Envia feedback
                  await fetch(`http://${ip}:3000/monitoring/feedback`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        fileName: fileName,
                        sessao: sessionId,
                        node: node
                    })
                  });
                }
                
            } else {
                console.warn(`Falha ao enviar ${fileName}. Código: ${responseDownloadFile.status}`);
                failedFiles.push(fileName);
            }
        } catch (error) {
            console.error(`Erro ao enviar ${fileName}:`, error);
            failedFiles.push(fileName);
        }
    }

    // Tentativa de reenvio dos arquivos que falharam
    if (failedFiles.length > 0) {
        console.log(`Tentando reenviar ${failedFiles.length} arquivos que falharam...`);

        for (let fileName of failedFiles) {
            try {
                let retryResponse = await fetch(`http://${ip}:3000/ndn/file`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        fileName: fileName,
                        sessao: sessionId,
                        node: node
                    })
                });

                if (retryResponse.status === 200 || retryResponse.status === 201) {
                    console.log(`Arquivo ${fileName} reenviado com sucesso (status ${retryResponse.status}).`);

                    // Envia feedback
                    if(retryResponse.status === 201){
                      // Envia feedback
                      await fetch(`http://${ip}:3000/monitoring/feedback`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            fileName: fileName,
                            sessao: sessionId,
                            node: node
                        })
                      });
                    }
                } else {
                    console.warn(`Falha ao reenviar ${fileName}. Código: ${retryResponse.status}`);
                }
            } catch (error) {
                console.error(`Erro ao reenviar ${fileName}:`, error);
            }
        }
    }

    console.log("Processo de envio concluído.");
}

  async checkAndRenameFiles() {
    try {
        const files = fs.readdirSync(this.mediaPath);
        
        for (const file of files) {
            const filePath = path.join(this.mediaPath, file);
            
            // Verifica se é um arquivo e não uma pasta
            if (!fs.lstatSync(filePath).isFile()) {
                continue;
            }

            // Regex para validar o formato "nome-UID.extensão"
            const regex = /^(.+)-([a-f0-9\-]+)\.\w+$/;

            if (!regex.test(file)) {
                // Gera um UID e renomeia o arquivo
                const fileExt = path.extname(file);
                const fileName = path.basename(file, fileExt);
                const newFileName = `${fileName}-${uuidv4()}${fileExt}`;
                const newFilePath = path.join(this.mediaPath, newFileName);

                fs.renameSync(filePath, newFilePath);
                console.log(`Arquivo renomeado: ${file} -> ${newFileName}`);
            }
        }

        console.log("Verificação de nomenclatura de arquivos concluída.");
    } catch (error) {
        console.error("Erro ao verificar os arquivos:", error);
    }
}
}
