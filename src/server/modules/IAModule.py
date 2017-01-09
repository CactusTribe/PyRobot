from ThreadClient import ThreadClient
from devices.Devices import *

class IAModule(ThreadClient):
	def __init__(self, name):
		ThreadClient.__init__(self, name)

	# Execute command
	def execute_cmd(self, cmd):
		args = cmd.split(" ")
		cmd = args[0]