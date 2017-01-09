import subprocess, re

from ThreadClient import ThreadClient
from devices.Devices import *

class EventModule(ThreadClient):
	def __init__(self, name):
		ThreadClient.__init__(self, name)

	# Execute command
	def execute_cmd(self, cmd):
		args = cmd.split(" ")
		cmd = args[0]

		if cmd == "wifi":
			#stdoutdata = subprocess.getoutput("python3 WifiQuality.py")
			stdoutdata = subprocess.getoutput("iwconfig")
			
			res = re.search(r"(Quality=)([0-9]{0,3})/([0-9]{0,3})", stdoutdata.split()[33])
			if res != None:
				current = int(res.group(2))
				maximum = int(res.group(3))
				percent = int( (current/maximum)*100 )

				self.tcp_send("wifi {}".format(percent))