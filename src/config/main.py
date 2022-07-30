# -*- coding: utf-8 -*-
# Handles Configuration reading, saving and the integration with the web UI
# Contains model, service and view controller for Config
#
# This files is part of anki-web-browser addon
# @author ricardo saturnino
# -------------------------------------------------------
from typing import List

from ..core import Feedback

import os
import json
import re
import shutil

_currentLocation = os.path.dirname(os.path.realpath(__file__))
_CONFIG_LOCATION = _currentLocation + '/..'
CONFIG_FILE = 'config.json'


def addon_home() -> str:
    raise ValueError("Must be overiden")

# ---------------------------------- Model ------------------------------


# noinspection PyPep8Naming
class ConfigHolder:
    SHORTCUT = 'Ctrl+Shift+B'
    RP_SHORT = 'F10'
    INITIAL_SIZE = '850x500'

    def __init__(self, keepBrowserOpened=True, browserAlwaysOnTop=False, menuShortcut=SHORTCUT,
                 providers=[], initialBrowserSize=INITIAL_SIZE, enableDarkReader=False,
                 repeatShortcut=RP_SHORT, useSystemBrowser=False, groups=[], filteredWords=[],
                 imgMaxHeight: int = None, imgMaxWidth: int = None, **kargs):

        self.providers = [Provider(**p) for p in providers]
        self.groups = [SearchGroup(**g) for g in groups]
        self.keepBrowserOpened = keepBrowserOpened
        self.browserAlwaysOnTop = browserAlwaysOnTop
        self.useSystemBrowser = useSystemBrowser
        self.menuShortcut = menuShortcut
        self.repeatShortcut = repeatShortcut
        self.filteredWords = filteredWords
        self.initialBrowserSize = initialBrowserSize

        self.imgMaxHeight = imgMaxHeight
        self.imgMaxWidth = imgMaxWidth
        self.enableDarkReader = enableDarkReader

    def toDict(self):
        res = dict({
            'keepBrowserOpened': self.keepBrowserOpened,
            'browserAlwaysOnTop': self.browserAlwaysOnTop,
            'useSystemBrowser': self.useSystemBrowser,
            'menuShortcut': self.menuShortcut,
            'repeatShortcut': self.repeatShortcut, 
            'providers': [p for p in map(lambda p: p.__dict__, self.providers)],
            'groups': [g for g in map(lambda g: g.__dict__, self.groups)],
            'filteredWords': self.filteredWords,
            'initialBrowserSize': self.initialBrowserSize,
            'enableDarkReader': self.enableDarkReader,
            'imgMaxHeight': self.imgMaxHeight,
            'imgMaxWidth': self.imgMaxWidth
        })
        return res


class Provider:

    def __init__(self, name, url, **kargs):
        self.name = name
        self.url = url


class SearchGroup:

    def __init__(self, name: str, providerList: List[str]):
        self.name = name
        self.providerList = providerList


# ------------------------------ Service class --------------------------
# noinspection PyPep8Naming,PyMethodMayBeStatic
class ConfigService:
    """
        Responsible for reading and storing configurations
    """
    _config = None
    _validURL = re.compile('^((http|ftp){1}s{0,1}://)([\w._/?&=%#,@]|-)+{}([\w._/?&=%#,;+]|-)*$')
    firstTime = None

    def getConfig(self):
        if not self._config:
            return self.load()
        return self._config

    def _configLocationV5(self):
        return "%s/%s" % (_currentLocation, CONFIG_FILE)

    def load(self, createIfNotExists=True):
        Feedback.log('[INFO] Trying to read web-browser config')
        try:
            conf = self._readConfigAsObj()
        except Exception as e:
            print(e)
            conf = False

        if not conf and createIfNotExists:
            conf = self._createConfiguration()
        self._config = conf
        return conf

    def _readConfigAsObj(self) -> ConfigHolder:
        raise Exception("Must be overridden")

    def _writeConfig(self, config):
        """ Handles file writing... """
        raise Exception("Must be overridden")

    def _createConfiguration(self):
        """
            Creates a new default configuration file. 
            A simple JSON from a dictionary. Should be called only if the file doesn't exist yet
        """

        Feedback.log('[INFO] Creating a new web-browser config')

        conf = ConfigHolder()

        # default providers
        conf.providers = [
            Provider('Google Web', 'https://google.com/search?q={}'),
            Provider('Google Translate', 'https://translate.google.com/#view=home&op=translate&sl=auto&tl=en&text={}'),
            Provider('Google Images', 'https://www.google.com/search?tbm=isch&q={}'),
            Provider('Forvo', 'https://forvo.com/search/{}/')]

        conf.groups = [SearchGroup('Google', ['Google Web', 'Google Translate', 'Google Images'])]

        self._writeConfig(conf)
        self.firstTime = True
        return conf

    def _configLocation(self):
        return "%s/%s" % (addon_home(), CONFIG_FILE)

    def save(self, config):
        """ Save a given configuration """

        Feedback.log('Save: ', vars(config))

        if not config:
            return

        try:
            self.validate(config)
        except ValueError as ve:
            Feedback.showInfo(ve)
            return False
        
        Feedback.log('[INFO] Storing web-browser')
        self._writeConfig(config)
        self._config = config
        Feedback.showInfo('Anki-Web-Browser configuration saved')
        return True

    def validate(self, config):
        """
            Checks the configuration before saving it. 
            Checks types and the URL from the providers
        """

        checkedTypes = [(config, ConfigHolder), (config.keepBrowserOpened, bool), (config.browserAlwaysOnTop, bool),
                        (config.useSystemBrowser, bool), (config.providers, list),
                        (config.enableDarkReader, bool),
                        (config.imgMaxHeight, int), (config.imgMaxWidth, int)]
        for current, expected in checkedTypes:
            if current is None:
                continue
            if not isinstance(current, expected):
                raise ValueError('{} should be {}'.format(current, expected))

        for name, url in map(lambda item: (item.name, item.url), config.providers):
            if not name or not url:
                raise ValueError('There is an illegal value for one provider (%s %s)' % (name, url))
            if not self._validURL.match(url):
                raise ValueError('Some URL is invalid. Check the URL and if it contains {} that will be replaced by ' +
                                 'the text: %s' % url)

        if not self.isValidSize(config.initialBrowserSize):
            raise ValueError('Initial browser size contains invalid values')

    # ---------------------------------- Validations ------------------------------------

    reDimensions = re.compile(r'\d+x\d+', re.DOTALL)

    def isValidSize(self, value: str):
        return self.reDimensions.match(value)

    def getInitialWindowSize(self) -> tuple:
        cValue = self._config.initialBrowserSize if hasattr(self._config, 'initialBrowserSize') else None
        if cValue:
            if self.reDimensions.findall(cValue):
                return tuple(map(lambda i: int(i), cValue.split('x')))
        return tuple(map(lambda i: int(i), self._config.INITIAL_SIZE.split('x')))


# -----------------------------------------------------------------------------
# global instances

service = ConfigService()
