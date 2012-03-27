from sys import argv
#
import config
import boto.sdb
from boto.exception import SDBResponseError
from parsing import parsing

# Helpful links:
# http://nullege.com/codes/search/boto.exception.SDBResponseError
# http://docs.python.org/library/stdtypes.html#typesseq
# http://stackoverflow.com/questions/8176002/how-can-i-handle-a-boto-exception-in-python

# Helpful python:
#print strftime("%Y-%m-%dT%H:%M:%S+0000", localtime()) #Properly formatted for SimpleDB!
#conn = boto.sdb.connect_to_region('us-west-2',aws_access_key_id=config.values['access_key_id'],aws_secret_access_key=config.values['secret_access_key'])
#results = conn.get_all_domains()


def connect():
	conn = boto.sdb.connect_to_region(config.values['region'],aws_access_key_id=config.values['access_key_id'],
						aws_secret_access_key=config.values['secret_access_key'])
	try:
		conn.get_all_domains()
	except SDBResponseError as error:
		aws_print_error(error)
  	return conn		
			
	
if __name__ == "__main__":

	#First we make sure the config has variables in it
	if (config.values['access_key_id']=='access key here' 
		or config.values['secret_access_key']=='secret key here' 
		or config.values['domain']=='your desired domain name here'):
		print_error('Please set your values in the config.py file!')

	#Second, we see if the options they used make sense
	the_input=parsing(argv)

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
	if the_input.flags['is_purge']==True:
		the_input.remEntry(dom)
	elif the_input.flags['is_report']==True:
		the_input.fetchRecord(dom)
	elif the_input.flags['is_entry']==True:
		the_input.logEntry(dom)


