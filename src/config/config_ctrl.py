# -*- coding: utf-8 -*-
# Intermediates comunication between Config API and Config View
#
# This files is part of anki-web-browser addon
# @author ricardo saturnino
# -------------------------------------------------------

from .main import service
from .config_view import ConfigView


# noinspection PyPep8Naming
class ConfigController:
    """
        Manages the view interface for configurations
    """

    _ui: ConfigView = None
    _tempCfg = None

    def __init__(self, myParent):
        self._ui = ConfigView(None)
        self._ui.save = service.save

    def open(self):
        """Opens the Config window"""
        self._ui.open(service.getConfig())
