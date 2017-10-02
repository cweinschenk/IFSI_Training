#include <Wire.h>
#include <Adafruit_ADS1015.h>
#include <SPI.h>
#include <SD.h>
#include <Time.h>

Adafruit_ADS1115 ads;  // Declare an instance of the ADS1115

int16_t rawADCvalue;  // The is where we store the value we receive from the ADS1115
float scalefactor = 0.187500F; // This is the scale factor for the default +/- 6.144 Volt Range we will use
float volts = 0.0; // The result of applying the scale factor to the raw value

const int chipSelect = 4;

void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  
  ads.begin();
}

void loop(void)
{  
  
  
  rawADCvalue = ads.readADC_Differential_0_1(); 
  volts = (rawADCvalue * scalefactor)/1000.0;
  
  String dataString = "";
  
  dataString += rawADCvalue; 
  
  dataString += " , ";
  
  dataString += hour();
  dataString += ":";
  dataString += minute();
  dataString += ":";
  dataString += second();
  dataString += " , ";
  dataString += volts;
  
  Serial.println(rawADCvalue);
  Serial.println(volts);
  Serial.println(volts,6);
  //Serial.println(dataString);
  
  delay(1000);
}
