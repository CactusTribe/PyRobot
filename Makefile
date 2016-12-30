PI=pi@joaquim-lefranc.butandsystems.com:~/PyRobot_Serveur/

all:
	python3 make_qrc.py
	python3 pyrcc5.py
	mv resources_rc.py src/client/resources_rc.py

run:
	python3 src/client/MainWindow.py

send:
	scp -P 2238 -r src/server/devices/ $(PI)
	scp -P 2238 src/server/PyRobot_Serveur.py $(PI)