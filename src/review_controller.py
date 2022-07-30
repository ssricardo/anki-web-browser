# -*- coding: utf-8 -*-
# Interface between Anki Review and this addon

# This files is part of anki-web-browser addon
# @author ricardo saturnino
# ------------------------------------------------
from typing import List

from anki.hooks import addHook
from aqt.qt import QAction
from aqt.reviewer import Reviewer

from .base_controller import BaseController
from .browser import AwBrowser
from .config.main import service as cfg
from .core import Feedback
from .exception_handler import exceptionHandler
from .no_selection import NoSelectionResult


class ReviewController(BaseController):
    """
        The mediator/adapter between Anki with its components and this addon specific API
    """

    browser = None
    _curSearch: List[str] = None

    def __init__(self, ankiMw):
        super(ReviewController, self).__init__(ankiMw)
        self.browser = AwBrowser.singleton(ankiMw.web, cfg.getInitialWindowSize())
        self.browser.setResultHandler(None)

    def setupBindings(self):
        addHook('AnkiWebView.contextMenuEvent', self.onReviewerHandle)

        Reviewer.nextCard = self.wrapOnCardShift(Reviewer.nextCard)
        Reviewer._shortcutKeys = self.wrap_shortcutKeys(Reviewer._shortcutKeys)

        # Add web to menu
        action = QAction("Anki-Web-Browser Config", self._ankiMw)
        action.triggered.connect(self.openConfig)
        self._ankiMw.form.menuTools.addAction(action)

    def openConfig(self):
        from .config.config_ctrl import ConfigController
        cc = ConfigController(self._ankiMw)
        cc.open()

    def wrapOnCardShift(self, originalFunction):
        """
        Listens when the current showed card is changed, in Reviewer.
        Send msg to browser to cleanup its state"""

        ref = self

        def wrapped(self, focusTo=None):
            Feedback.log('Browser - CardShift')

            originalResult = None
            if focusTo:
                originalResult = originalFunction(self, focusTo)
            else:
                originalResult = originalFunction(self)

            if not ref.browser or cfg.getConfig().useSystemBrowser:
                return originalFunction

            ref.browser.clearContext()
            if not cfg.getConfig().keepBrowserOpened:
                ref.browser.close()

            if ref._ankiMw.reviewer and ref._ankiMw.reviewer.card:
                ref._currentNote = ref._ankiMw.reviewer.card.note()

            return originalResult

        return wrapped

    def wrap_shortcutKeys(self, fn):
        ref = self

        def customShortcut(self):
            sList = fn(self)
            sList.append((cfg.getConfig().menuShortcut,
                          lambda: ref.createReviewerMenu(
                              ref._ankiMw.web, ref._ankiMw.web)))

            sList.append((cfg.getConfig().repeatShortcut, ref._repeatProviderOrShowMenu))
            return sList

        return customShortcut

    # --------------------------------------------------------------------------

    @exceptionHandler
    def _repeatProviderOrShowMenu(self):
        if not self._curSearch:
            return self.createReviewerMenu(self._ankiMw.web, self._ankiMw.web)

        webView = self._ankiMw.web
        super()._repeatProviderOrShowMenu(webView)

    def handleProviderSelection(self, resultList: List[str]):
        Feedback.log('Handle provider selection')
        webview = self._ankiMw.web
        query = self._getQueryValue(webview)
        self._curSearch = resultList
        if not query:
            return
        Feedback.log('Query: %s' % query)
        self.openInBrowser(query)

    @exceptionHandler
    def createReviewerMenu(self, webView, menu):
        """Handles context menu event on Reviewer"""

        self._providerSelection.showCustomMenu(menu, self.handleProviderSelection)

    # TODO: move parts to superclass / adapt
    def _getQueryValue(self, webview):
        Feedback.log('getQueryValue', webview, self._currentNote)
        if webview.hasSelection():
            return self._filterQueryValue(webview.selectedText())

        if self._noSelectionHandler.isRepeatOption():
            noSelectionResult = self._noSelectionHandler.getValue()
            if noSelectionResult.resultType == NoSelectionResult.USE_FIELD:
                if noSelectionResult.value < len(self._currentNote.fields):
                    Feedback.log('USE_FIELD {}: {}'.format(noSelectionResult.value,
                                                           self._currentNote.fields[noSelectionResult.value]))
                    return self._filterQueryValue(self._currentNote.fields[noSelectionResult.value])

        return self.prepareNoSelectionDialog(self._currentNote)

    def handleNoSelectionResult(self, resultValue: NoSelectionResult):
        if not resultValue or \
                resultValue.resultType in (NoSelectionResult.NO_RESULT, NoSelectionResult.SELECTION_NEEDED):
            Feedback.showInfo('No value selected')
            return
        value = resultValue.value
        if resultValue.resultType == NoSelectionResult.USE_FIELD:
            value = self._currentNote.fields[resultValue.value]
            value = self._filterQueryValue(value)
            Feedback.log('USE_FIELD {}: {}'.format(resultValue.value, value))

        return self.openInBrowser(value)

    def getCurrentSearch(self) -> List[str]:
        return self._curSearch

    # ---------------------------------- Events listeners ---------------------------------

    def onReviewerHandle(self, webView, menu):
        """
            Wrapper to the real context menu handler on the reviewer;
        """

        if self._ankiMw.reviewer and self._ankiMw.reviewer.card:
            self.createReviewerMenu(webView, menu)

    def beforeOpenBrowser(self):
        self.browser.setFields(None)  # clear fields
        self.browser.setInfoList(['No action available on Reviewer mode'])
        self.browser.setResultHandler(None)
