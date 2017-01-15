import threading, io, struct, time
from ThreadClient import ThreadClient
from devices.Devices import *


class CameraModule(ThreadClient):
	def __init__(self, name):
		ThreadClient.__init__(self, name)
		self.camera_capture = False

	# Execute command
	def execute_cmd(self, cmd):
		args = cmd.split(" ")
		cmd = args[0]

		if cmd == "cam":
			self.Camera_commands(args)

	# --------------------------------------------
	# MODULE CAMERA
	# --------------------------------------------
	def Camera_commands(self, args):
		try:
			if args[1] == "start":
				print(" -> Start camera capture")
				self.camera_capture = True
				ThreadCapture = threading.Thread(target = self.Camera_capture, args = [] )
				ThreadCapture.start()

			elif args[1] == "stop":
				self.camera_capture = False
				print(" -> Stop camera capture")

		except Exception as e:
			print(e)
			traceback.print_exc()

	def Camera_capture(self):
		pipe = self.connection.makefile('wb')
		i = 0

		try:
			stream = io.BytesIO()
			for foo in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
				# Write the length of the capture to the stream and flush to
				# ensure it actually gets sent
				pipe.write(struct.pack('<L', stream.tell()))
				pipe.flush()
				# Rewind the stream and send the image data over the wire
				stream.seek(0)
				pipe.write(stream.read())

				if self.camera_capture == False:
					break

				# Reset the stream for the next capture
				stream.seek(0)
				stream.truncate()

				i += 1
				#print(" > Frame " + str(i) + " time " + str(elapsed)[0:6] + " ms")

			# Write a length of zero to the stream to signal we're done
			pipe.write(struct.pack('<L', 0))
			print(" (*) " + str(i) + " frames sended")

		finally:
			pipe.close()