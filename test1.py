import sys

#for arg in sys.argv:
#    print arg

#print sys.argv[1]
results=''

if sys.argv[1]=='-c':
	results+='\033[1;32mCompleted a task, way to go!\033[1;m\n'
results+='\033[1;36mLog Entry Submitted Successfully\033[1;m'
print results