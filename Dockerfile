# Usa Ubuntu 20.04 para compatibilidade com IBR-DTN
FROM ubuntu:20.04

# Define variáveis para evitar prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependências necessárias
RUN apt update && apt install -y python3 python3-pip

# Instala a biblioteca pyd3tn
RUN pip install pyd3tn

# Define o diretório de trabalho
WORKDIR /app

# Copia o script Python para dentro do container
COPY dtn_script.py /app/dtn_script.py

# Dá permissão de execução ao script
RUN chmod +x /app/dtn_script.py

# Comando de entrada para rodar o script Python
CMD python3 /app/dtn_script.py
