#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

// DHT Sensor
#include "DHT.h"
#define DHTTYPE DHT11
const int DHTPin = 4; //connect with esp8266 pin D2
// Initialize DHT sensor.
DHT dht(DHTPin, DHTTYPE);

//Soil moisture sensor
int SoilmoisturesensorPin = A0;

String valvestatus = "OFF";

#define valvepin 12


void setup() {
  Serial.begin(115200);    //Serial connection
  WiFi.begin("Tham", "12345678");   //WiFi connection
  pinMode(valvepin, OUTPUT);
  digitalWrite(valvepin, LOW);
  Serial.println("Serial Work");
  delay(5000); //delay to wait for find wifi that may can't flash new code

  while (WiFi.status() != WL_CONNECTED) {  //Wait for the WiFI connection completion
    delay(1000);
    Serial.println("Waiting for connection");

  }
}

void loop() {

  if (WiFi.status() == WL_CONNECTED) { //Check WiFi connection status

    //ArduinoJson v6
    //calculate capacity size at//https://arduinojson.org/v6/assistant/
    StaticJsonDocument<200> doc;
    //DHT11
    doc["humidity"] = dht.readHumidity();
    doc["temp C"] = dht.readTemperature();
    doc["temp F"] = dht.readTemperature(true);
    //Soil moisture
    doc["soil moisture"] = map(analogRead(SoilmoisturesensorPin), 300, 1024, 100, 0);
    doc["valvestat"] = valvestatus;
    serializeJson(doc, Serial); //Print to Serial
    Serial.print("\n");
    char json[200];
    serializeJson(doc, json);

    WiFiClient client;
    HTTPClient http;    //Declare object of class HTTPClient


    if (doc["soil moisture"] <= 60) {
      http.begin(client, "http://41d69695.ngrok.io/notification");     //Specify request destination
      http.addHeader("Content-Type", "application/json");  //Specify content-type header
      int httpCode = http.POST(json);   //Send the request
      const String& payload = http.getString();
      Serial.println(httpCode);
      Serial.println("************");
      Serial.println(payload);    //Print request response payload
      http.end();
      while (doc["soil moisture"] <= 60) {
        doc["soil moisture"] = map(analogRead(SoilmoisturesensorPin), 300, 1024, 100, 0);
        delay(1000);
      }
    }
    http.begin(client, "http://41d69695.ngrok.io/sensordatastatus");
    int httpCodeget = http.GET();   //Send the request
    const String& payloadget = http.getString();
    Serial.println(httpCodeget); // this code get 200,504 etc.
    Serial.println(payloadget);    //Print request response payload
    StaticJsonDocument<100> doc2;
    deserializeJson(doc2, payloadget);
    JsonObject obj = doc2.as<JsonObject>();
    Serial.println("obj['sentdata'] = "+obj["sentdata"].as<String>());
    if (obj["sentdata"].as<String>() == "1") {
      http.addHeader("Content-Type", "application/json");  //Specify content-type header
      http.POST(json);
      const String& payloadpost = http.getString();
      Serial.println(payloadpost);
    }
    else if (obj["valve"].as<String>() == "1") {
      digitalWrite(valvepin, HIGH);
      Serial.println("On valve");
      valvestatus = "ON";
    }
    else if (obj["valve"].as<String>() == "0") {
      digitalWrite(valvepin, LOW);
      Serial.println("Off valve");
      valvestatus = "OFF";
    }
    http.end();  //Close connection

  } else {

    Serial.println("Error in WiFi connection");

  }
  delay(10000);
}
