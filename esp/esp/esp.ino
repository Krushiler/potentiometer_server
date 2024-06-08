#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <EEPROM.h>
#include <PubSubClient.h>
#include <Stepper.h>
#include "ArduinoJson.h"


#define DEVICE_NAME "[MPD] DualC Phone Amp"
#define DEVICE_PASSWORD "mpdpassword"
#define CONNECTION_ATTEMPTS 30
#define DEVICE_TYPE "dual-c-phone-amp"
#define MQTT_DEFAULT_PORT 1883 
#define MQTT_ADDR "broker.emqx.io"
#define STEPS 200
#define POT_PIN A0

Stepper stepper(STEPS, D1, D2, D5, D6);
const int potsCount = 2;

bool isRotating = true;
const int dt = 5;
const int dt_max = 100;

int target_1 = 0;
int target_2 = 0;


WiFiClient espClient;
PubSubClient mqttClient(espClient);

ESP8266WebServer server(80);
bool mayConnectBroker = true;




void rotatePot(int targetValue, int potValue) {
  if (potValue < targetValue - dt_max) {
    stepper.step(-100);
  } else if (potValue < targetValue - dt) {
    stepper.step(-20);
  } else if (potValue > targetValue + dt_max) {
    stepper.step(100);
  } else if (potValue > targetValue + dt) {
    stepper.step(20);
  } else {
    isRotating = false;
    stepper.step(0);
  }
}




String readFromEeprom(int start, int end) {
  String data = "";
  for (int i = start; i < end; ++i) {
    data += char(EEPROM.read(i));
  }
  return data;
}

void writeToEprom(String row, int start, int end) {
  for (int i = start; i < end; ++i) {
    EEPROM.write(i, i - start < row.length() ? row[i - start] : 0);
  }
  EEPROM.commit(); 
}

bool connectWifiNetwork(String ssid, String password) {
  WiFi.begin(ssid.c_str(), password.c_str());
  Serial.println("");
  Serial.print("[MPD] Connecting to network: ");
  Serial.println(ssid);
  int counter = 0;
  while (WiFi.status() != WL_CONNECTED && counter < CONNECTION_ATTEMPTS) {
    delay(500);
    Serial.print(".");
    counter++;
  }
  return WiFi.status() == WL_CONNECTED;
}

bool connectPreviousNetwork() {
  String ssid = readFromEeprom(0, 32);
  String password = readFromEeprom(32, 96);
  return connectWifiNetwork(ssid, password);
}

void changePreset(char* topic, byte* payload, unsigned int length) {
  Serial.println("[MPD] IT WORKED!");
  DynamicJsonDocument doc(2048);

  deserializeJson(doc, payload);

  target_1 = doc[0]["value"];
  isRotating = true;
  Serial.println(target_1);
}

void startAccessPoint() {
  Serial.println("Starting AP mode");
  WiFi.softAP(DEVICE_NAME, DEVICE_PASSWORD);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);
}

void handleNetworkChange() {
  if (server.method() == HTTP_POST) {
    Serial.println("[MPD] Changing wifi network");
    String ssid = server.arg("ssid");
    String password = server.arg("password");
    writeToEprom(ssid, 0, 32);
    writeToEprom(password, 32, 96);
    bool connectionStatus = connectWifiNetwork(ssid, password);
    if (connectionStatus) {
      mayConnectBroker = true; 
      Serial.print("\n[MPD] Successfuly connected to ");
      Serial.println(ssid);
      Serial.println("[MPD] Connecting to MQTT Broker");
      mqttClient.setServer(MQTT_ADDR, MQTT_DEFAULT_PORT);
      mqttClient.setCallback(changePreset);
      connectToMQTTBroker();
    } else {
      Serial.println("[MPD] Wi-Fi connection failed");
    }
  }
}

void handleInfo() {
  String macAddress = WiFi.macAddress();
  String jsonResponse = "{\"mac\":\"" + macAddress + "\", \"device\":\"" + String(DEVICE_TYPE) + "\"}";
  server.send(200, "application/json", jsonResponse);
}

void connectToMQTTBroker() {
  mqttClient.setCallback(changePreset);
  while (!mqttClient.connected()) {
    String client_id = "mpd-id-" + String(WiFi.macAddress());
    String mac = String(WiFi.macAddress());
    mac.replace(":", "");
    String topic = mac;
    if (mqttClient.connect(client_id.c_str())) {
      mayConnectBroker = true;
      Serial.println("[MPD] Connected to MQTT broker");
      mqttClient.subscribe(topic.c_str());
      Serial.print("[MPD] Listening to topic: ");
      Serial.println(topic);
      WiFi.softAPdisconnect(true);
      Serial.println("[MPD] AP mode disabled after connecting to MQTT broker");
    } else {
      Serial.print("[MPD] Failed to connect to MQTT broker, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  
  pinMode(D0, OUTPUT);
  pinMode(D1, OUTPUT);

  Serial.begin(115200);
  EEPROM.begin(512); 
  bool status = connectPreviousNetwork();
  if (!status) {
    Serial.println("[MPD] Previous Wi-Fi network is not specified");
    startAccessPoint();
  } else {
    Serial.println("\n[MPD] Successfuly connected to Wi-Fi newtork");
    Serial.println("[MPD] Connecting to MQTT Broker...");
    mqttClient.setServer(MQTT_ADDR, MQTT_DEFAULT_PORT);
    mqttClient.setCallback(changePreset);
    connectToMQTTBroker();
  }
  server.on("/info", HTTP_GET, handleInfo);
  server.on("/changenet", HTTP_POST, handleNetworkChange);
  server.begin();
  stepper.setSpeed(100);
}

void loop() {
  
  server.handleClient();
  if (mqttClient.connected() && mayConnectBroker) {
    mqttClient.loop();
  }
  
  int potValue = analogRead(POT_PIN);

  Serial.print("Current value: ");
  Serial.println(potValue);

  if (isRotating) {
    rotatePot(target_1, potValue);
  }
  delay(100);
}