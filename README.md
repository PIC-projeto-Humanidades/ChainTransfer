# 🔗 ChainTransfer

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

---

