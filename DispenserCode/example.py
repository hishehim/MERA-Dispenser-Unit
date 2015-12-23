import RPi.GPIO as GPIO
import PinManager as PMan
import time
import CONSTANTS as CONST
import Dispensing as DP

try:
	PMan.setLEDState("READY")
	time.sleep(0.5)
	while(PMan.getButton()): #While button is not pressed do nothing
		continue
	PMan.setLEDState("BUSY")
	
	allAddresses = DP.scanForAll() #fetch all available container addresses
	if(len(allAddresses) > 0):
		for addr in allAddresses:
			allAddresses[addr] = 5 #sets a dummy value of 5
		
		results = DP.startDispensing(allAddresses)
		
		for addr in results:
				if (results[addr] in CONST.ERROR.keys()):
					print "Device", addr, ": ", CONST.ERROR[results[addr]]
				elif(results[addr] == 0):
					print "Device", addr, ": Dispense succesfull"
				elif(results[addr] == None):
					print "Device", addr, ": Invalid number of dosage"
				else:
					print "Device", addr, ": Failed to dispense ", results[addr], " pills"
				results[addr] = None
		
	else:
		print "No containers found!
finally:
	PMan.cleanup()
