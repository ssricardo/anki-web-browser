# -*- coding: utf-8 -*-
# Interface between Anki Review and this addon
import html
import urllib
# This files is part of anki-web-browser addon
# @author ricardo saturnino
# ------------------------------------------------
from typing import List, Optional, Iterable

from aqt import gui_hooks, mw
from aqt.qt import QAction
from aqt.reviewer import Reviewer
from aqt.sound import av_player

from .base_controller import BaseController
from .browser import AwBrowser
from .browser_context_menu import DataImportListener
from .config.main import service as cfg
from .core import Feedback
from .exception_handler import exceptionHandler
from .no_selection import NoSelectionResult


class ReviewController(BaseController, DataImportListener):
    """
        The mediator/adapter between Anki with its components and this addon specific API
    """

    browser = None
    _curSearch: List[str] = None
    _last_card_id: Optional[int] = None

    def __init__(self, anki_mw):
        super(ReviewController, self).__init__(anki_mw)
        # self.browser = AwBrowser.singleton(anki_mw.web, mw.pm.profile.name, cfg.getInitialWindowSize())
        self.browser.set_import_listener(None)

    def setup_bindings(self):
        gui_hooks.webview_will_show_context_menu.append(self.onReviewerHandle)

        gui_hooks.card_will_show.append(self.load_card)
        Reviewer._shortcutKeys = self.wrap_shortcutKeys(Reviewer._shortcutKeys)

        # Add web to menu
        action = QAction("Anki-Web-Browser Config", self._ankiMw)
        action.triggered.connect(self.open_config)
        self._ankiMw.form.menuTools.addAction(action)
        self._result_handler.create_image_from_url = ReviewController._import_urlToLink

    @staticmethod
    def _import_urlToLink(url):
        return ""

    def open_config(self):
        from .config.config_ctrl import ConfigController
        cc = ConfigController(self._ankiMw)
        cc.open()

    def wrap_shortcutKeys(self, fn):
        ref = self

        def customShortcut(self):
            sList = fn(self)
            sList.append((cfg.getConfig().menuShortcut,
                          lambda: ref.createReviewerMenu(
                              ref._ankiMw.web, ref._ankiMw.web)))

            sList.append((cfg.getConfig().repeatShortcut, ref._repeat_provider_or_show_menu))
            return sList

        return customShortcut

    # --------------------------------------------------------------------------

    @exceptionHandler
    def _repeat_provider_or_show_menu(self):
        if not self._curSearch:
            return self.createReviewerMenu(self._ankiMw.web, self._ankiMw.web)

        webView = self._ankiMw.web
        super()._repeat_provider_or_show_menu_for_view(webView)

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

        return self.prepareNoSelectionDialog()

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

    def load_card(self, text: str, card, kind: str) -> str:
        Feedback.log('WebBrowser - CardShift')
        if not self.browser or cfg.getConfig().useSystemBrowser:
            return text

        if self._last_card_id != card.id:
            self.browser.clearContext()
        if not cfg.getConfig().keepBrowserOpened:
            self.browser.close()

        self._currentNote = card.note()
        self.update_fields_from_note()
        self._last_card_id = card.id

        return text

    def onReviewerHandle(self, webView, menu):
        """
            Wrapper to the real context menu handler on the reviewer;
        """

        if self._ankiMw.reviewer and self._ankiMw.reviewer.card:
            self.createReviewerMenu(webView, menu)

    def handle_selection(self, field_index: int, value: any, isUrl=False):
        if isUrl:
            Feedback.showWarn("Importing media (URLs) is not supported in Review mode")
            return

        imported_content = self._result_handler.handle_selection(value, isUrl)
        if imported_content is None:
            return

        note = self._currentNote
        note.fields[field_index] += imported_content
        mw.col.update_note(note)
        mw.reviewer._redraw_current_card()
        Feedback.showInfo("Anki Web Browser: Note was edited during review. New content is imported.")

    def beforeOpenBrowser(self):
        self.browser.setFields(None)  # clear fields
        self.browser.setInfoList(['No action available on Reviewer mode'])
        self.browser.set_import_listener(self)

        self.update_fields_from_note()

    def update_fields_from_note(self):
        if not self._currentNote:
            return
        note = self._currentNote
        fieldList = note.model()["flds"]
        fieldsNames = {
            ind: val for ind, val in enumerate(map(lambda i: i["name"], fieldList))
        }
        self.browser.setFields(fieldsNames)