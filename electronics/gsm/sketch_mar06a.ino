#include <SoftwareSerial.h>

// Configure software serial port
SoftwareSerial SIM900(12, 13 ); 

// Variables for phone number and message
String phoneNumber = "+250721418654";
String message = "deuxieme of dynamic memory, leaving 1864 bytes for local variables. Maximum is 2048 bytes.";

void setup() {
  // Arduino communicates with SIM900 GSM shield at a baud rate of 19200
  SIM900.begin(19200);
  
  // Give time to your GSM shield log on to the network
  delay(20000);   
  
  // Send the SMS
  sendSMS();
}

void loop() { 
  // Your main loop code here
}

void sendSMS() {
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
  SIM900.println((char)26); 
  delay(100);
  SIM900.println();
  
  // Give the module time to send SMS
  delay(5000); 
}
