# -*- coding: utf-8 -*-
# Related to config_controller
# Test code for web modules

# This files is part of anki-web-browser addon
# @author ricardo saturnino
# ------------------------------------------------

import os
import sys

from aqt.qt import *

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.argv.append("-awb-test")


app = QApplication(sys.argv)

from src.config import config_view as cc
from src.config.main import ConfigHolder, Provider, SearchGroup

main = QMainWindow()
view = cc.ConfigView(None)
view.save = lambda cfg: print(vars(cfg))
config = ConfigHolder(
    providers=[
        Provider("Insta", "https://instagram.com/{}").__dict__,
        Provider("LinkedIn", "https://linkedin.com/{}").__dict__,
    ],
    groups=[SearchGroup("Others", ["Insta", "LinkedIn"]).__dict__],
)
config.enableDarkReader = True

import json

print(json.dumps(config, default=lambda o: o.__dict__, indent=2))

view.open(config)
sys.exit(app.exec())
