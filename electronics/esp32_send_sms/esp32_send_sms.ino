// Use the appropriate hardware serial port on ESP32
#define SIM900 Serial2

// Variables for phone number and message
//String numero = "+250721418654";
//String sms = "Embrace the journey of life, earn from challenges, cherish moments. Inh step, find growth and joy. Your path is uniquely yours to ehbb bkgukgkj kuhuk ggkj.";



#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <Arduino_JSON.h>

const char* ssid = "Home_Sweet_Home";
const char* password = "!Rehema!";

//Your IP address or domain name with URL path
const char* serverName = "https://vicky243.pythonanywhere.com/gestion/messages/";

// Update interval time set to 5 seconds
const long interval = 5000;
unsigned long previousMillis = 0;

String outputsState;






void setup() {
  // Start the serial communication with the SIM900 GSM shield
  Serial.begin(115200);
  SIM900.begin(19200, SERIAL_8N1, 16, 17); // Assuming RX is on pin 16, TX is on pin 17
  
  // Give time to your GSM shield log on to the network
  //delay(20000);

  // Send the SMS
  //sendSMS(numero, sms);

  WiFi.begin(ssid, password);
  Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED) { 
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());




}





void loop() {
  unsigned long currentMillis = millis();
  
  if(currentMillis - previousMillis >= interval) {
     // Check WiFi connection status
    if(WiFi.status()== WL_CONNECTED ){ 
      outputsState = httpGETRequest(serverName);
      Serial.println(outputsState);
      JSONVar myObject = JSON.parse(outputsState);
  
      // JSON.typeof(jsonVar) can be used to get the type of the var
      if (JSON.typeof(myObject) == "undefined") {
        Serial.println("Parsing input failed!");
        return;
      }
    
      Serial.print("JSON object = ");
      Serial.println(myObject);
    
      // myObject.keys() can be used to get an array of all the keys in the object
      JSONVar keys = myObject.keys();
    
      for (int i = 0; i < keys.length(); i++) {
        JSONVar value = myObject[keys[i]];
        Serial.print("GPIO: ");
        Serial.print(keys[i]);
        Serial.print(" - SET to: ");
        Serial.println(value);
        //pinMode(atoi(keys[i]), OUTPUT);
        //digitalWrite(atoi(keys[i]), atoi(value));
        sendSMS(keys[i], value);
      }
      // save the last HTTP GET Request
      previousMillis = currentMillis;
    }
    else {
      Serial.println("WiFi Disconnected");
      digitalWrite(1, HIGH); // PIN 1 FOR AUTOMATION MODE
    }
  }
}


String httpGETRequest(const char* serverName) {
  WiFiClientSecure *client = new WiFiClientSecure;
  
  // set secure client without certificate
  client->setInsecure();
  HTTPClient https;
    
  // Your IP address with path or Domain name with URL path 
  https.begin(*client, serverName);
  
  // Send HTTP POST request
  int httpResponseCode = https.GET();
  
  String payload = "{}"; 
  
  if (httpResponseCode>0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    payload = https.getString();
  }
  else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
  }
  // Free resources
  https.end();

  return payload;
}





void sendSMS(String phoneNumber, String message) {
  // AT command to set SIM900 to SMS mode
  SIM900.print("AT+CMGF=1\r");
  delay(100);

  // Use international format code for mobile numbers
  SIM900.print("AT+CMGS=\"");
  SIM900.print(phoneNumber);
  SIM900.println("\"");
  delay(100);
  
  // SMS message content
  SIM900.println(message);
  delay(100);

  // End AT command with a ^Z, ASCII code 26
  SIM900.write(26);
  delay(100);

  // Give the module time to send SMS
  delay(5000);
}
