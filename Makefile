PI=pi@joaquim-lefranc.butandsystems.com:~/PyRobot_Serveur/

all:
	python3 make_qrc.py
	python3 pyrcc5.py
	mv resources_rc.py src/client/resources_rc.py
	python3 setup.py py2app -A

run:
	open dist/PyRobot.app

send:
	scp -P 2238 -r src/server/devices/ $(PI)
	scp -P 2238 -r src/server/modules/ $(PI)
	scp -P 2238 src/server/PyRobot_Serveur.py $(PI)
	scp -P 2238 src/server/ThreadClient.py $(PI)
	scp -P 2238 src/server/SharedParams.py $(PI)

deploy:
	python3 setup.py py2app