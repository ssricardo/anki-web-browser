# -*- coding: utf-8 -*-
# Related to config_controller
# Test code for web modules

# This files is part of anki-web-browser addon
# @author ricardo saturnino
# ------------------------------------------------

import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
sys.argv.append('-awb-test')

from PyQt5 import QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView
app = QtWidgets.QApplication(sys.argv)

from src.config import config_view as cc
from src.config.main import ConfigHolder, Provider

main = QtWidgets.QMainWindow()
view = cc.ConfigView(None)
view.open(ConfigHolder(providers=[Provider("Insta", "https://instagram.com/{}").__dict__]))
sys.exit(app.exec_())
