import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import * as ping from 'ping';

@Injectable()
export class NetworkService {
  /**
   * Lista de dispositivos esperados na rede mesh com seus respectivos MACs e nomes simbólicos.
   */
  getNamedDevices() {
    return [
      { node: 'node-A', mac: 'a4:63:a1:5a:9d:95' }, // máquina A
      { node: 'node-B', mac: '60:03:08:90:8b:1c' }, // máquina B
    ];
  }

  /**
   * Retorna todos os dispositivos ativos na rede mesh baseados no comando arp -an,
   * após realizar ping sweep em 10.0.0.100-199.
   */
  async getConnectedDevices(): Promise<{ ip: string; mac: string }[]> {
    const baseIp = '10.0.0.';
    const start = 100;
    const end = 199;

    // Dispara pings para "acordar" dispositivos na rede mesh
    const pingSweep = Array.from({ length: end - start + 1 }, (_, i) => i + start).map((i) =>
      ping.promise.probe(`${baseIp}${i}`, { timeout: 1 })
    );
    await Promise.all(pingSweep);

    return new Promise((resolve, reject) => {
      exec('arp -an', (error, stdout) => {
        if (error) {
          return reject('Erro ao executar ARP');
        }

        const devices = stdout
          .split('\n')
          .map((line) => {
            const ipMatch = line.match(/\(([^)]+)\)/);
            const macMatch = line.match(/([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}/);

            if (ipMatch && macMatch) {
              return {
                ip: ipMatch[1],
                mac: macMatch[0].toLowerCase(),
              };
            }
            return null;
          })
          .filter(Boolean) as { ip: string; mac: string }[];

        resolve(devices);
      });
    });
  }
}
