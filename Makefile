PI=pi@joaquim-lefranc.butandsystems.com:~/PyRobot_Serveur/
VERSION=0.1
APP_NAME=PyRobot

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	UI_DIR = interface_linux/
endif
ifeq ($(UNAME_S),Darwin)
	UI_DIR = interface_osx/
endif

all:
	python3 make_qrc.py
	pyrcc5 resources.qrc -o resources_rc.py
	mv resources_rc.py src/client/resources_rc.py

run:
	python3 src/client/MainWindow.py

runa:
	open dist/$(APP_NAME)/$(APP_NAME).app

clean:
	rm -rf dist/$(APP_NAME)/

send:
	scp -P 2238 -r src/server/devices/ $(PI)
	scp -P 2238 -r src/server/modules/ $(PI)
	scp -P 2238 src/server/PyRobot_Serveur.py $(PI)
	scp -P 2238 src/server/ThreadClient.py $(PI)
	scp -P 2238 src/server/SharedParams.py $(PI)

macos:
	python3 setup.py py2app -A
	rm -rf dist/$(APP_NAME)/
	mkdir dist/$(APP_NAME)/
	mkdir dist/$(APP_NAME)/camera_pictures
	mkdir dist/$(APP_NAME)/camera_videos
	mv dist/$(APP_NAME).app dist/$(APP_NAME)/

deploy_macos:
	python3 setup.py py2app
	rm -rf dist/$(APP_NAME)/$(APP_NAME).app
	mv dist/$(APP_NAME).app dist/$(APP_NAME)/

dmg:
	rm -rf dist/$(APP_NAME)_$(VERSION)/
	mkdir dist/$(APP_NAME)_$(VERSION)/
	cp -R dist/$(APP_NAME) dist/$(APP_NAME)_$(VERSION)/
	hdiutil create -volname $(APP_NAME) -srcfolder dist/$(APP_NAME)_$(VERSION)/ -ov -format UDZO dist/$(APP_NAME)_$(VERSION).dmg
	rm -rf dist/$(APP_NAME)_$(VERSION)/

info:
	find src/ -name '[^resources_rc, pyrcc5]*.py' | xargs wc -l