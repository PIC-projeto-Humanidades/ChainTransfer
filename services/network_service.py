def routes():
    own_ip = "10.0.0.102"  # IP da própria máquina na rede mesh

    NODES = [
        {"node": "node-A", "ip": "10.0.0.102"},
        {"node": "node-B", "ip": "10.0.0.101"}
    ]

    return [node for node in NODES if node["ip"] != own_ip]
