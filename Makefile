all:
	python3 pyrcc5.py
	mv resources_rc.py src/resources_rc.py

run:
	python3 src/main.py