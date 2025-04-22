# 🔗 ChainTransfer
## 📝 Modelagem de processo Inicial - Estruturação
![img](/image/modelagemA.png)


## 📝 Modelagem de processo para iniciar a transferencia
![img](/image/modelagemB.png)

# 📌  **Backlog do Projeto**

![img](/image/walpaper.png)

## **Visão Geral**
O projeto consiste no desenvolvimento de um dispositivo autônomo baseado em Linux para realizar a transferência automática de dados entre dispositivos similares ao se aproximarem. A ideia é criar uma rede descentralizada de transmissão contínua, sem a necessidade de interação humana para iniciar o processo. Dessa forma, o dispositivo A transferirá os dados para o dispositivo B, que, por sua vez, continuará o fluxo para o dispositivo C, e assim por diante.


---

A aplicacao foi dividida em modulos para separar a divisao de responsabilidades, seguindo o em 
logs
indentify
monitoring
network
routines
storage

main module 

logs:
contem logs que seram propagados entre dispositivos, neste contexto existe a divisao service,module e models que detem o esquema de logs propagados e persistido via DB SQLite

monitoring:
monitoring mantem os endpoints status,device e feedback
status mantem  uma especie de ping que pergunta ao servidor se o arquivo ja foi enviado ou nao,
devices mantem o ping e scaneamneto da rede para verificar os devices encontrados,
feedback ao acessasr esse endpoint e possivel comunicar o servidor que o arquivo foi recebido com sucesso

ndn:
ndn/files mantem endpoint para donwload de arquivo ou arquivos nomeados

routines:
mnatem um esquema de rotinas opara executar de maneira automatizada e organizada o envio/recebimento dos arquivos entre dispositivos mantendo a propagacao de feedback para envio de arquivos 

## **Fluxo de Transferência de Dados**
A transmissão dos dados seguirá um esquema de **prioridade**, garantindo que os dispositivos com maior volume de dados iniciem a transferência para aqueles com menor volume. Além disso, todas as transferências serão registradas em logs para análise e monitoramento.

### **Cenário de Fluxo**
![img](/image/fluxo.png)
1. **Dispositivo A** possui o maior volume de dados.
2. **Dispositivo B** possui um volume menor.
3. O dispositivo **A** iniciará a transferência para o **B** e registrará esse evento nos logs.
4. Após a finalização, a transferência **não poderá ser revertida**, ou seja, o B não poderá enviar os mesmos dados de volta para A.
5. Esse processo se repetirá com os demais dispositivos disponíveis na rede.

---

## **Desenvolvimento da Aplicação**
A aplicação será desenvolvida em **Python**, utilizando o framework **Flask** para fornecer serviços via APIs REST. 

### **Principais Funcionalidades**
- **Envio de dados** para um IP específico.
- **Recebimento de dados** de um IP determinado.
- **Verificação de prioridade** para decidir qual dispositivo deve iniciar a transferência.
- **Varredura da rede** para detectar dispositivos disponíveis e independentes.
- **Rotina de decisão** para organizar a transferência com base nas prioridades.
- **Registro de logs** em um banco de dados **SQLite**.
- **Consulta de logs** para auditoria e monitoramento.
- **Verificação de status** dos serviços em execução.
- **Módulo de sinalização por LED** para indicar o status da transferência, utilizando uma lâmpada Wi-Fi/Bluetooth:
  - **Verde**: Envio concluído com sucesso.
  - **Amarelo**: Transferência em andamento.
  - **Vermelho**: Falha no envio.
  - **Roxo**: Procurando dispositivos disponíveis.
  - **Laranja**: Tentando restabelecer comunicação.

---

## **Especificações do Dispositivo**
O dispositivo utilizado será um **Raspberry Pi**, podendo ser dos modelos **3 ou 4**, com os seguintes requisitos mínimos:
- **Memória RAM**: 4 GB
- **Conectividade**: Wi-Fi e Bluetooth
- **Armazenamento Interno**: Cartão microSD de pelo menos 64 GB
- **Sistema Operacional**: Distribuição Linux Server (para facilitar comunicação via SSH)

### **Infraestrutura e Gerenciamento**
- A aplicação será encapsulada em um **container Docker**, garantindo maior estabilidade, políticas de start/restart automático em caso de falhas e facilidade de replicação para outros dispositivos.
- O dispositivo deverá ter **proteção contra intempéries**, garantindo seu funcionamento em diferentes condições ambientais.
- Ele será denominado um **dispositivo independente**, garantindo seu funcionamento sem a necessidade de infraestrutura externa.

---

