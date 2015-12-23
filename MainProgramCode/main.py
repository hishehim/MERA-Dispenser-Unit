import dispenser
import datetime
import time
import threading
#for retrieving update
import jhttp
#for posting containers
import pcontainers
#for dispensing, canning of containers
import Dispensing
#for button
import PinManager as PM
#for all constant variables for dispensing
import CONSTANTS as const

D = dispenser.Dispenser()

Devices = Dispensing.scanForAll()
postData = {}
for addr in Devices:
	containers =[]
	containers.append({"Container":addr, "Available":True })
	postData.update({"Dispenser ID": D.DISPENSER_ID, "Containers": containers})
#check to see if we are connected to server
connected = pcontainers.pContainers(json.dumps(postData))
if (connected == 200):
	data = jhttp.jRequest(D.DISPENSER_ID)
	jhttp.SQLUpdate(data)
	
	if (data['Operation Start Time'] != null or data['Operation End Time'] != null):
		sTime = datetime.datetime.strptime(data['Operation Start Time'], '%I:%M %p')
		eTime = datetime.datetime.strptime(data['Operation End Time'], '%I:%M %p')
		D.infoUpdate(sTime,eTime])
		#UPDATE SQLITE
	for container in data['Containers']:
		if (container['Updated']):	
			addr = int(container['Container ID'])
			numberPills = int(container['Pill Count'])
			dosage = int(med['Dose'])
			frequency = datetime.datetime.timedelta(hours = int(med['Frequency']))
			start_time = datetime.datetime.strptime(med['Daily Time'], '%I:%M %p')
			inital_time = datetime.datetime.strptime(med['Scheduled Time'], ' %m/%d/%Y %I:%M %p ')
			newContainer = dispenser.Container(addr, dosage, frequency, initial_time, start_time, numberPills, dispenser.DISPENSE_HEAP, dispenser.EACH_CONTAINER,Devices)
			# UPDATE SQL LITE

else:
	#parse the database for values
	#but for now lets use dummy values
	x = dis.Container(		6
						,5
						,datetime.timedelta(hours=4)
						,datetime.datetime.now()+datetime.timedelta(minutes = 5)
						,datetime.time(9,0,0)
						,30
						,dispenser.DISPENSE_HEAP
						,dispenser.EACH_CONTAINER
						,dispenser.DEVICES
					)
			
#put what we have just created into a gigantic while loop 
t_diff = 0
while (datetime.datetime.now().time()>D.OPERATION_START_TIME and datetime.datetime.now().time() < D.OPERATION_END_TIME):
	nextDispense = (D.DISPENSE_HEAP.getStart() - datetime.datetime.now().time()).total_seconds()
	nextCheck = 600 -diff
	if (nextDispense < nextCheck):
		time.sleep(nextDispense)
		PM.setLEDState("READY")
		while (PM.getButton()):
			#check for if there's network update

		PM.setLEDState("BUSY")
		time.sleep(1)
		PM.cleanup()







