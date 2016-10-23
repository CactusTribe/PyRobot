import sys, subprocess, re

if __name__ == "__main__":
	stdoutdata = subprocess.getoutput("iwconfig")
	
	res = re.search(r"(Quality=)([0-9]{0,3})/([0-9]{0,3})", stdoutdata.split()[33])
	if res != None:
		current = int(res.group(2))
		maximum = int(res.group(3))
		print("{}".format( int((current/maximum)*100 )))