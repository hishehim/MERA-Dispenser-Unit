#include <Servo.h>
#include <Wire.h>
#include "MsTimer2.h"

#define SERVOPIN 3
#define IRSENSOR 17
#define DISPENSER_ADDRESS 0x028

/*
 * Process Codes
*/
#define CODE_DEFAULT 255
#define CODE_READY 250
#define KNOCK_KNOCK 200 // CODE_KNOCK
#define WHOS_THERE 210 // CODE_READY
#define DISPENSE_PENDING 215
#define DISPENSE_IN_PROGRESS 219
#define CODE_COMPLETE 220
#define CODE_ERROR 234
#define CODE_RESET 222
/*
 * defining all possible dispenser states
*/
#define READY_TO_RECEIVE 0
#define ACCEPTED_KNOCK 100
#define ACCEPTED_DISPENSE_COUNT 110
#define BUSY_DISPENSING -999
#define DISPENSE_COMPLETE 500
#define READY_TO_SEND_RESULT 900
Servo myservo;

int fail_count = 0;
int dispenser_state = READY_TO_RECEIVE;
int pills_to_dispense = -1;


void setup() {
  pinMode(IRSENSOR, INPUT);
  digitalWrite(IRSENSOR, HIGH);

  pinMode(13, OUTPUT);

  /*
  * Sets the timeout routing for dispensing
  *  failDispense: see function comments
  *  1500: 1500 milliseconds - timeout for one pill
  */
  MsTimer2::set(1500, timedOut);

  // Set up i2c comm line
  Wire.begin(DISPENSER_ADDRESS);

  // Define Callbacks for i2c
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
  dispenser_state = READY_TO_RECEIVE;
  pills_to_dispense = -1;
  fail_count = 0;
}


/* Description:
 *    callback for when data is sent from the Master. The request codes
 *    must be sent in certain order for the state of the dispenser to advance.
 * Params:
 *    byteCount: number of bytes sent by Master 
*/
void receiveData(int byteCount) {
  while ( Wire.available() ) {
    int readVal = Wire.read();
    if (dispenser_state == READY_TO_RECEIVE
        && readVal == KNOCK_KNOCK) {
      dispenser_state = ACCEPTED_KNOCK;
    } else if (dispenser_state == ACCEPTED_KNOCK
               && readVal < 100) {
      pills_to_dispense = readVal;
      dispenser_state = ACCEPTED_DISPENSE_COUNT;
    } else if (readVal == CODE_RESET) {
      dispenser_state = READY_TO_RECEIVE;
      pills_to_dispense = -1;
    }
  }
}


/* Description:
 *    callback function for when Master request for data.
 *    Sends the
 * Returns:
 *    Returns a protocol code based on the current state of the machine.
*/
void sendData() {
  switch (dispenser_state) {
    case READY_TO_RECEIVE:
      Wire.write(CODE_READY);
      break;
    case ACCEPTED_KNOCK:
      Wire.write(WHOS_THERE);
      break;
    case ACCEPTED_DISPENSE_COUNT:
      Wire.write(DISPENSE_PENDING);
      break;
    case BUSY_DISPENSING:
      Wire.write(DISPENSE_IN_PROGRESS);
      break;
    case DISPENSE_COMPLETE:
      Wire.write(CODE_COMPLETE);
      dispenser_state = READY_TO_SEND_RESULT;
      break;
    case READY_TO_SEND_RESULT:
      Wire.write(pills_to_dispense);
      dispenser_state = READY_TO_RECEIVE;
      pills_to_dispense = -1;
      fail_count = 0;
      break;
    default:
      Wire.write(CODE_DEFAULT);
      break;
  }
}


// The function thata keeps looping.
void loop() {
  if (dispenser_state == ACCEPTED_DISPENSE_COUNT) {
    dispense();
  }
}

/* Description:
 *    Begin the routine to start dispensing and change the state accordingly.
 *    Every individual pill has up to five misses before dispenser stops. The 
 *    state of the machine could be changed during dispensing to force a stop.
 *    Every successful dispense resets the miss count.
*/
void dispense() {
  dispenser_state = BUSY_DISPENSING;
  int gate, prev_count;
  fail_count = 0;
  while ( pills_to_dispense > 0 && fail_count < 5 && (dispenser_state == BUSY_DISPENSING) ) {
    int sensor_timeout;
    sensor_timeout = 3000;
    gate = digitalRead(IRSENSOR);
    while (gate == LOW && sensor_timeout > 0) {
      if (dispenser_state != BUSY_DISPENSING) {
        return;
      }
      delay(100);
      sensor_timeout -= 100;
      gate = digitalRead(IRSENSOR);
    }
    if (sensor_timeout <= 0) {
      pills_to_dispense = CODE_ERROR;
      dispenser_state = DISPENSE_COMPLETE;
      break;
    }
    
    pinMode(13, OUTPUT);
    digitalWrite(13, HIGH);
    gate = HIGH;
    prev_count = fail_count;

    // begain timeout counter
    MsTimer2::start();
    // begain servo control
    myservo.attach(SERVOPIN);
    myservo.write(78);

    while (gate == HIGH && prev_count == fail_count) {
      gate = digitalRead(IRSENSOR);
      if (dispenser_state == READY_TO_RECEIVE) {
        myservo.detach(); // cleanup if state is changed.
        MsTimer2::stop();
        digitalWrite(13, LOW);
        return;
      }
    }

    myservo.detach();
    MsTimer2::stop();
    delay(50);

    digitalWrite(13, LOW);

    if (gate == LOW) {
      pills_to_dispense--;
      fail_count = 0; 
      // reset fail threshold upon a single success
    }
  }
  if (dispenser_state == BUSY_DISPENSING) {
    dispenser_state = DISPENSE_COMPLETE;
  }
}

// the function that is called when timer is up
void timedOut() {
  fail_count++;
}

