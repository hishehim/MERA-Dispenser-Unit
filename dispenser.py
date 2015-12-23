
import datetime
import time
import heapq
import threading
import httplib
import json
#import smbus

from uuid import getnode as get_mac

#bus = smbus.SMBus(1)

"""
/***********************
Class Dispenser vaiables:
***********************/
*	DISPENSER_ID is the mac address of pi which is also the primary key of the dispenser
*	OPERATION_START_TIME is the start time of the dispenser -user input datetime.time()
*	OPERATION_END_TIME is the end time of the dispenser  -user input datetime.time()
*	EACH_CONTAINER is a dictionary of {address: Container} which contains information about
		all the containers that is connected to the dispenser main unit
*	DISPENSER_HEAP is a modified min heap that keeps track of the next dispenser that will 
		dispense

/************************
Class dispeners functions:
************************/
*	__init__()is the constructor of dispenser
*	infoUpdate() is called in case OPERATION_START_TIME OR OPERATION_END_TIME is changed by 
		user
**	THE FUNCTION TO SCAN DISPENSERS SHOULD BE HERE [MIKE]
**	NETWORK CHECKING THREAD WILL BE KEPT HERE [NOT YET]
**	LOGGING FUNCTION [WILL NEED TO THINK MORE THOUGHLY]
**	HTTP REQUEST FUNCTIONS [ANAHI]
**	PARSING JSON [ASK ANAHI FOR HELP]
**	UPDATING DATABASE [ANAHI]
**	PARSING DATABASE TO GET VARIABLES WHEN CAN'T CONNECT TO SERVER CONVERT INTO USABLE TYPES 
		[SHOULD KNOW HOW TO PARSE FIRST]
		
"""
#need to update dispenser info into sqlite just once for the operation start and end time
class Dispenser:
	def __init__(self):
		self.DISPENSER_ID = get_mac()
		self.OPERATION_START_TIME = None
		self.OPERATION_END_TIME = None
		self.EACH_CONTAINER = {}
		self.DISPENSE_HEAP = Dispense_Heap()
		#out web link 
		self.WEB_URL="thawing-ravine-9396.herokuapp.com"

	def infoUpdate(self,startTime, endTime):
		self.OPERATION_START_TIME = startTime
		self.OPERATION_END_TIME = endTime
		
	"""	replaced by jhttp and pContainers 
	def ServerConnection(self):
		Connected = False
		tries = 0
		while(not Connected and tries<5):
			connection = httplib.HTTPSConnection(self.WEB_URL, timeout = 10)
			try:
				connection.request("GET","/")
				response = connection.getresponse()
				status = response.status
				if (status == httplib.OK):
					self.c = True
					break
		#		connection.close()
			except:
				pass
			tries += 1
			print "...", str(tries)
		return
	"""	
	"""
	def TimeStampLog(self, TimeLog):
		Logupdate ={}
		Time_Stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y %I:%M %p')
		Logupdate.update({"Dispenser ID": self.DISPENSER_ID, "Time Stamp": Time_Stamp})
		x = TimeLog[0][0]
		if (x == "Successes"):
			Logupdate.update({"Successes":TimeLog})
			Logupdate.update({"Errors":[]})
			Logupdate.update({"Warnings":[]})
		elif(x == "Errors"):
			Logupdate.update({"Success":[]})
			Logupdate.update({"Errors":TimeLog})
			Logupdate.update({"Warnings":[]})
		elif(x == "Warnings"):
			Logupdate.update({"Success":[]})
			Logupdate.update({"Errors":[]})
			Logupdate.update({"Warnings":TimeLog})
		Log = json.dumps(Logupdate)
		
		#http json request to server return True if updated
		httpBool = False 
		
		path = "/home/pi/Desktop/MERA/logs/"
		date = datetime.datetime.today().strftime("%Y_%m_%d") + ".json"
		if (not httpBool):
			if(not self.LogupdateServer):
				LogFile.open(path+date, 'r')
				data = json.load(LogFile)
				LogFile.close()
				type = data[x]
				type =  type + TimeLog
				data[x] = type
				LogFile.open(path+date, 'w')
				LogFile.write(json.dumps(data))
				LogFile.close()
			elif(self.LogupdateServer):
				WriteLog.open(path+date,'w')
				WriteLog.write(Log)

		"""
			

			
"""
/************************
Class Container variables:
************************/
*	Addr is the container address
*	Dosage is the number of pills to be taken per dispense
*	Frequency is the number of hours till next dispense datetime.timedelta(hours = x)
*	Next_Immediate is the next immedate dispense time in datetime.datetime yyyy:MM:dd hh:mm
*	Start is the time in datetime.time() format so its in hh:mm
*	Pills = total number of pills

/************************
Class Container functions:
************************/
*	__init__() constructor for Container check to see if the address is in the dictionary of containers
		then check to see if the next immediate time to dispense is greater than current time
		then update dispense heap and each container dictionary
*	chcck_address(address) check a given address and see if it's in the dictionary of online devices
*	printContainers() just prints out containers and its fields
*	dispenseUpdate() is a function that will only be called when pills are dispensed successfully 
		so that it updates the pill count and Next_Immediate then calls update on the Dispense heap
*	delete() deletes a container cuz it's not connected
*	TimeStampLog() returns a dictionary of {LogCode: {dispenser_id: {timestamp: {log reason}}}}
"""

class Container:
	#def __init__(self,addr, dosage, frequency, initial_time, start_time, numberPills, DayString, DISPENSE_HEAP, EACH_CONTAINER,DEVICES):
	def __init__(self,addr, dosage, frequency, initial_time, start_time, numberPills, DISPENSE_HEAP, EACH_CONTAINER,DEVICES):
		check = self.checkAddress(addr,DEVICES)
		if check and initial_time>datetime.datetime.now()-datetime.timedelta(minutes = 30):
			self.Addr = addr
			self.Dosage = dosage
			self.Frequency = frequency
			self.Next_Immediate = initial_time
			self.Start = start_time
			self.Pills = numberPills
			self.timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y %I:%M:%p')
			self.timestamp = self.TimeLog("s", "Adding Containers",self.timestamp)
			DISPENSE_HEAP.update(self.Next_Immediate, self.Addr)
			EACH_CONTAINER.update({self.Addr:self})			
		elif check:
			print "this container is online but time is not right"
			self.timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y %I:%M:%p')
			#log error to return to server
			self.timestamp = self.TimeLog("w","this container is online but time is not right",self.timestamp)
		elif initial_time>datetime.datetime.now():
			print "this container is not online but time is right"
			#log error to return to server
			self.timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y %I:%M:%p')
			self.timestamp =  TimeLog("w", "this container is not online",self.timestamp)
		else:
			print "this container is not online and time is wrong"
			#return error to server
			self.timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y %I:%M:%p')
			self.timestamp =  TimeLog("w", "this container is not online and time entered is wrong",self.timestamp)
	#device is a dictionary of online devices with addrs as its key
	def checkAddress(self,address,DEVICES):
		if address in DEVICES:
			return True
		else:
			return False
	
	def printContainers(self):
		print self.Addr, self.Dosage, self.Frequency, self.Start, self.Next_Immediate, self.Pills
	
	def dispenseUpdate(self,DISPENSE_HEAP):
		self.Pills -= self.Dosage
		self.Next_Immediate += self.Frequency
		if (self.Pills> 0 and self.Pills < 2 * self.Dosage):
			print"Container ", self.Addr, "is about to run out of pills"
			#Log into Warning Log that there's not enough pills for next pill
			#Connect with the server that there's not enouph pills
		if(self.Pills <= self.Dosage ):
			print"Container ", self.Addr, "is about to run out of pills"
		DISPENSE_HEAP.update(self.Next_Immediate,self.Addr)
			
	def delete(self,EACH_CONTAINER,DISPENSER_HEAP):
		del EACH_CONTAINER[self.Addr]
		for (x,y)in DISPENSE_HEAP:
			if y == self.Addr:
				i = DISPENSE_HEAP.index((x,y))
				DISPENSE_HEAP.pop(i)

	def TimeLog(self, type, message,eventTime):
		SUCCESS = []
		ERROR = []
		WARNING = []
		LOG = {}
		if (type =="s"):
			SUCCESS.append({"Container ID": self.Addr, "Message":message, "Scheduled Time": self.Next_Immediate.strftime('%m/%d/%Y %I:%M:%p'), "Event Time Stamp": eventTime})
			LOG.update({"Successes": SUCCESS})
			return LOG
		elif(type == "w"):
			WARNING.append({"Container ID": self.Addr, "Message":message, "Scheduled Time": self.Next_Immediate.strftime('%m/%d/%Y %I:%M:%p'), "Event Time Stamp": eventTime})
			LOG.update({"Warnings": WARNING})
			return LOG
		elif(type == "e"):
			ERROR.append({"Container ID": self.Addr, "Message":message, "Scheduled Time": self.Next_Immediate.strftime('%m/%d/%Y %I:%M:%p'), "Event Time Stamp": eventTime})
			LOG.update({"Errors":ERROR})
			return LOG

"""
/***********************
Class Dispense_Heap variable
************************/
*	Heap contains the touple (next_dispense_time, address)
		- next_dispense_time is in datetime format (yyyy,MM,dd,mm)
*	StartWindow is the time that's safe to dispense 30 minutes before next dispense time
*	EndWindow is the end time of the window that's safe to dispense 30 minutes after next dispense time

/***********************
Class Dispense_Heap functions:
************************/
*	__init__() is the constructor
*	getStart() return the exact start time of root on heap
*	getEnd() return the exact end time of root on heap
*	__getitem__() is to overwrite [] for the tuples
*	len() returns the number of nodes in the Heap
*	isEmpty() returns whether the heap is empty or not
*	dispense_insert() will insert new node into the Heap and update the start and end of Window
*	update() 
"""
		
class Dispense_Heap:
	def __init__(self):
		self.Heap = []
		heapq.heapify(self.Heap)
		self.StartWindow = datetime.time(0,0,0)
		self.EndWindow = (23,59,59)

	
	def getStart(self):
		self.StartWindow = self.Heap[0][0] - datetime.timedelta(minutes = 30)
		return self.StartWindow

	def getEnd(self):
		self.EndWindow = self.Heap[0][0] + datetime.timedelta(minutes = 30)
		return self.EndWindow	
		
	def update(self, next_time, addr):
		for (x,y)in self.Heap:
			if y == addr:
				i = self.Heap.index((x,y))
				self.Heap.pop(i)
				heapq.heapify(self.Heap)
		heapq.heappush(self.Heap,(next_time,addr))
	
	def len(self):
		return len(self.Heap)
	
	def isEmpty(self):
		if (len(self.Heap) == 0):
			return True
		else:
			return False
			
	def __getitem__(self,x):
		return self.Heap[x][0],self.Heap[x][1]
		
	def dispenseWindow(self, EACH_CONTAINER):
		eTime = self.getEnd()
		tries = 0
		Window = {}
		while (True):
			t = self.Heap[0][0] - datetime.timedelta(minutes = 30)
			if ( t < eTime):
				id = self.Heap[0][1]
				dosage = EACH_CONTAINER[id].Dosage
				Window.update({id:dosage})
				EACH_CONTAINER[id].dispenseUpdate(self)
			else: 
				break		
		return Window
	
	def checkExpired(self, EACH_CONTAINER):
		eTime = self.getEnd()
		while (True):
			t = self.Heap[0][0] - datetime.timedelta(minutes = 30)
			if ( t < eTime):
				id = self.Heap[0][1]
				dosage = EACH_CONTAINER[id].Dosage
				EACH_CONTAINER[id].dispenseUpdate(self)
				#log missed dosage
				#return EACH_CONTAINER[id].TimeLog("w","Pills Missed")
			else: 
				break
		
		
		
		
		
		
		
		
		
	
