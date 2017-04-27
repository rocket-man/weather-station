#include <ESP8266WiFi.h>
#include <DHT.h>

#define DHTPIN 0
#define RAINPIN A0

const char* ssid = "SSID";
const char* password = "PASSWORD";

int rainVal;
float humidity;
float temperature;
 
WiFiServer server(80);
DHT dht(DHTPIN, DHT22);
 
void setup() {
  Serial.begin(9600);
  dht.begin();
  delay(100);
  
  // Connect to WiFi network
  Serial.print("Connecting to ");
  Serial.println(ssid);
 
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
 
  // Start the server
  server.begin();
  Serial.println("Server started");
 
  // Print the IP address
  Serial.print("Use this URL to connect: ");
  Serial.print("http://");
  Serial.print(WiFi.localIP());
  Serial.println("/");
 
}
 
void loop() {
  // Check if a client has connected
  WiFiClient client = server.available();
  if (!client) {
    return;
  }
 
  // Return the response
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/html");
  client.println("");

  humidity = dht.readHumidity();
  temperature = dht.readTemperature();
  rainVal = analogRead(RAINPIN);
  rainVal = map(rainVal, 1024, 0, 0, 100);
  if(rainVal <= 20){rainVal = 0;} // Sensor doesn't reach totally zero
  delay(2000);

  client.print("{\"humidity\":");
  client.print(humidity);
  client.print(", \"temperature\":");
  client.print(temperature);
  client.print(", \"rain\":");
  client.print(rainVal);
  client.print("}");
}
