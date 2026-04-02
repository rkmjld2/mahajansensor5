#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// -------- WIFI --------
const char* ssid = "Airtel_56";
const char* password = "Raviuma5658";

// -------- SERVER (USE HTTPS ONLY) --------
String serverName = "https://mahajansensor5.onrender.com/api/data";

// -------- API KEY --------
String apiKey = "12b5112c62284ea0b3da0039f298ec7a85ac9a1791044052b6df970640afb1c5";

// -------- SENSOR PIN --------
int sensorPin = A0;

WiFiClientSecure client;

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.print("Connecting");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected ✅");
  Serial.println(WiFi.localIP());

  // 🔥 VERY IMPORTANT FOR HTTPS
  client.setInsecure();
}

void loop() {

  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;

    float s1 = random(200, 300);
    float s2 = random(500, 700);
    float s3 = random(300, 600);

    String url = serverName + "?s1=" + String(s1, 2) +
                 "&s2=" + String(s2, 2) +
                 "&s3=" + String(s3, 2) +
                 "&key=" + apiKey;

    Serial.println("Sending: " + url);

    http.begin(client, url);

    http.setTimeout(15000);   // 🔥 VERY IMPORTANT

    int httpCode = http.GET();

    if (httpCode > 0) {
      Serial.println("HTTP Code: " + String(httpCode));
      Serial.println("Response: " + http.getString());
    } else {
      Serial.println("❌ Error: " + http.errorToString(httpCode));
    }

    http.end();

  }

  delay(10000);  // 🔥 reduce load on server
}