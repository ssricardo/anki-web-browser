# -*- coding: utf-8 -*-

# ---------------------------------- ================ ---------------------------------
# ---------------------------------- Base Controller -----------------------------------
# ---------------------------------- ================ ---------------------------------
from typing import List

from .config.main import service as cfg
from .core import Feedback
from .exception_handler import exceptionHandler
from .browser import AwBrowser
from .no_selection import NoSelectionController, NoSelectionResult
from .provider_selection import ProviderSelectionController


class BaseController:
    """ Concentrates common operations between both concrete controllers """

    browser = None
    _currentNote = None
    _ankiMw = None    

    def __init__(self, ankiMw):
        super().__init__()
        self._ankiMw = ankiMw
        self.browser = AwBrowser.singleton(ankiMw, cfg.getInitialWindowSize())
        self._noSelectionHandler = NoSelectionController(ankiMw)
        self._providerSelection = ProviderSelectionController()

    @exceptionHandler
    def _repeatProviderOrShowMenu(self, webView):
        query = self._getQueryValue(webView)
        if not query:
            return
        self.openInBrowser(query)

    def _filterQueryValue(self, query: str):
        "Remove words defined on filteredWords from web"

        filteredWords = cfg.getConfig().filteredWords
        if not filteredWords:
            return query
        querywords = query.split()
        resultwords = [word for word in querywords if word.lower() not in filteredWords]
        return ' '.join(resultwords)

    def _getQueryValue(self, input):
        raise Exception('Must be overriden')

    def prepareNoSelectionDialog(self, note):
        fieldList = note.model()['flds']
        fieldsNames = {ind: val for ind, val in enumerate(map(lambda i: i['name'], fieldList))}
        self._noSelectionHandler.setFields(fieldsNames)
        self._noSelectionHandler.handle(self.handleNoSelectionResult)
        return None

    def openInBrowser(self, query):
        """
            Setup enviroment for web browser and invoke it
        """

        Feedback.log('OpenInBrowser: {}'.format(self._currentNote))
        websiteList = self.getCurrentSearch()

        if cfg.getConfig().useSystemBrowser:
            for wl in websiteList:
                target = self.browser.formatTargetURL(wl, query)
                BaseController.openExternalLink(target)
            return
        
        self.beforeOpenBrowser()
        self.browser.open(websiteList, query, True, True)

    def beforeOpenBrowser(self):
        raise Exception('Must be overriden')

    @staticmethod
    def openExternalLink(target):
        raise Exception('Must be overriden')

    def getCurrentSearch(self) -> List[str]:
        raise Exception('Must be overriden')

    def handleNoSelectionResult(self, resultValue: NoSelectionResult):
        raise Exception('Must be overriden')
