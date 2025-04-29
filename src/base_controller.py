# -*- coding: utf-8 -*-
# ---------------------------------- ================ ---------------------------------
# ---------------------------------- Base Controller -----------------------------------
# ---------------------------------- ================ ---------------------------------
from abc import ABC, abstractmethod
from typing import List

from .browser_dock import WebBrowserDock
from .browser_window import WebBrowserWindow
from .config.main import config_service as cfg
from .core import Feedback
from .exception_handler import exceptionHandler
from .no_selection import NoSelectionController, NoSelectionResult
from .provider_selection import ProviderSelectionController
from .result_handler import ResultHandler


class BaseController(ABC):
    """ Concentrates common operations between both concrete controllers """

    browser = None
    _currentNote = None
    _result_handler: ResultHandler
    _noSelectionHandler: NoSelectionController = None
    _providerSelection: ProviderSelectionController = None

    def init_configurable_components(self):
        self._providerSelection = ProviderSelectionController()
        self._result_handler = ResultHandler()

    def setup_view(self, parent):
        if cfg.getConfig().useAsDock:
            self.browser = WebBrowserDock.new(parent, cfg.getInitialWindowSize())
        else:
            self.browser = WebBrowserWindow.singleton(parent, cfg.getInitialWindowSize())

        self._noSelectionHandler = NoSelectionController(parent)


    @exceptionHandler
    def _repeat_provider_or_show_menu_for_view(self, webView):
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

    def _getQueryValue(self, webview):
        if webview.hasSelection():
            return self._filterQueryValue(webview.selectedText())

        if self._noSelectionHandler.isRepeatOption():
            noselection_result = self._noSelectionHandler.getValue()
            if noselection_result.resultType == NoSelectionResult.USE_FIELD:
                if noselection_result.value < len(self._currentNote.fields):
                    Feedback.log("USE_FIELD {}: {}".format(noselection_result.value, self._currentNote.fields[noselection_result.value], ))
                    return self._filterQueryValue(self._currentNote.fields[noselection_result.value])

        return self.prepareNoSelectionDialog()

    def prepareNoSelectionDialog(self):
        note = self._currentNote
        if note is None:
            Feedback.showInfo('No context for search was found. Ignoring Web-Browser call')
            return

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
                target = self.browser.format_target_url(wl, query)
                BaseController.openExternalLink(target)
            return
        
        self.beforeOpenBrowser()
        self.browser.open(websiteList, query, True, True)

    @abstractmethod
    def beforeOpenBrowser(self):
        pass

    @staticmethod
    def openExternalLink(target):
        raise Exception('Must be overriden')

    @abstractmethod
    def getCurrentSearch(self) -> List[str]:
        pass

    @abstractmethod
    def handleNoSelectionResult(self, resultValue: NoSelectionResult):
        pass