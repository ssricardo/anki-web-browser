# -------------------------------------------------------------
# Module for anki-web-browser addon

# This files is part of anki-web-browser addon
# @author ricardo saturnino
# -------------------------------------------------------------

from aqt import mw
from aqt.utils import openLink, showWarning, tooltip

from .base_controller import BaseController
from .config.main import service as cfg, ConfigHolder
from .core import Feedback
from .review_controller import ReviewController
from .editor_controller import EditorController

# Holds references so GC doesnt kill them
controllerInstance = None
editorCtrl = None

# @staticmethod
def _ankiShowInfo(*args):
    tooltip(args, 3500)


# @staticmethod
def _ankiShowError(*args):
    showWarning(str(args))


def _bindAnkiConfig():
    # global cfg

    def _readAnkiToObj():
        print("Anki read config")
        configMap = mw.addonManager.getConfig(__name__)
        return ConfigHolder(**configMap)

    def _writeAnkiConfig(config):
        print("Anki write config")
        mw.addonManager.writeConfig(__name__, config.toDict())

    cfg._readConfigAsObj = _readAnkiToObj
    cfg._writeConfig = _writeAnkiConfig


def run():
    global controllerInstance, editorCtrl

    _bindAnkiConfig()
    Feedback.log('Setting anki-web-browser controller')
    Feedback.showInfo = _ankiShowInfo
    Feedback.showError = _ankiShowError
    Feedback.showWarn = lambda args: tooltip('<b>Warning</b><br />' + args, 7500)
    BaseController.openExternalLink = openLink

    cfg.getConfig()  # Load web
    controllerInstance = ReviewController(mw)
    controllerInstance.setupBindings()

    editorCtrl = EditorController(mw)

    if cfg.firstTime:
        controllerInstance.browser.welcome()
