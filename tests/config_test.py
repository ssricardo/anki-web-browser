# -*- coding: utf-8 -*-
# Related to config_controller
# Test code for web modules

# This files is part of anki-web-browser addon
# @author ricardo saturnino
# ------------------------------------------------

import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')
sys.argv.append('-awb-test')

from src.config import main as cc
from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)

_tested = cc.ConfigService()


def test_loadOK():
    cc.currentLocation = os.path.dirname(os.path.realpath(__file__))
    if os.path.exists(cc.currentLocation + '/' + cc.CONFIG_FILE):
        os.remove(cc.currentLocation + '/' + cc.CONFIG_FILE)
    config = _tested.load()
    assert config is not None
    assert (config.keepBrowserOpened is True)
    assert (config.browserAlwaysOnTop is False)


def test_loadNoFile():
    try:
        config = _tested.load(False)
        assert 1 == 2  # exception expected
    except:
        pass


def test_loadAndSave():
    cc.currentLocation = os.path.dirname(os.path.realpath(__file__))
    config = _tested.load(False)
    providers = config.providers
    providers.append(cc.Provider('Yahoo', 'https://www.yahoo.com/{}'))
    config.keepBrowserOpened = True
    _tested._config = config

    return  # should not change the real file. Would break future tests
    _tested.save()


def test_validation():
    c = cc.ConfigHolder(browserAlwaysOnTop=True)
    _tested.validate(c)
    try:
        c2 = 'Error'
        _tested.validate(c2)
        assert 1 == 2  # exception expected
    except:
        pass

    try:
        c2 = cc.ConfigHolder()
        c2.providers = ['Oh no!']
        _tested.validate(c2)
        assert 1 == 2  # exception expected
    except:
        pass

    try:
        c2 = cc.ConfigHolder(keepBrowserOpened='Now as string')
        _tested.validate(c2)
        assert 1 == 2  # exception expected
    except:
        pass


def test_valid_urls():
    ch = cc.ConfigHolder()
    ch.providers.append(cc.Provider('Google', 'https://www.google.com/search?tbm=isch&q={}'))
    ch.providers.append(
        cc.Provider('Sentence', 'http://sentence.yourdictionary.com/{}?direct_search_result=yes'))
    ch.providers.append(cc.Provider('issues#5', 'https://www.google.co.jp/search?tbm=isch&q={}+アニメ美少女'))
    ch.providers.append(
        cc.Provider('Issue#5', 'https://lexin.nada.kth.se/lexin/#searchinfo={},swe_tur,ord;'))
    _tested.validate(ch)


def test_getInitialWindowSizeOk():
    ch = cc.ConfigHolder(initialBrowserSize="5050x30")
    _tested._config = ch
    result = _tested.getInitialWindowSize()
    assert (5050 == result[0])
    assert (30 == result[1])


def test_getInitialWindowSizeInvalid():
    ch = cc.ConfigHolder(initialBrowserSize="3030-30")
    _tested._config = ch
    result = _tested.getInitialWindowSize()
    assert (850 == result[0])
    assert (500 == result[1])

# if __name__ == '__main__':
#     if '-view' in sys.argv:
#         main = QtWidgets.QMainWindow()
#         view = cc.ConfigController(main)
#         view.open()
#         sys.exit(app.exec_())
