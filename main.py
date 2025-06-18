#!/usr/bin/env python3
import subprocess
import sys
import os

# Diretório do projeto (onde está mkdocs.yml)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def iniciar_mkdocs():
    cmd = [
        sys.executable, "-m", "mkdocs", "serve",
        "--dev-addr=0.0.0.0:3000",
        "--config-file", os.path.join(ROOT_DIR, "mkdocs.yml")
    ]
    subprocess.run(cmd, cwd=ROOT_DIR)

if __name__ == "__main__":
    print("🌐 Servindo documentação em http://localhost:3000 ...")
    iniciar_mkdocs()
