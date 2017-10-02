/*

  //Use wifi to upload the SD card and initialize SD Card, print to bridge console. Create data file on the SD card with the date and time as the name.

*/

#include <Console.h>
#include <SPI.h>
#include <FileIO.h>
#include <Wire.h>
#include <Adafruit_ADS1015.h>


//declare file path as Char
char filePath [50];

//Declare an instance of the ADS1115 chip
Adafruit_ADS1115 ads;

int16_t rawADCvalue1; //Value from ADS1115
int16_t rawADCvalue2; //value 2 from ADS1115

float scaleFactor = 0.187500F; //Scale factor to convert signal from ADS1115
float HF1volts = 0.0;
float HF2volts = 0.0;

int sensorPin = A0;    // select the input pin for the potentiometer
float TC_Value = 0;  // variable to store the value coming from the sensor

void setup() {
  // Setup Bridge/Console for display.
  Bridge.begin();   // Initialize Bridge
  Console.begin();  // Initialize Console

  // Wait for the Console port to connect
//   while (!Console);

  //Print "Console Port Connected"
  Console.println("Console Port Connected");

  //Set up file system
  Console.println("Set up file system");

  if (FileSystem.begin()) {
    Console.println("File system opened");
  } else {
    Console.println("File system failed to open");
  }

  String fileName;
  String currentDateTime;

  currentDateTime = getTimeStamp();
  currentDateTime.replace("/", "");
  currentDateTime.replace(":", "");

  fileName += "/mnt/sda1/Data_";
  fileName += currentDateTime;
  fileName += ".txt";

  fileName.toCharArray(filePath, 50);

  Console.print("Data file name is ");
  Console.println(fileName);

  Console.println("Starting ADS..");
  ads.begin();
  Console.println("ADS Started");
  
  File dataFile = FileSystem.open(filePath, FILE_APPEND);

  dataFile.println("Time, HF1, HF2, TC1");
  Console.println("Time, HF1, HF2, TC1");
}

void loop() {

  File dataFile = FileSystem.open(filePath, FILE_APPEND);

  rawADCvalue1 = ads.readADC_Differential_0_1();
  rawADCvalue2 = ads.readADC_Differential_2_3();
  HF1volts = (rawADCvalue1 * scaleFactor) / 1000;
  HF2volts = (rawADCvalue2 * scaleFactor) / 1000;
  TC_Value = ((analogRead(sensorPin) * (5.0 / 1023.0)) - 1.25) / 0.005;
  
  String currentTime = getTimeStamp();

  if (dataFile) {
    PrintDataLine(dataFile, currentTime, HF1volts, HF2volts, TC_Value);
    ConsolePrintLine(currentTime, HF1volts, HF2volts, TC_Value);
  } else {
    Console.println("File not opened");
  }

  delay(1000);

}

// This function return a string with the time stamp
String getTimeStamp() {
  String result;
  Process time;
  // date is a command line utility to get the date and the time
  // in different formats depending on the additional parameter
  time.begin("date");
  time.addParameter("+%D_%T");  // parameters: D for the complete date mm/dd/yy
  //             T for the time hh:mm:ss
  time.run();  // run the command

  // read the output of the command
  while (time.available() > 0) {
    char c = time.read();
    if (c != '\n') {
      result += c;
    }
  }

  return result;
}


//Compile Data on a single line
void PrintDataLine(File file, String dateTime, float volts1, float volts2, float TC_Value) {
  file.print(dateTime);
  file.print(", ");
  file.print(volts1, 6);
  file.print(", ");
  file.print(volts2, 6);
  file.print(", ");
  file.print(TC_Value, 6);
  file.println();
}

//Compile Data on a single line Console
void ConsolePrintLine(String dateTime, float volts1, float volts2, float TC_Value) {
  Console.print(dateTime);
  Console.print(", ");
  Console.print(volts1, 6);
  Console.print(", ");
  Console.print(volts2, 6);
  Console.print(", ");
  Console.print(TC_Value, 6);
  Console.println();
}
