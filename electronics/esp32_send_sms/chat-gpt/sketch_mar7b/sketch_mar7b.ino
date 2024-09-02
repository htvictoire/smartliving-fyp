


#define SIM900 Serial2


#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <Arduino_JSON.h>

const char* ssid = "Home_Sweet_Home";
const char* password = "!Rehema!";

//Your IP address or domain name with URL path
const char* Link_one = "https://vicky243.pythonanywhere.com/gestion/messages/"; // verifier les messages

const char* Link_two = "https://vicky243.pythonanywhere.com/gestion/update_messages/";   // mettre à jour

// Update interval time set to 5 seconds
const long interval = 5000;
unsigned long previousMillis = 0;

String outputsState;




void setup() {
  // Start the serial communication with the SIM900 GSM shield
  Serial.begin(115200);
  SIM900.begin(19200, SERIAL_8N1, 16, 17); //  RX is on pin 16, TX is on pin 17
  
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
  
  if (currentMillis - previousMillis >= interval) {
    // Check WiFi connection status
    if (WiFi.status() == WL_CONNECTED) { 
      outputsState = httpGETRequest(Link_one);
      Serial.println(outputsState);
      JSONVar myArray = JSON.parse(outputsState);
  
      // JSON.typeof(jsonVar) can be used to get the type of the var
      if (JSON.typeof(myArray) == "undefined") {
        Serial.println("Parsing input failed!");
        return;
      }
    
      Serial.print("JSON array size = ");
      Serial.println(myArray.length());
    
      for (int i = 0; i < myArray.length(); i++) {
        JSONVar output = myArray[i];
        Serial.print("Recipient: ");
        Serial.print(output["recipient"]);
        Serial.print(" - Message: ");
        Serial.print(output["message"]);
        Serial.print(" - id: ");
        Serial.println(output["id"]);
        
        // pinMode(atoi(output["gpio"]), OUTPUT);
        // digitalWrite(atoi(output["gpio"]), atoi(output["state"]));

        sendSMS(output["recipient"],output["message"], output["id"]);
        
        
      }
      // Save the last HTTP GET Request
      previousMillis = currentMillis;
    }
    else {
      Serial.println("WiFi Disconnected");
      digitalWrite(1, HIGH); // PIN 1 FOR AUTOMATION MODE
    }
  }
}




String httpGETRequest(const char* Link_one) {
  WiFiClientSecure *client = new WiFiClientSecure;
  
  // set secure client without certificate
  client->setInsecure();
  HTTPClient https;
    
  // Your IP address with path or Domain name with URL path 
  https.begin(*client, Link_one);
  
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




void UpdateMessageStatus(String MessageId) {
  //Check WiFi connection status
  if(WiFi.status()== WL_CONNECTED){
    WiFiClientSecure *client = new WiFiClientSecure;
    client->setInsecure(); //don't use SSL certificate
    HTTPClient https;
    
    // Your Domain name with URL path or IP address with path
    https.begin(*client, Link_two);
    
    // Specify content-type header
    https.addHeader("Content-Type", "application/x-www-form-urlencoded");
    
    // Prepare your HTTP POST request data
    String httpRequestData = "&message=" + MessageId;
    Serial.print("httpRequestData: ");
    Serial.println(httpRequestData);
    
 
    // Send HTTP POST request
    int httpResponseCode = https.POST(httpRequestData);
     
 
    if (httpResponseCode>0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
    }
    else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    // Free resources
    https.end();
  }
  else {
    Serial.println("WiFi Disconnected");
  } 
}



void sendSMS(String phoneNumber, String message, String messageId) {
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

  if (SIM900.find("OK")) {
    // Message sent successfully, update status
    UpdateMessageStatus(messageId);
  } else {
    Serial.println("NO MESSAGE NOT SENT OR SIM MODULE NOT FOUND");
  }


}

void Receiver(message):
  if message:
    SIM900.DigitalWrite(message);
    return redirect(message_sent, 'done')




