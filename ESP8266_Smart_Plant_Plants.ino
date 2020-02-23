#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

// DHT Sensor
#include "DHT.h"
#define DHTTYPE DHT11
const int DHTPin = 4; //connect with esp8266 pin D2
DHT dht(DHTPin, DHTTYPE); // Initialize DHT sensor.

//Soil moisture sensor
int SoilmoisturesensorPin = A0; //connect with esp8266 pin A0

#define valvepin 5 //connect with esp8266 pin D1

//++Setting++
String valvevalue = "OFF", valvetext, valvestatus = "0", automode = "OFF", autotext, autostatus = "0";
int delay_for_one_loop = 15000; //delay 15 sec for 1 loop (auto)
const int soilmoisture_at_least = 60; //soilmoisture should less than this value (depends on each plants)
//Auto
const int soilmoisture_max = 80; //when it get this value valve will stop



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
    doc["soil moisture"] = map(analogRead(SoilmoisturesensorPin), 350, 1024, 100, 0);
    //valve
    doc["valvestat"] = valvevalue;
    //automode
    doc["auto"] = automode;
    serializeJson(doc, Serial); //Print to Serial
    Serial.print("\n");
    char json[200];
    serializeJson(doc, json);

    WiFiClient client;
    HTTPClient http;    //Declare object of class HTTPClient

    http.begin(client, "http://7acf3d5b.ngrok.io/sensordatastatus");
    int httpCodeget = http.GET();   //Send the request
    const String& payloadget = http.getString();
    Serial.println(httpCodeget); // this code get 200,504 etc.
    Serial.println(payloadget);    //Print request response payload
    StaticJsonDocument<100> doc2;
    deserializeJson(doc2, payloadget);
    JsonObject obj = doc2.as<JsonObject>();
    Serial.println("obj['sentdata'] = " + obj["sentdata"].as<String>());
    if (autostatus != obj["auto"].as<String>()) {
      if (obj["auto"].as<String>() == "1") {
        automode = "ON";
      }
      else if (obj["auto"].as<String>() == "0") {
        automode = "OFF";
      }
      autostatus = obj["auto"].as<String>();
      http.begin(client, "http://7acf3d5b.ngrok.io/automodereply");     //Specify request destination
      http.addHeader("Content-Type", "application/json");  //Specify content-type header
      autotext = "Auto mode is ";
      autotext += automode;
      StaticJsonDocument<50> automodedoc;
      automodedoc["automode"] = autotext;
      char automodejson[50];
      serializeJson(automodedoc, automodejson);
      http.POST(automodejson);   //Send the request
      http.end();
    }

    if (obj["sentdata"].as<String>() == "1") {
      http.begin(client, "http://7acf3d5b.ngrok.io/sensordatastatus");
      http.addHeader("Content-Type", "application/json");  //Specify content-type header
      http.POST(json);
      const String& payloadpost = http.getString();
      Serial.println(payloadpost);
      http.end();
    }

    if (automode == "OFF") {
      if (doc["soil moisture"] < soilmoisture_at_least) { //notification
        http.begin(client, "http://7acf3d5b.ngrok.io/notification");     //Specify request destination
        http.addHeader("Content-Type", "application/json");  //Specify content-type header
        int httpCode = http.POST(json);   //Send the request
        const String& payload = http.getString();
        Serial.println(httpCode);
        Serial.println("************");
        Serial.println(payload);    //Print request response payload
        http.end();
      }
      if (valvestatus != obj["valve"].as<String>()) {
        if (obj["valve"].as<String>() == "1") {
          delay_for_one_loop = 10000; //for not too much delay to control
          digitalWrite(valvepin, HIGH);
          Serial.println("On valve");
          valvevalue = "ON";
        }
        else if (obj["valve"].as<String>() == "0") {
          delay_for_one_loop = 10000;
          digitalWrite(valvepin, LOW);
          Serial.println("Off valve");
          valvevalue = "OFF";
        }
        valvestatus = obj["valve"].as<String>();
        http.begin(client, "http://7acf3d5b.ngrok.io/valvereply");     //Specify request destination
        http.addHeader("Content-Type", "application/json");  //Specify content-type header
        valvetext = "Valve is ";
        valvetext += valvevalue;
        StaticJsonDocument<50> valvedoc;
        valvedoc["valve"] = valvetext;
        char valvejson[50];
        serializeJson(valvedoc, valvejson);
        http.POST(valvejson);   //Send the request
        http.end();
      }
    }
    else if (automode == "ON") {
      if (doc["soil moisture"] < soilmoisture_at_least) {
        digitalWrite(valvepin, HIGH);
        Serial.println("On valve");
        valvevalue = "ON";
        valvetext = "Auto mode : Valve is ";
        valvetext += valvevalue;
        StaticJsonDocument<100> valvedoc;
        valvedoc["valve"] = valvetext;
        char valvejson[100];
        serializeJson(valvedoc, valvejson);
        http.begin(client, "http://7acf3d5b.ngrok.io/valvereply");
        http.addHeader("Content-Type", "application/json");  //Specify content-type header
        http.POST(valvejson);   //Send the request
        http.end();
        while (doc["soil moisture"] < soilmoisture_max) {
          doc["soil moisture"] = map(analogRead(SoilmoisturesensorPin), 350, 1024, 100, 0);
          delay(500);
        }
        digitalWrite(valvepin, LOW);
        Serial.println("Off valve");
        valvevalue = "OFF";
        valvetext = "Auto mode : Valve is ";
        valvetext += valvevalue;
        valvedoc["valve"] = valvetext;
        serializeJson(valvedoc, valvejson);
        http.begin(client, "http://7acf3d5b.ngrok.io/valvereply");
        http.addHeader("Content-Type", "application/json");  //Specify content-type header
        http.POST(valvejson);   //Send the request
        http.end();  //Close connection
      }
    }
    else {
      Serial.println("*******ERROR*********");
    }
  }
  else {
    Serial.println("Error in WiFi connection");
  }
  delay(delay_for_one_loop);
}

//https://github.com/esp8266/Arduino/blob/master/libraries/ESP8266HTTPClient/examples/BasicHttpClient/BasicHttpClient.ino
//https://github.com/esp8266/Arduino/blob/master/libraries/ESP8266HTTPClient/examples/PostHttpClient/PostHttpClient.ino
//https://arduinojson.org/v6/example/
//https://medium.com/educate/esp8266-posting-json-data-to-a-flask-server-on-the-cloud-2a354580094a
