import json
import urllib2

def pContainer(postData):
	try:
		req = urllib2.Request('thawing-ravine-9396.herokuapp.com/containers')
		req.add_header('Content-Type', 'application/json')
		response = urllib2.urlopen(req, json.dumps(postData))
		result = response.getcode()
		return result
	except:
		print "HTTP Post Error"
		pass
