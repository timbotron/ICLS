from time import strftime, localtime
from uuid import uuid4
from re import compile
from framework import aws_print_error, colorize, print_help, makeover
from boto.exception import SDBResponseError

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
			#print "It's a report!, num of args:"+str(len(argv))
			if self.flags['is_search']:
				self.flags['search_query']+=' WHERE '
				#print "It's a search!"
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
		
		#print self.flags

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
			self.add_tags(dom,the_id,entry)
		except SDBResponseError as error:
				aws_print_error(error)
		output+=colorize('gray','Entry: '+entry,1)
		output+=colorize('green','Log entry submitted successfully.')
		print output
		return True

	def add_tags(self,dom,the_id,entry=''):
		if entry.count('#'):		
			pat = compile(r"#(\w+)")		
			for x in pat.findall(entry):
				try:
					#print x
					dom.put_attributes(the_id,{'tag':x},replace=False)
				except SDBResponseError as error:
					aws_print_error(error)	
		return True
