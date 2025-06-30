import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import * as ping from 'ping';

@Injectable()
export class NetworkService {
    getNamedDevices() {
        return [
            { node: "node-A", ip: "192.168.0.2" },
            { node: "node-B", ip: "192.168.0.2" },
        ];
    }

    async getConnectedDevices(): Promise<{ ip: string, mac: string, hostname: string }[]> {
        const baseIp = '192.168.0.'; 

        // Faz ping em todos os IPs da faixa
        const pingPromises = Array.from({ length: 254 }, (_, i) => i + 1)
            .map(i => ping.promise.probe(`${baseIp}${i}`, { timeout: 1 }));

        // console.log("Fazendo ping sweep...");
        await Promise.all(pingPromises);

        // Agora que os IPs foram "acordados", rodamos o arp
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
                        return { ip: ipMatch[0], mac: macMatch[0].toLowerCase(), hostname: "Desconhecido" };
                    }
                    return null;
                }).filter(device => device !== null) as { ip: string, mac: string, hostname: string }[];

                // Resolve os hostnames
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
            const timeout = setTimeout(() => resolve("Desconhecido"), 3000);

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
}
