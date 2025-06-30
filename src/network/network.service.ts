import { Injectable } from '@nestjs/common';

@Injectable()
export class NetworkService {
    // Configure manualmente o IP da sua máquina aqui
    private readonly SELF_HOSTED_IP = "192.168.0.15"; // <-- SUBSTITUA pelo seu IP real
    private readonly SELF_NODE_NAME = "node-B"; // <-- Nome do nó local

    getNamedDevices() {
        return [
            { node: "node-A", ip: "192.168.0.33" },
            { 
                node: this.SELF_NODE_NAME, 
                ip: this.SELF_HOSTED_IP,
                selfhosted: true
            }
        ];
    }

    isSelfHosted(ip: string): boolean {
        return ip === this.SELF_HOSTED_IP;
    }

    getSelfNodeName(): string {
        return this.SELF_NODE_NAME;
    }

    getSelfIp(): string {
        return this.SELF_HOSTED_IP;
    }
}