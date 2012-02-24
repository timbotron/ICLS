import sys
import xml.dom.minidom
from time import strftime, strptime, localtime
from uuid import uuid4
from re import compile
import config
import boto.sdb
from boto.exception import SDBResponseError
from uuid import uuid4

# Helpful links:
# http://nullege.com/codes/search/boto.exception.SDBResponseError
# http://docs.python.org/library/stdtypes.html#typesseq
# http://stackoverflow.com/questions/8176002/how-can-i-handle-a-boto-exception-in-python

# Helpful python:
#print strftime("%Y-%m-%dT%H:%M:%S+0000", localtime()) #Properly formatted for SimpleDB!
#conn = boto.sdb.connect_to_region('us-west-2',aws_access_key_id=config.values['access_key_id'],aws_secret_access_key=config.values['secret_access_key'])
#results = conn.get_all_domains()


def colorize(the_color='blue',entry='',new_line=0):
	color={'gray':30,'green':32,'red':31,'blue':34,'magenta':35,'cyan':36,'white':37,'highgreen':42,'highblue':44,'highred':41,'highgray':47}
	if new_line==1:
		new_line='\n'
	else:
		new_line=''
	return_me='\033[1;'+str(color[the_color])+'m'+entry+'\033[1;m'+new_line
	return return_me

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

# Only if error is one that halts things, stop script
def aws_print_error(error_obj):
	error_code=getText(xml.dom.minidom.parseString(error_obj[2]).documentElement.getElementsByTagName('Code')[0].childNodes)
	error_message=getText(xml.dom.minidom.parseString(error_obj[2]).documentElement.getElementsByTagName('Message')[0].childNodes)
	error_message=colorize('red',"ERROR",1)+colorize('red',"AWS Error Code: ")+error_code+colorize('red',"\nError Message: ")+error_message
  	print error_message
  	sys.exit()
  	return True

def print_error(error_text):
	error_message=colorize('red',"ERROR",1)+colorize('red',"\nError Message: ")+error_text
  	print error_message
  	sys.exit()
  	return True

def connect():
	conn = boto.sdb.connect_to_region('us-west-2',aws_access_key_id=config.values['access_key_id'],
						aws_secret_access_key=config.values['secret_access_key'])
	try:
		conn.get_all_domains()
	except SDBResponseError as error:
		aws_print_error(error)
  	return conn		
  
def add_tags(dom,the_id,entry=''):
	if entry.count('#'):		
		pat = compile(r"#(\w+)")		
		for x in pat.findall(entry):
			try:
				#print x
				dom.put_attributes(the_id,{'tag':x},replace=False)
			except SDBResponseError as error:
				aws_print_error(error)	
	return True

#takes in domain connection, entry text, and flag of completed or not.
def logEntry(dom,entry='',done=0):
	the_id=uuid4()
	entry_dict={'com':done,'entry':entry,'date':strftime("%Y-%m-%dT%H:%M:%S+0000", localtime())}
	output=''
	if done==1:
		output+=colorize('cyan','Completed a task, way to go!',1)	
	try:		
		dom.put_attributes(the_id,entry_dict)
		add_tags(dom,the_id,entry)
	except SDBResponseError as error:
			aws_print_error(error)
	output+=colorize('gray','Entry: '+entry_text,1)
	output+=colorize('green','Log entry submitted successfully.')
	print output
	return True
#takes an entry, and makes it pretty!
def makeover(entry):	
	output=colorize('gray','==============================',1)	
	output+=colorize('cyan',entry['entry'],1)
	output+=colorize('gray',strftime("%H:%M %m.%d.%Y", strptime(entry['date'],"%Y-%m-%dT%H:%M:%S+0000")),0)
	return output
			
	
#generates reports, TODO match the readme functionality on this
def fetchRecord(dom,the_type='r',needle=''):
	if the_type=='t':
		query = 'select * from `icls` where tag="'+needle+'"'
	else: 
		query = 'select * from `icls`'
	results = dom.select(query)
	for result in results:
		print makeover(result)
	print colorize('gray','==============================',0)
	return True
#
#
#	BEGIN MAIN
#
#

#First we make sure the config has variables in it
if (config.values['access_key_id']=='access key here' 
	or config.values['secret_access_key']=='secret key here' 
	or config.values['domain']=='your desired domain name here'):
	print_error('Please set your values in the config.py file!')

#Now we connect to AWS!
conn=connect()

#Check if domain exists, if it doesn't create it
try:
 	dom = conn.get_domain(config.values['domain'])
except SDBResponseError as error:
	if getText(xml.dom.minidom.parseString(error[2]).documentElement.getElementsByTagName('Code')[0].childNodes)=='NoSuchDomain':
		try:
			conn.create_domain(config.values['domain'])
			dom = conn.get_domain(config.values['domain'])
		except SDBResponseError as error:
			aws_print_error(error)
	else:
		aws_print_error(error)



entry_text=''
output=''
print len(sys.argv)

if sys.argv[1]=='-c':
	#is a standard log entry that has been flagged completed	
	entry_text=sys.argv[2].replace('\\','')
	try:
		logEntry(dom,entry_text,1)
	except SDBResponseError as error:
		aws_print_error(error)
elif sys.argv[1]=='-r':
	#Requesting a report, check for dates
	try:
		fetchRecord(dom,'r')
	except SDBResponseError as error:
		aws_print_error(error)
elif sys.argv[1]=='-t':
	#Requesting a report, check for dates
	try:
		fetchRecord(dom,'t',sys.argv[2])
	except SDBResponseError as error:
		aws_print_error(error)
else:
	#is standard, non-completed log entry
	entry_text=sys.argv[1].replace('\\','')
	try:
		logEntry(dom,entry_text,0)
	except SDBResponseError as error:
		aws_print_error(error)
	

