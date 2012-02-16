import sys
import xml.dom.minidom
import config
import boto.sdb
from boto.exception import SDBResponseError

# Helpful links:
# http://nullege.com/codes/search/boto.exception.SDBResponseError
# http://docs.python.org/library/stdtypes.html#typesseq
# http://stackoverflow.com/questions/8176002/how-can-i-handle-a-boto-exception-in-python

def colorize(the_color='blue',entry='',new_line=0):
	color={'gray':30,'green':32,'red':31,'blue':34,'magenta':35,'cyan':36}
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

def connect():
	conn = boto.sdb.connect_to_region('us-west-2',aws_access_key_id=config.values['access_key_id'],
						aws_secret_access_key=config.values['secret_access_key'])
	try:
		print conn.get_all_domains()
	except SDBResponseError as error:
		aws_print_error(error)
  	return conn		

def logEntry(entry='',done=0):
	return True

#conn = boto.sdb.connect_to_region('us-west-2',aws_access_key_id=config.values['access_key_id'],aws_secret_access_key=config.values['secret_access_key'])
#results = conn.get_all_domains()
conn=connect()

try:
 	results = conn.get_domain(config.values['domain']);
except SDBResponseError as error:
  	aws_print_error(error)


entry_text=''
output=''

if sys.argv[1]=='-c':
	output+=colorize('cyan','Completed a task, way to go!',1)
	entry_text=sys.argv[2].replace('\\','')
else:
	entry_text=sys.argv[1].replace('\\','')

output+=colorize('gray','Entry: '+entry_text,1)
output+=colorize('green','Log entry submitted successfully.')
print output

