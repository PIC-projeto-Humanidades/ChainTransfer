import hashlib

def hash_do_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()
