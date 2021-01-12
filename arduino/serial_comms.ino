#include <Servo.h>
#include <ArduinoJson.h>
#include <HCSR04.h>


Servo baseServo;
Servo sideServo;
Servo triggerServo;


// echo pin is blue
int echoPin = 13;
int triggerPin = 12;
UltraSonicDistanceSensor ultrasonic(triggerPin, echoPin);


void setup() {
  // put your setup code here, to run once:
  short basePin = 9;
  short sidePin = 10; 
  short triggerPin = 6;
  short triggerPinBackup = 11;


  // begin receiving data 9600 bits at a time
  Serial.begin(9600);


  // tell Arduino to let pin number x be output
  //pinMode(basePin, OUTPUT);

  // attach servos to pins
  baseServo.attach(basePin);
  sideServo.attach(sidePin);
  triggerServo.attach(triggerPin);

  
  // set it to midpoint (90 deg)
  baseServo.write(90);
  sideServo.write(90);

  // wind up the sucker
  triggerServo.write(145);
  


  // wait .250 seconds
  delay(250);
  

}

void loop() {

  // if there is data available, read it in
  // and do something with it
  if (Serial.available()) {

    // stop reading data until the null byte
    String data = Serial.readStringUntil('\0');
    // Serial.println(data);

    // should only need 512 bytes of data
    StaticJsonDocument<512> doc;



    // deserialize the json into the document
    DeserializationError err = deserializeJson(doc, data);

    // if there was an error, return from the function to not
    // get a seg fault
    if (err) {
      Serial.print("Error in deserialization: ");
      Serial.println(err.c_str());
      return;
    }

    // get the servo that we want to turn
    const char* servo = doc["servo"];

    // get how many degrees to turn it at
    const int degree = doc["degrees"];

    // whether or not to subtract the degrees
    const bool subtract = doc["subtract"];

    // whether or not to fire the blaster
    const bool fire = doc["fire"];


    // if the servo we want to turn is the base servo, then it will
    // turn this servo
    if (strncmp(servo, "base", 5) == 0) {
      // turn the base servo here
       moveServoByDegrees(&baseServo, degree, subtract);

    // turn the side servo 
    } else if (strncmp(servo, "side", 5) == 0) {
       moveServoByDegrees(&sideServo, degree, subtract);
    }

    // if we want to fire then fire the blasta
    if (fire) fireBlaster();
    

  }  

  //triggerServo.write(0);
  //delay(2000);
  //triggerServo.write(0);
  //delay(2000);
  

}

/**
 * Moves the servo by a set amount of degrees, given a pointer to a servo.
 * The function calculates the current angle at which it is at, and rotates it
 * by however many degrees. It takes the subtract boolean to determine whether to 
 * subtract the amount of degrees or add them
 */
void moveServoByDegrees(Servo *servo, uint16_t degree, bool subtract) {

  // get the current degrees the servo is turned
  int currDegrees = servo->read();

 // if the current degrees is greater than 180, or less than 0, then just go back
 // to original starting position
  if (currDegrees >= 180 || currDegrees <= 0) {

      servo->write(90);
      return;
    
  }
  if (!subtract)
  servo->write(currDegrees + degree);
  else 
  servo->write(currDegrees - degree);
  //delay(25);
  
}

/**
 * Clench the trigger to the blaster
 */
void fireBlaster() {
  for (int i = 145; i > 0; i--) {
      triggerServo.write(i);
      delay(2);
  }

  for (int i = 0; i < 145; i++) {
      triggerServo.write(i);
      delay(2);
  }





}
