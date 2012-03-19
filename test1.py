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
	conn = boto.sdb.connect_to_region(config.values['region'],aws_access_key_id=config.values['access_key_id'],
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
	entry=entry.replace('\\','')
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
#If, during parsing, help was flagged print out help text and then exit
def print_help():
	print colorize('highblue',"ICLS (Inconcievebly Complex Logging System)",1)
	print colorize('white','DESCRIPTION:')
	print "A silly, contrived command line application to add and search text entries that are stored in Amazons AWS SimpleDB.\n"
	print colorize('white','SYNTAX:')
	sys.exit()
			
class parsing:
	flags={'is_report':False,
			'is_entry':False,
			'entry_text':'',
			'is_tag':False,
			'is_search':False,
			'search_term':[],
			'is_default':False,
			'is_complete':False,
			'is_help':False,
			'start_date':False,
			'end_date':False,
			'search_query':False}
	def __init__(self,argv):
		if argv[1][0]=='-':
			for arg in argv[1]:
				if arg=='r':   self.flags['is_report']=True
				elif arg=='d':
					self.flags['is_default']=True
					self.flags['is_entry']=True
					self.flags['entry_text']=argv[2]
				elif arg=='c':
					self.flags['is_complete']=True
					self.flags['is_entry']=True
					self.flags['entry_text']=argv[2]		
				elif arg=='h': self.flags['is_help']=True
				elif arg=='t':
					self.flags['is_tag']=True
					self.flags['is_search']=True
					self.flags['is_report']=True
				elif arg=='s':
					self.flags['is_search']=True
					self.flags['is_report']=True
			if self.flags['is_complete']==True and self.flags['is_report']==True: self.flags['is_help']=True
		else:
			self.flags['is_entry']=True
			self.flags['entry_text']=argv[1]
		#If anything was wrong, send to help
		if self.flags['is_help']:
			print_help()
		#Lets get all the report/search stuff together!
		if self.flags['is_report']:
			self.flags['search_query']='select * from `icls`'
			#It's a report, first try to parse it
			print "It's a report!, num of args:"+str(len(argv))
			if self.flags['is_search']:
				self.flags['search_query']+=' WHERE '
				print "It's a search!"
				if len(argv)<3:	print_error('No Search term or tag detected; use -h to see options')
				else:					
					if argv[2].count(',')>0:
						for i, v in enumerate(argv[2].split(',')):
							self.flags['search_term'].append(v)
					else: self.flags['search_term'].append(argv[2])
					# TODO Now we iterate and make there where clause, IN if search, tag= if tag
					for key, term in enumerate(self.flags['search_term']):
						if self.flags['is_tag']:
							if key==0: self.flags['search_query']+="tag IN ("
							if key>0:	self.flags['search_query']+=","
							self.flags['search_query']+="'"+term+"'"
						else:							
							if key>0:	self.flags['search_query']+=' AND '
							self.flags['search_query']+=" entry LIKE '%"+term+"%'"		
					if self.flags['is_tag']: self.flags['search_query']+=')'	
	
				if len(argv)>=4:
					#term and start date					
					self.flags['start_date']=argv[3]
					self.flags['search_query']+=" AND date>'"+self.flags['start_date']+"'"
				if len(argv)==5:
					#term, start and finish date	
					self.flags['end_date']=argv[4]				
					self.flags['search_query']+=" AND date<'"+self.flags['end_date']+"'"				
			else:				
				if len(argv)>=3:
					#start date only
					self.flags['start_date']=argv[2]
					self.flags['search_query']+=" WHERE date>'"+self.flags['start_date']+"'"
				if len(argv)==4:
					#term and start date
					self.flags['end_date']=argv[3]	
					self.flags['search_query']+=" AND date<'"+self.flags['end_date']+"'"	
		
		print self.flags

	def fetchRecord(self,dom):	
		try:
			results = dom.select(self.flags['search_query'])
		except SDBResponseError as error:
			aws_print_error(error)	 		
		results_yn=0 	#this is in case there are no results, don't know why this isn't built in.
		for result in results:
			results_yn=1
			print makeover(result)
		if results_yn==1:
			print colorize('gray','==============================',0)
		return True
	
	#takes in domain connection, entry text, and flag of completed or not.
	def logEntry(self,dom):
		output=''
		entry=self.flags['entry_text']
		if self.flags['is_complete']==True:
			entry+=' #complete'
			output+=colorize('cyan','Completed a task, way to go!',1)
		if self.flags['is_default']==True:
			entry+=' #'+config.values['default']
		the_id=uuid4()
		entry=entry.replace('\\','')
		entry_dict={'entry':entry,'date':strftime("%Y-%m-%dT%H:%M:%S+0000", localtime())}								
		try:		
			dom.put_attributes(the_id,entry_dict)
			add_tags(dom,the_id,entry)
		except SDBResponseError as error:
				aws_print_error(error)
		output+=colorize('gray','Entry: '+entry,1)
		output+=colorize('green','Log entry submitted successfully.')
		print output
		return True

	
#
#
#	BEGIN MAIN
#
#
print sys.argv
#First we make sure the config has variables in it
if (config.values['access_key_id']=='access key here' 
	or config.values['secret_access_key']=='secret key here' 
	or config.values['domain']=='your desired domain name here'):
	print_error('Please set your values in the config.py file!')

#Second, we see if the options they used make sense
the_input=parsing(sys.argv)

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

if the_input.flags['is_report']==True:
	the_input.fetchRecord(dom)
elif the_input.flags['is_entry']==True:
	the_input.logEntry(dom)


	



entry_text=''
output=''


