import sys, subprocess, re

subprocess.call(["pyrcc4", "resources.qrc", "-o", "resources_rc.py", "-py3"])

# Read in the file
filedata = ""
with open('resources_rc.py', 'r') as file :
	for line in file:
		filedata += line
	file.close()

# Replace the target string
filedata = filedata.replace("PyQt4", "PyQt5")

# Write the file out again
with open('resources_rc.py', 'w') as file :
  file.write(filedata)
  file.close()
