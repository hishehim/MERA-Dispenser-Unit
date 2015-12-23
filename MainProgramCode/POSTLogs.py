import json
import urllib2

postData = {"Dispenser ID":10,"Time Stamp": "","Warning":[{"Container ID": 1,"Message":"Missed Medication Dose", "Scheduled Time":"12/18/2015 09:10 AM"}],"Success":[{"Container ID": 2,"Message": "Succcessfully Dispensed Medication", "Scheduled Time":"12/18/2015 01:30 PM"}],"Error":[{"Container ID": 3, "Message": "Raspberry Pi Error","Scheduled Time":"12/20/2015 08:45 PM"}]}

#TIME IN THIS FORM PLEASE
#"Scheduled Time":"mm/dd/yyyy hh:mm aa"

try:
	req = urllib2.Request('http://localhost:9000/logs')
	req.add_header('Content-Type', 'application/json')
	response = urllib2.urlopen(req, json.dumps(postData))
except:
	print "HTTP Post Error"



