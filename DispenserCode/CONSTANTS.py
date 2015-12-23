"""
Author: Shankun Lin
Date: Nov, 2015
Description:
	This file contains the constant codes being used throughout the 
	dispensing routine as well as the ERROR dictionary that maps error
	codes to string descriptions.

***THE VALUES IN THIS CODE SHOULD NOT BE DIRECTLY MODIFY!***

"""

#Communication protocol code. These code should reflect the code
#in the trinket code, located in Pro_Trinket_Code/dispenser_unit.ino
KNOCK_KNOCK = 200
WHOS_THERE = 210
DISPENSER_COMPLETE = 220
DISPENSER_RESET = 222
DISPENSER_ERROR = 234

#Dispensing Result Codes:
#Code 0 to 50 reserved for number of pills NOT dispensed
#Code 0 = successfully dispensed everything
NO_ONE_HOME = 404404
WRONG_ANSWER = -999999
LOCATION_UNKNOWN = -555555
UNEXPECTED_ERROR_CODE = -666666
CONNECTION_LOST = -1010101

#dictionary to map error code to error message
ERROR = {
	NO_ONE_HOME : "Expected container did not respond to knock request.",
	WRONG_ANSWER : "Container returned the wrong response.",
	LOCATION_UNKNOWN : "There was an unknown error with the container.",
	UNEXPECTED_ERROR_CODE : "The thread communicating with the container threw an unexpected error.",
	CONNECTION_LOST : "Connection lost with container during operation"
}