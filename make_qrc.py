import sys,os

files_list = []

for path, subdirs, files in os.walk("resources/"):
	for name in files:
		if name[0] != ".":
			file_path = os.path.join(path, name)
			files_list += [file_path]
			print(file_path)



with open("resources.qrc","w") as f:
	f.write("<RCC>\n")
	f.write("\t<qresource prefix=\"/resources/img\">\n")
	
	for e in files_list:
		f.write("\t\t<file>{}</file>\n".format(e))

	f.write("\t</qresource>\n")
	f.write("</RCC>\n")
	f.close()