"""
Author: Shankun Lin
Date: Nov, 2015
Description:
	Contains functions used to communication with slave i2c container units
	Each container will be managed by individual threads; thus all med
		dispensing routine will be cocurrent.

FUNCTIONS TO USE:
scanFor(addr)
startDispensing(devices_dictionary)
scanForAll()
"""

import smbus
import time
import threading
import sys
import CONSTANTS as CONST

bus = smbus.SMBus(1)


#containerDispenseThread: The function in which a dispensing thread will be called upon
#DO NOT call this function directly.
#  param:
#	 devices: the dictionary where the different results will be written to
#    addr: the address of the container (A.K.A the trinket i2c address)
#    dosage: the number of pills to be dispensed by the container
#  Return: void
def containerDispenseThread(devices, addr, dosage):
	#global devices
	#some simple book keeping variables
	sec = 0
	readVal = 0

	print "Dispenser ", addr, "has begun."
	
	if(dosage < 0):
		return
	
	try:
		writeNumber(addr, CONST.DISPENSER_RESET)
		time.sleep(0.1)
		writeNumber(addr, CONST.KNOCK_KNOCK) #Knocking
		time.sleep(0.5) #give time to respond
		readVal = readNumber(addr)
	except IOError:
		print "Failed to reach containerDispenseThread addr=", addr
		devices[addr] = CONST.NO_ONE_HOME
		return
	except:
		print"Unexpected exception caught: ", sys.exc_info()[0]
		devices[addr]  = CONST.UNEXPECTED_ERROR_CODE
		return
	
	# initial communication successful at this point
	if (readVal != CONST.WHOS_THERE): #ensure containerDispenseThread returned the correct response code
		print "Incorrect code returned from address ", addr
		devices[addr] = CONST.WRONG_ANSWER
		return

	try:
		writeNumber(addr, dosage)
		time.sleep(0.25)
		readVal = readNumber(addr)

		while (readVal != CONST.DISPENSER_COMPLETE):
			readVal = readNumber(addr)
			time.sleep(0.25)
			sec += 0.25

		readVal = readNumber(addr)

		if (readVal == CONST.DISPENSER_ERROR):
			devices[addr]  = CONST.LOCATION_UNKNOWN
			print "Unexpected error on containerDispenseThread at address ", addr
			return

		elif (readVal > 50):
			devices[addr] = CONST.WRONG_ANSWER
			print "Unexpected respone from containerDispenseThread ", addr
			print "\tResponse: ", readVal
		else:
			devices[addr] = readVal

	except IOError:
		print "Lost connection to containerDispenseThread addr=", addr
		devices[addr] = CONST.CONNECTION_LOST
		return
	except:
		print "Unexpected error caught: ", sys.exc_info()[0]
		devices[addr]  = CONST.UNEXPECTED_ERROR_CODE
		return
	return


#function to began dispensing from all detected container
#will need to be changed based on the medication dictionary
#Expected parameter:
#	a dictionary that is a list of devices address to dosage-to-dispense mapping
def startDispensing(devices):
	print "\nBegin dispesing routine:\n"
	threads = []
	results = {}

	for addr in devices:
		results.update({addr : None})
		threads.append(threading.Thread(target=containerDispenseThread, args=(results,addr,devices[addr])))
	#fetch dosage from container list
	
	for i in range (len(threads)):
		threads[i].start()
	
	for i in range(len(threads)):
		threads[i].join()
	
	print "\nAll dispensing completed\n"
	return results


#function used for communcating with a slave trinket(aka container)
#DO NOT call this function directly
def writeNumber(addr, value):
	bus.write_byte(addr, value)
	return -1

#function used for communcating with a slave trinket(aka container)
#DO NOT call this function directly
def readNumber(addr):
	number = bus.read_byte(addr)
	return number


#scan for containers
#Due to the constraint of the i2c bus line, max number of container
#  will be 127, where the possible slave (container in our case)
#  addresses are 1 to 127 and the master reserves address 0 for itself.
#A exception will be made for the Real Time Clock module as it also
#  uses i2c bus; special rules will be made for the address of the RTC
#scanUnits() will iterate through all addresses, except the RTC address (68),
#  and request a particular response from the containers
#Return:
#	returns a dictionary that contains a list of valid containers
def scanForAll():
	devices = {}
	for addr in range (1, 67):
		try:
			writeNumber(addr, CONST.DISPENSER_RESET)
			time.sleep(0.25)
			num = readNumber(addr)
			if (num == 250):
				devices[addr] = None
				print "Device found at address 0x", addr
		except:
			pass
	for addr in range (69, 127):
		try:
			writeNumber(addr, CONST.DISPENSER_RESET)
			time.sleep(0.25)
			num = readNumber(addr)
			if (num == 250):
				devices[addr] = None
				print "Device found at address 0x", addr
		except:
			pass
	return devices


#Function that returns true if the given address is a reponse of a container
def scanFor(addr):
	try:
		writeNumber(addr, CONST.DISPENSER_RESET)
		time.sleep(0.25)
		num = readNumber(addr)
		if (num == 250):
			return true
	except:
			pass
	return false
	
"""
CODES USED FOR TESTING:	
while 1:
	
	devices = scanForAll()
	
	for i in range (1, 5):
		if ( len(devices) > 0 ):
			startDispensing(devices)
			print "\n\n"
		
			#For each device, print match error based on error code
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
		time.sleep(1)

"""
