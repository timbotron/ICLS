import xml.dom.minidom
from time import strftime, strptime
from sys import exit
from textwrap import wrap

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
  	exit()
  	return True

def print_error(error_text):
	error_message=colorize('red',"ERROR",1)+colorize('red',"\nError Message: ")+error_text
  	print error_message
  	exit()
  	return True

#takes an entry, and makes it pretty!
def makeover(entry,ismonochrome=False):	
	if ismonochrome==False:
		output=colorize('gray','========================================',1)	
		output+=colorize('cyan',entry['entry'],1)
		output+=colorize('cyan',strftime("%H:%M %m.%d.%Y", strptime(entry['date'],"%Y-%m-%dT%H:%M:%S+0000")),1)
		output+=colorize('gray','ID: '+entry.name,0)
	else:
		output="========================================\n"
		output+=entry['entry']+"\n"
		output+=strftime("%H:%M %m.%d.%Y", strptime(entry['date'],"%Y-%m-%dT%H:%M:%S+0000"))+"\n"
		output+='ID: '+entry.name

		
	return output
#If, during parsing, help was flagged print out help text and then exit TODO read it from a md file
def print_help():
	print colorize('highblue',"ICLS (Inconcievebly Complex Logging System)",1)
	print colorize('white','DESCRIPTION:')
	print "A silly, contrived command line application to add and search text entries that are stored in Amazons AWS SimpleDB.\n"
	print colorize('white','SYNOPSIS:')
	print "icls.py [-c] [-d] [-r] [-s] [-t] [-p]\n"
	print colorize('white','ENTRY EXAMPLES:')
	print "[no option]\tA simple entry into the system.\n\tEx: icls.py 'Here is an entry.'\n"
	print wrap("[-c]\t\tWill have #complete truncated to the end of the entry. Ex. icls.py -c 'Here is a completed entry.' Will go into SimpleDB with '#complete' at end.")
	exit()