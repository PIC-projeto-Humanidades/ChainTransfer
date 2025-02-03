# 🔗 ChainTransfer
## 📝 Modelagem de processo Inicial - Estruturação
![img](/image/modelagemA.png)


## 📝 Modelagem de processo para iniciar a transferencia
![img](/image/modelagemB.png)
## 📌 Introdução
O ChainTransfer é um sistema descentralizado de transferência de dados projetado para operar em redes Wi-Fi locais sem a necessidade de conexão com a internet. Este projeto tem como objetivo principal permitir que dispositivos compartilhem informações de forma eficiente e segura, mesmo em ambientes isolados onde a conectividade com a internet é limitada ou inexistente. Ele resolve o problema da comunicação offline em cenários distribuídos, possibilitando a troca de dados entre dispositivos que não se conhecem previamente, atuando como uma solução robusta e adaptável para diversas aplicações.

## ⚡ Recursos e Funcionalidades
O ChainTransfer oferece as seguintes funcionalidades principais:

*   **Detecção Automática de Dispositivos:** Os dispositivos na rede local são automaticamente detectados, eliminando a necessidade de configuração manual.
*   **Transferência de Dados Offline:** O sistema opera completamente sem a necessidade de conexão com a internet, tornando-o ideal para ambientes isolados.
*   **Encaminhamento Dinâmico:** Os dados são encaminhados de um dispositivo para outro até chegar ao destino, seguindo um modelo de comunicação em cadeia.
*   **Sistema Descentralizado:** Cada dispositivo atua como um nó independente, enviando, armazenando e retransmitindo informações, sem depender de um servidor central.
*   **Resiliência e Adaptabilidade:** O sistema é projetado para ser resiliente e adaptável a diferentes cenários, permitindo a transmissão de logs, dados fragmentados e sincronização de informações em ambientes distribuídos.

**Exemplo Prático:** Imagine uma rede local onde um dispositivo (A) precisa enviar um arquivo para outro dispositivo (C), mas eles não estão diretamente conectados. Com o ChainTransfer, o dispositivo A envia o arquivo para um dispositivo intermediário (B) que, por sua vez, encaminha o arquivo para C, sem a necessidade de qualquer configuração prévia ou conexão com a internet.

## ✅ Tecnologias Utilizadas
*   ✅ **Python:** A linguagem de programação principal para o desenvolvimento do sistema, escolhida por sua versatilidade e facilidade de uso, facilitando a implementação da lógica de comunicação e manipulação de dados.
*   ✅ **MQTT:** O protocolo de comunicação utilizado para a troca de mensagens entre os dispositivos, ideal para ambientes com recursos limitados, garantindo uma comunicação eficiente e confiável.
*   ✅ **Linux:** O sistema operacional base para a execução do projeto, devido à sua estabilidade e flexibilidade, especialmente em dispositivos como o Raspberry Pi.
*   ✅ **Serviço Descentralizado:** O conceito arquitetônico que permite que o sistema opere de forma autônoma, onde cada dispositivo contribui para a funcionalidade geral, aumentando a resiliência e adaptabilidade.

## 🛠️ Pré-requisitos e Instalação
Antes de iniciar o projeto, certifique-se de que você possui os seguintes pré-requisitos:

*   **Raspberry Pi com Linux:** Um Raspberry Pi rodando um sistema Linux é necessário para executar o projeto.
*   **Python 3.6+:** É necessário ter uma versão do Python igual ou superior a 3.6 instalada.
*   **MQTT Broker:** Um broker MQTT local. Caso não tenha, é possível utilizar o `Mosquitto`.

<!-- **Passos para instalação:**

1.  **Clone o repositório:**
    ```bash
    git clone [URL_DO_REPOSITÓRIO]
    cd ChainTransfer
    ```
2.  **Instale as dependências:**
    ```bash
    pip install paho-mqtt
    ```
3. **Instale o MQTT Broker (Opcional, caso não tenha)**
    ```bash
    sudo apt-get update
    sudo apt-get install mosquitto mosquitto-clients
    ```

4.  **Inicie o broker (Opcional, caso tenha instalado)**

    ```bash
    sudo systemctl enable mosquitto
    sudo systemctl start mosquitto
    ```

5. **Execute o projeto:**
    ```bash
    python main.py
    ```

## ⚙️ Como Usar

1.  **Inicie o projeto** em cada Raspberry Pi que fará parte da rede de comunicação.
2.  Os dispositivos **detectarão automaticamente** outros dispositivos na mesma rede Wi-Fi local.
3.  Para enviar uma mensagem, utilize a função específica no script `main.py` ou implemente um cliente MQTT que se conecte ao mesmo tópico usado para comunicação na rede (exemplo: `chaintransfer/data`).
4.  A mensagem será **encaminhada automaticamente** através da rede, de dispositivo em dispositivo, até chegar ao destino final.
5.  Para receber uma mensagem, o dispositivo deve estar inscrito no tópico adequado (exemplo: `chaintransfer/data`) no broker MQTT.

O sistema não possui interface gráfica, sendo um serviço que funciona em background, trocando dados através de mensagens MQTT. -->



<!-- **Exemplo de Publicação de Mensagem (cliente MQTT):** -->

<!-- ```python
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Conectado com código de resultado: {rc}")

client = mqtt.Client()
client.on_connect = on_connect
client.connect("localhost", 1883, 60) # Ajuste o endereço do broker MQTT caso necessario

client.loop_start()

message = "Hello, ChainTransfer!"
client.publish("chaintransfer/data", message)
print(f"Mensagem publicada: {message}")

client.loop_stop()
client.disconnect()
``` -->

<!-- **Exemplo de Recebimento de Mensagem (cliente MQTT):** -->

<!-- ```python
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Conectado com código de resultado: {rc}")
    client.subscribe("chaintransfer/data")

def on_message(client, userdata, msg):
    print(f"Mensagem recebida: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60) # Ajuste o endereço do broker MQTT caso necessario

client.loop_forever()
``` -->

**Observação:** O Broker MQTT deve estar acessível e funcional. Os scripts devem ser executados em cada dispositivo que fará parte da rede.

## 🗂️ Estrutura de Diretórios
```
ChainTransfer/
├── main.py      # Código principal que executa o sistema
├── mqtt_client.py # Código da lógica de conexão e comunicação com MQTT
├── README.md    # Documentação do projeto
```
*   `main.py`: Arquivo principal que contém a lógica de inicialização do sistema, gerenciamento de dispositivos e encaminhamento de mensagens.
*   `mqtt_client.py`: Arquivo que concentra a implementação da conexão e comunicação com o protocolo MQTT, incluindo funções para publicar e receber mensagens.
*   `README.md`: Este arquivo que você está lendo, contendo a documentação do projeto.

## 🤝 Contribuição
Contribuições são bem-vindas! Siga os seguintes passos para contribuir com o projeto:

1.  Faça um fork do repositório.
2.  Crie uma branch com o nome da sua feature: `git checkout -b feature/sua-nova-feature`.
3.  Faça suas alterações e commit: `git commit -m 'Adiciona sua nova feature'`.
4.  Envie suas alterações: `git push origin feature/sua-nova-feature`.
5.  Abra um pull request para a branch `main` do projeto.

Siga as convenções de código e inclua testes sempre que possível.

## 📝 Licença
Este projeto está licenciado sob a Licença MIT. Para mais detalhes, consulte o arquivo [LICENSE](https://opensource.org/licenses/MIT).
```
