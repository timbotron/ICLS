import sys

def colorize(the_color='blue',entry='',new_line=0):
	color={'gray':30,'green':32,'red':31,'blue':34,'magenta':35,'cyan':36}
	if new_line==1:
		new_line='\n'
	else:
		new_line=''
	return_me='\033[1;'+str(color[the_color])+'m'+entry+'\033[1;m'+new_line
	return return_me


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

