# Usa uma imagem oficial do Node.js como base
FROM node:18

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para o container
COPY package.json package-lock.json ./
RUN npm install

# Copia o restante do código
COPY . .

# Compila a aplicação NestJS
RUN npm run build

# Expõe a porta que o NestJS usará
EXPOSE 3000

# Comando para iniciar o servidor
CMD ["npm", "run", "start"]
# Usa uma imagem oficial do Node.js como base
FROM node:18

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para o container
COPY package.json package-lock.json ./
RUN npm install

# Copia o restante do código
COPY . .

# Compila a aplicação NestJS
RUN npm run build

# Expõe a porta que o NestJS usará
EXPOSE 3000

# Comando para iniciar o servidor
CMD ["npm", "run", "start"]
