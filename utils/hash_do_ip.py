import hashlib

def hash_do_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()

def hash_name(name: str) -> str:
    """
    Gera um hash SHA-256 a partir de uma string (o nome do dispositivo).
    """
    return hashlib.sha256(name.encode("utf-8")).hexdigest()