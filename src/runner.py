# -------------------------------------------------------------
# Module for anki-web-browser addon

# This files is part of anki-web-browser addon
# @author ricardo saturnino
# -------------------------------------------------------------

import os

from aqt import gui_hooks
from aqt import mw
from aqt.utils import openLink, showWarning, tooltip

from .base_controller import BaseController
from .config.main import config_service as cfg, ConfigHolder
from .core import Feedback
from .editor_controller import set_new_editor, editor_controller, setup_editor_bindings
from .result_handler import ResultHandler
from .review_controller import review_controller


# --------------------------------------


# @staticmethod
def _ankiShowInfo(*args):
    text = "".join(args)
    tooltip(text, 3500)


# @staticmethod
def _ankiShowError(*args):
    showWarning(str(args))


def _bindAnkiConfig():

    def _readAnkiToObj():
        print("Anki read config")
        configMap = mw.addonManager.getConfig(__name__)
        return ConfigHolder(**configMap)

    def _writeAnkiConfig(config):
        print("Anki write config")
        mw.addonManager.writeConfig(__name__, config.toDict())

    cfg._readConfigAsObj = _readAnkiToObj
    cfg._writeConfig = _writeAnkiConfig
    ResultHandler.get_media_location = lambda: os.path.join(mw.pm.profileFolder(), "collection.media")


def run():

    _bindAnkiConfig()
    Feedback.log('Setting anki-web-browser controller')
    Feedback.showInfo = _ankiShowInfo
    Feedback.showError = _ankiShowError
    Feedback.showWarn = lambda args: tooltip('<b>Warning</b><br />' + args, 7500)
    BaseController.openExternalLink = openLink

    cfg.getConfig()  # Load web
    review_controller.init_configurable_components()
    review_controller.setup_view(mw)
    editor_controller.init_configurable_components()

    setup_editor_bindings()
    gui_hooks.editor_did_init.append(set_new_editor)

    if cfg.firstTime:
        review_controller.browser.welcome()
