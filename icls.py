#	This file is part of ICLS.
#
#	ICLS is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	ICLS is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with ICLS.  If not, see <http://www.gnu.org/licenses/>.

from sys import argv
import config
import boto.sdb
from boto.exception import SDBResponseError
from framework import aws_print_error, print_error
import xml.dom.minidom
from parsing import parsing

# Connect to the region chosen in the config file
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



