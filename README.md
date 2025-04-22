# 📡 Projeto de Transferência Autônoma de Dados entre Dispositivos

## 🔍 Visão Geral

Este projeto tem como objetivo o desenvolvimento de um **dispositivo autônomo baseado em Linux** capaz de realizar **transferência automática de dados** entre dispositivos semelhantes ao detectarem proximidade em rede local. A proposta é criar uma **rede descentralizada de replicação**, onde os dados fluem automaticamente, sem necessidade de interação humana.

> Exemplo de fluxo:  
> O **Dispositivo A** transfere seus arquivos para o **Dispositivo B**, que, por sua vez, os propaga para o **Dispositivo C**, e assim por diante.

---

## 🧠 Arquitetura Modular

A aplicação é dividida em módulos, cada um responsável por uma parte específica da lógica da aplicação.

### 📁 Módulos

#### 🟨 `main module`
Responsável pela inicialização da aplicação NestJS e composição dos outros módulos.

#### 📜 `logs`
Gerencia os registros das transferências de arquivos entre dispositivos.
- Usa **SQLite** como banco local.
- Componentes:
  - `LogService`: cria e busca logs.
  - `LogModel`: define o schema dos logs.
  - `LogModule`: expõe e integra os recursos do módulo.

#### 🩺 `monitoring`
Monitora o status das transferências e a comunicação entre dispositivos.
- **Endpoints:**
  - `GET /monitoring/status/:sessao`: verifica se um arquivo já foi recebido.
  - `GET /monitoring/devices`: escaneia a rede local.
  - `POST /monitoring/feedback`: confirma o recebimento de arquivos.

#### 🌐 `network`
Faz a varredura de dispositivos na rede local:
- Usa `ping` e `arp -a` para detectar IPs e MACs ativos.
- Mapeia dispositivos conhecidos com base em seus MACs.

#### 💾 `storage`

Gerencia os arquivos locais da aplicação, com separação entre acesso e lógica de negócio.

##### 📦 Estrutura

- **`StorageRepository`**
  - Acessa o sistema de arquivos.
  - Lista arquivos existentes no diretório `media_data`.
  - Lança exceções se o arquivo ou diretório não existirem.

- **`StorageService`**
  - Verifica se um arquivo já foi transferido anteriormente, com base nos logs de sessão.
  - Evita transferências duplicadas.
  - Encapsula a lógica de controle de envio.

##### 📁 Diretório de Armazenamento
- Todos os arquivos são armazenados em `media_data/`.
- Arquivos fora do padrão `nome-UUID.extensão` são renomeados automaticamente na inicialização.

---

## 🔁 `routines` – Serviço de Replicação Automática

A `RoutinesService` executa a lógica principal de **transferência de arquivos entre dispositivos de forma contínua e automatizada**.

### 🔄 Funcionamento

1. **Inicialização**
   - Verifica e renomeia arquivos locais (garantindo nome único).
   - Inicia a rotina cíclica.

2. **Execução a Cada 2 Segundos**
   - Escaneia a rede com `NetworkService`.
   - Detecta dispositivos conhecidos pela tabela MAC.
   - Para cada dispositivo detectado, chama `routine_foundDevice()`.

3. **Transferência**
   - Obtém a lista de arquivos remotos via `GET /ndn/files`.
   - Compara com os arquivos locais.
   - Solicita apenas os arquivos ausentes via `POST /ndn/file`.
   - Salva o conteúdo como buffer no disco local.
   - Caso o status seja `201`, envia `POST /monitoring/feedback`.

4. **Reenvio em Caso de Falha**
   - Arquivos que falharem são colocados numa fila de reenvio imediato.

5. **Persistência de Logs**
   - Todas as ações de transferência são registradas no módulo de logs com data, origem e destino.

---

## 📂 `ndn`

Gerencia os endpoints de transferência de arquivos.

### Endpoints

- `GET /ndn/files`: retorna a lista de arquivos disponíveis para transferência.
- `POST /ndn/file`: recebe o nome do arquivo, a sessão e o node, e envia o conteúdo como buffer.

---

## 🔄 Fluxo de Transferência de Dados

1. Varredura da rede via `ping` + `arp`.
2. Comparação entre arquivos locais e remotos.
3. Transferência apenas dos arquivos ausentes.
4. Envio de feedback após conclusão da transferência.
5. Registro da operação no banco de dados local (`logs`).

---

## ♻️ Modelo de Replicação

> ⚠️ **Não há lógica de prioridade**.

O sistema funciona como uma **malha de replicação total**:

- Todos os dispositivos funcionam de forma **igualitária**.
- Sempre que dois dispositivos se encontram:
  - Ambos verificam e compartilham **arquivos ausentes entre si**.
  - Isso garante **redundância** e continuidade mesmo com dispositivos offline temporariamente.

---

## 🧪 Tecnologias Utilizadas

- **NestJS (Node.js)** – Backend estruturado e modular
- **SQLite** – Banco de dados local leve e persistente
- **node-fetch** – Comunicação HTTP entre dispositivos
- **fs / path / uuid** – Manipulação de arquivos locais
- **ping + arp** – Detecção de dispositivos na rede

---

## ▶️ Como Executar

```bash
# Instalar dependências
npm install

# Iniciar a aplicação
npm run start
```

---

## 🚀 Roadmap 📬 Contribuições

Contribuições são bem-vindas!  
Se você encontrou um bug, tem sugestões ou deseja expandir a funcionalidade, sinta-se à vontade para abrir uma **issue** ou **pull request**.

---