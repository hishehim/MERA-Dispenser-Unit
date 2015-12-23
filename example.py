import RPi.GPIO as GPIO
import PinManager as PMan
import time
import Dispensing as DispRoute
import CONSTANTS as CONST


try:
	while(True):
		time.sleep(1)
		print "READY...."
		PMan.setLEDState("READY")
		while(PMan.getButton()): #While button is not pressed do nothing
			continue
		print "BUSY..."
		PMan.setLEDState("BUSY")

		addresses = DispRoute.scanForAll()
		#addresses = {8: 3, 40 : 3}

		if(len(addresses) > 0):
			for addr in addresses:
				addresses[addr] = 3

			devices = DispRoute.startDispensing(addresses)

			for addr in devices:
				if (devices[addr] in CONST.ERROR.keys()):
					print "Device", addr, ": ", CONST.ERROR[devices[addr]]
				elif(devices[addr] == 0):
					print "Device", addr, ": Dispense succesfull"
				elif(devices[addr] == None):
					print "Device", addr, ": Invalid number of dosage"
				else:
					print "Device", addr, ": Failed to dispense ", devices[addr], " pills"
				devices[addr] = None
		else:
			print "No devices found!\n"
except:
	PMan.cleanup()
