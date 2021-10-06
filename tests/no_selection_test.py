# -*- coding: utf-8 -*-
# Related to no_selection
# Test code for no selecion option

# This files is part of anki-web-browser addon
# @author ricardo saturnino
# ------------------------------------------------

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
sys.argv.append('-awb-test')

import src.no_selection as ns
import src.config.main as cc

from PyQt5 import QtWidgets
app = QtWidgets.QApplication(sys.argv)

_tested = ns.NoSelectionViewAdapter

# TODO...

@pytest.fixture()
def setup():
    pass

def test_loadOK():
    pass
    # cc.currentLocation = os.path.dirname(os.path.realpath(__file__))
    # os.remove(cc.currentLocation + '/' + cc.CONFIG_FILE)
    # config = _tested.load()
    # assert config is not None
    # assert (config.keepBrowserOpened is True)
    # assert (config.browserAlwaysOnTop is False)
    # assert (5 == len(config.providers))




if __name__ == '__main__':
    if '-view' in sys.argv:        
        main = QtWidgets.QMainWindow()
        view = ns.NoSelectionController(main)
        view.setFields({
            1: "State",
            2: "City",
            3: "Stadion"
        })
        # view.open()
        view.open()
        sys.exit(app.exec_())
