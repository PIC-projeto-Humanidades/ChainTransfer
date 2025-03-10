/*
https://docs.nestjs.com/providers#services
*/

import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';

@Injectable()
export class NetworkService {
    getNamedDevices(){
        return [
            {node:"node-A",mac:"02:42:ac:11:00:02"},
            {node:"node-B",mac:"02:42:ac:11:00:03"},
        ]
    }

    async getConnectedDevices(): Promise<{ ip: string, mac: string, hostname: string }[]> {
        return new Promise((resolve, reject) => {
            exec("arp -a", async (error, stdout) => {
                if (error) {
                    reject("Erro ao obter dispositivos conectados");
                    return;
                }
    
                const deviceList = stdout.split("\n").map(line => {
                    const ipMatch = line.match(/([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})/);
                    const macMatch = line.match(/([0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2})/);
    
                    if (ipMatch && macMatch) {
                        return { ip: ipMatch[0], mac: macMatch[0], hostname: "Desconhecido" };
                    }
                    return null;
                }).filter(device => device !== null) as { ip: string, mac: string, hostname: string }[];
    
                // Resolve os hostnames em paralelo
                Promise.all(deviceList.map(async (device) => {
                    device.hostname = await this.getHostname(device.ip);
                    return device;
                })).then(resolve);
            });
        });
    }

    async getHostname(ip: string): Promise<string> {
        return new Promise((resolve) => {
            const command = `nslookup ${ip}`;
            const timeout = setTimeout(() => resolve("Desconhecido"), 3000); // Timeout de 3 segundos

            exec(command, (error, stdout) => {
                clearTimeout(timeout);
                if (error || !stdout) {
                    resolve("Desconhecido");
                    return;
                }
                const match = stdout.split("\n").find(line => line.includes("name ="));
                resolve(match ? match.split("=")[1].trim() : "Desconhecido");
            });
        });
    }

    async getMacAddress(ip: string): Promise<string> {
        return new Promise((resolve) => {
            exec(`arp -n ${ip}`, (error, stdout) => {
                if (error || !stdout) {
                    resolve("Desconhecido");
                    return;
                }
                const match = stdout.match(/([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}/);
                resolve(match ? match[0] : "Desconhecido");
            });
        });
    }
}
