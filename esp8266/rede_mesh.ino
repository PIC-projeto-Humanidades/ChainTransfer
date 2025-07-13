#include <Arduino.h>
#include <painlessMesh.h>
#include <ESP8266WiFi.h>
#include <user_interface.h>   // para wifi_softap_dhcps_stop()

// ————— Configurações —————
#define MESH_SSID           "MESH_NET"
#define MESH_PASSWORD       "meshPassword"
#define LED_PIN             2       // D4 onboard (ativo-baixo)
#define LED_ON              LOW
#define LED_OFF             HIGH
#define MAX_CLIENTS         4
#define MESH_PORT           5555
#define MESH_CHANNEL        1
#define BLINK_INTERVAL_MS   500
#define RETRY_INTERVAL_MS   10000UL

Scheduler    userScheduler;
painlessMesh mesh;

uint32_t lastBlink = 0;
uint32_t lastRetry = 0;
bool     havePeers = false;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LED_OFF);

  // 1) Rádio em AP+STA
  WiFi.mode(WIFI_AP_STA);

  // 2) Inicializa o mesh (cria o SoftAP automaticamente)
  mesh.setDebugMsgTypes(ERROR | STARTUP | CONNECTION);
  mesh.init(
    MESH_SSID,
    MESH_PASSWORD,
    &userScheduler,
    MESH_PORT,
    WIFI_AP_STA,
    MESH_CHANNEL
  );

  // 3) Desliga o servidor DHCP interno — não haverá atribuição automática de IP
  wifi_softap_dhcps_stop();

  // 4) Limita número de clientes conectados
  WiFi.softAP(MESH_SSID, MESH_PASSWORD, MESH_CHANNEL, false, MAX_CLIENTS);

  // Callbacks de peer
  mesh.onNewConnection([](uint32_t id){
    Serial.printf("Peer conectado: %u (total=%u)\n", id, mesh.getNodeList().size());
  });
  mesh.onDroppedConnection([](uint32_t id){
    Serial.printf("Peer desconectou: %u (restam=%u)\n", id, mesh.getNodeList().size());
  });

  // prepara retry imediato
  lastRetry = millis() - RETRY_INTERVAL_MS;
}

void loop() {
  mesh.update();
  userScheduler.execute();

  size_t peerCount = mesh.getNodeList().size();
  if (peerCount > 0) {
    if (!havePeers) {
      Serial.println("=== Reconectado, LED fixo ===");
      havePeers = true;
    }
    digitalWrite(LED_PIN, LED_ON);
  } else {
    if (havePeers) {
      Serial.println("=== Sem peers, começando piscar ===");
      havePeers = false;
      lastBlink = millis();
      lastRetry = millis() - RETRY_INTERVAL_MS;
    }
    // piscar LED
    if (millis() - lastBlink >= BLINK_INTERVAL_MS) {
      digitalWrite(LED_PIN,
                   digitalRead(LED_PIN) == LED_OFF ? LED_ON : LED_OFF);
      lastBlink = millis();
    }
    // retry de stationManual
    if (millis() - lastRetry >= RETRY_INTERVAL_MS) {
      Serial.println(">>> Tentando stationManual()");
      mesh.stationManual(
        MESH_SSID,
        MESH_PASSWORD,
        MESH_PORT,
        IPAddress(0,0,0,0)
      );
      lastRetry = millis();
    }
  }
}
