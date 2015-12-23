import dispenser
import datetime
import time
import threading
#for retrieving update
#import jhttp
#for posting containers
#import pcontainers
#for dispensing, canning of containers
import Dispensing
#for button
import PinManager as PM
#for all constant variables for dispensing
import CONSTANTS as const
#for retrieving 
#import SQLiteDBQueries as SQLite
#import logs
"""
def ConnectionCheckandUpdate():
	Devices = Dispensing.scanForAll()
	postData = {}
	for addr in Devices:
		containers =[]
		containers.append({"Container":addr, "Available":True })
		postData.update({"Dispenser ID": D.DISPENSER_ID, "Containers": containers})
	#check to see if we are connected to server
	connected = pcontainers.pContainers(json.dumps(postData))
	if (connected == 200):
		time.sleep(120)
		#if connected is successful call http request to pull updates
		data = jhttp.jRequest(D.DISPENSER_ID)
		#this will update the SQLite
		jhttp.SQLUpdate(data)
		sTime = datetime.datetime.strptime(data['Operation Start Time'], '%I:%M %p').time()
		eTime = datetime.datetime.strptime(data['Operation End Time'], '%I:%M %p').time()
		D.infoUpdate(sTime,eTime)
			
		for container in data['Containers']:
			addr = int(container['Container ID'])
			numberPills = int(container['Pill Count'])
			dosage = int(med['Dose'])
			frequency = datetime.datetime.timedelta(hours = int(med['Frequency']))
			start_time = datetime.datetime.strptime(med['Daily Time'], '%I:%M %p').time()
			inital_time = datetime.datetime.strptime(med['Scheduled Time'], ' %m/%d/%Y %I:%M %p ')
			newContainer = dispenser.Container(addr, dosage, frequency, initial_time, start_time, numberPills, dispenser.DISPENSE_HEAP, dispenser.EACH_CONTAINER,Devices)
				# UPDATE SQL LITE
		update = 1

	else:
		#parse local database to see previous entries
		contain = SQLite.fetchContainers()
		if (Contain == None):
			update = -1
		else:
			D.infoUpdate(contain.OstartTime, contain.OendTime)
			for each in contain:
				x = dis.Container(		contain.containerID
								,contain.dose
								,contain.frequency
								,contain.scheduledTime
								,contain.dailyTime
								,contain.pillCount
								,dispenser.DISPENSE_HEAP
								,dispenser.EACH_CONTAINER
								,dispenser.DEVICES
							)
		update = 0
"""

D = dispenser.Dispenser()
print "\n"
print "\n"
print "\n"
print "MERA Start Program Time: " , datetime.datetime.now().strftime('%m/%d/%Y %I:%M:%p')
#update = ConnectionCheckandUpdate()
print "\n"
print "\n"
print "\n"


print "Retrieving data for update"

update = 0
if (update ==-1):
	tries = 0
	while (update == -1 and tries < 5):
		tries += 1
		#update = ConnectionCheckandUpdate()
		print "Trying to connect..." ,tries 

Devices = {8: "a", 40: "c" }
		

#creating dummy dispensers
x = dispenser.Container(	8
					,2
					,datetime.timedelta(hours=5)
					,datetime.datetime.now()+datetime.timedelta(minutes = 1)
					,datetime.time(9,0,0)
					,30
					,D.DISPENSE_HEAP
					,D.EACH_CONTAINER
					,Devices
					)
print x.timestamp
					

x = dispenser.Container(	40
					,5
					,datetime.timedelta(hours=20)
					,datetime.datetime.now()+datetime.timedelta(minutes = 5)
					,datetime.time(9,0,0)
					,30
					,D.DISPENSE_HEAP
					,D.EACH_CONTAINER
					,Devices
					)
print x.timestamp

#put what we have just created into a gigantic while loop
start = datetime.time (9,0,0)
end = datetime.time(21,0,0)
D.infoUpdate(start,end)


while (True): 
	while ((datetime.datetime.now().time()>D.OPERATION_START_TIME) and (datetime.datetime.now().time() < D.OPERATION_END_TIME)):
		nextDispense = (D.DISPENSE_HEAP.getStart() - datetime.datetime.now()).total_seconds()
		nextCheck = 600
		if (nextDispense < nextCheck):
			#time.sleep(nextDispense)
			PM.setLEDState("READY")
			print "Setting LED"
			while(True):
				isNotPressed = True
				while(datetime.datetime.now()>=D.DISPENSE_HEAP.getStart() and datetime.datetime.now()<=D.DISPENSE_HEAP.getEnd() and isNotPressed):
					#ConnectionCheckandUpdate()
					if(update == 1):
						print "there was an upadte from the server"
					isNotPressed = PM.getButton()
					#isNotPressed = False
				
					#Button is pressed		
				if (not isNotPressed):
					window = D.DISPENSE_HEAP.dispenseWindow(D.EACH_CONTAINER)
					print "Items in the window" , window
					devices = Dispensing.startDispensing(window)
					print "Dispenseing"
					for addr in devices:
						if (devices[addr] in const.ERROR.keys()):
							print "Device", addr, ": ", const.ERROR[devices[addr]]
						elif(devices[addr] == 0):
							print "Device", addr, ": Dispense succesfull"
						elif(devices[addr] == None):
							print "Device", addr, ": Invalid number of dosage"
						else:
							print "Device", addr, ": Failed to dispense ", devices[addr], " pills"
						devices[addr] = None
					#after getting the results send the log to server
				else:
					D.DISPENSE_HEAP.checkExpired(D.EACH_CONTAINER)
					#update all expired elements (loop)? from in the heap
					#log all expired elements
					#check if next non-expired element has entered window. Break if not within window
					if (datetime.datetime.now()< D.DISPENSE_HEAP.getStart() or datetime.datetime.now()> D.DISPENSE_HEAP.getEnd()):
						break; #break out if next element is not within window
			PM.setLEDState("UNAVAILABLE")
			print "Set LED to UNAIVALABLE"
		else:
			print "Outside of Window of Dispensing Check Connection to server"
			print "Until the next window opens"
			time.sleep(nextCheck)
			#ConnectionCheckandUpdate()
			
#146.95.190.36
