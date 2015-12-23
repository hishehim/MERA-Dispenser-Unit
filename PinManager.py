"""
Author: Shankun Lin
Date: Nov, 2015
Description:
	Manages the GPIO pins on the Rapsberry Pi 2 Model B Rev 1
	Contains function to change an RGP LED on or off, or individual LED based on the Pins defined
	Contains function to read button press
	
Functions to use:
setLEDState(state)
getButton()
cleanup() ** Required before program exits. Contains GPIO pin cleanups **
"""

import RPi.GPIO as GPIO

LED_STATE = {
	"READY"         :  [0,1,0],
	"BUSY"          :  [0,0,1],
	"UNAVAILABLE"	:  [1,0,0]
}

PIN_BUTTON = 14
PIN_RED = 15
PIN_GREEN = 18
PIN_BLUE = 23

#Setup routinue for the pins
#RGB should not be access directly
RGB = [None,None,None]

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_RED, GPIO.OUT)
GPIO.setup(PIN_GREEN, GPIO.OUT)
GPIO.setup(PIN_BLUE, GPIO.OUT)

GPIO.output(PIN_RED, False)
GPIO.output(PIN_GREEN, False)
GPIO.output(PIN_BLUE, False)

RGB[0] = GPIO.PWM(PIN_RED, 100)
RGB[1] = GPIO.PWM(PIN_GREEN, 100)
RGB[2] = GPIO.PWM(PIN_BLUE, 100)
	
for i in RGB:
	i.start(0)
#end setup routine


#use this to change the LED states
#The parameter should be a dictionary KEY: "BUSY", "READY", "UNAVAILABLE"
def setLEDState(state):
	global RGB
	if(LED_STATE[state] == None):
		print "state does not exist: ", state
		return False
	if(RGB[0] == None):
		print "setUp() needs to be called!"
		return False
	for i in range(len(LED_STATE[state])):
		RGB[i].ChangeDutyCycle(LED_STATE[state][i])
	return True


#call this function upon exit
#not the end of the world if its not called
#but cleanup is nice, so place this function in all exit points
def cleanup():
	for i in RGB:
		if(i != None):
			i.stop()
	GPIO.cleanup()


#returns false when button is pressed
#use this to get button status
def getButton():
	return GPIO.input(PIN_BUTTON)