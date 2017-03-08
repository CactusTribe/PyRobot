"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['src/client/MainWindow.py']
APP_NAME = "PyRobot"
DATA_FILES = ['qt.conf','resources','interfaces', 'data']

OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'app.icns',
    'packages': "PIL, PyQt5",
    'includes': ['sip'],
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': "Robot controlling",
        'CFBundleIdentifier': "com.cactus.osx.pyrobot",
        'CFBundleVersion': "0.1",
        'CFBundleShortVersionString': "0.1",
        'NSHumanReadableCopyright': u"Copyright © 2017, Joaquim Lefranc, All Rights Reserved"
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
