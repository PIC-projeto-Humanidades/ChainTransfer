# 📁 Estrutura do Projeto

```text
ChainTransfer/
├─ 🔧 .eslintrc.js          # Regras de linting para JS/TS
├─ 🎨 .prettierrc           # Configuração de formatação de código
├─ 📦 src/                  # Código-fonte TypeScript
│   ├─ 🏷️ app.module.ts     # Módulo raiz da aplicação
│   ├─ 🆔 identify/         # Módulo de identificação de dispositivo
│   ├─ 📜 logs/             # Módulo de registro de transferencias
│   ├─ 📊 monitoring/       # Módulo de feedback, status e aparelhos da rede
│   ├─ 🌐 ndn/              # Endpoints de listagem/download de arquivos
│   ├─ 🛰️ network/          # Serviços de Varredura e descoberta de dispositivos
│   ├─ 🔄 routines/         # Rotinas de escaneamento e tratativa de processos transferencia automatizada 
│   └─ 💾 storage/          # Acesso e listagem de arquivos locais
├─ 📂 dist/                 # Artefatos compilados (JavaScript)
├─ 🗄️ media_data/           # Arquivos baixados e renomeados
├─ 💻 tsconfig.json         # Configuração principal do TypeScript
├─ 💻 tsconfig.build.json   # Configuração do build TypeScript
└─ ⚙️ nest-cli.json         # Configurações do CLI do NestJS
```

**Detalhes adicionais**  
- **.eslintrc.js** e **.prettierrc** garantem consistência de estilo no time.  
<!-- - **Dockerfile** e **docker-compose.yml** permitem ter um ambiente reproduzível em containers.   -->
- **src/** agrupa todos os módulos do NestJS, cada um com `*.module.ts`, `*.service.ts` e `*.controller.ts`.  
- **dist/** contém o código transpilado após `npm run build`.  
- **media_data/** é onde o sistema salva os arquivos recebidos de outros nós.  
- Arquivos de configuração (`tsconfig*`, `nest-cli.json`) definem como o projeto é compilado e executado.  

