# -*- coding: utf-8 -*-
# Interface between Anki's Editor and this addon's components

# This files is part of anki-web-browser addon
# @author ricardo saturnino
# ------------------------------------------------

# ---------------------------------- Editor Control -----------------------------------
# ---------------------------------- ================ ---------------------------------

import os
from typing import List

from anki.hooks import addHook
from aqt.editor import Editor
from aqt import mw
from aqt.qt import *

from .base_controller import BaseController
from .config.main import service as cfg
from .core import Feedback
from .no_selection import NoSelectionResult
from .result_handler import ResultHandler


# noinspection PyPep8Naming
class EditorController(BaseController):
    _editorReference = None
    _curSearch: List[str] = None

    def __init__(self, ankiMw):
        super(EditorController, self).__init__(ankiMw)

        self.setupBindings()

    def getCurrentSearch(self) -> List[str]:
        return self._curSearch

    # ------------------------ Anki interface ------------------

    def setupBindings(self):
        addHook("EditorWebView.contextMenuEvent", self.onEditorHandle)
        addHook("setupEditorShortcuts", self.setupShortcuts)
        addHook("loadNote", self.newLoadNote)

        ResultHandler.create_image_from_url = lambda url: self._editorReference.urlToLink(url)
        ResultHandler.get_media_location = lambda: os.path.join(mw.pm.profileFolder(), "collection.media")

# Not
# a
# directory: '/home/ricardo/.local/share/Anki2/Ricardo/collection.anki2/21-12-14-22-45-44175.png'

    def newLoadNote(self, editor: Editor):
        """Listens when the current showed card is changed.
        Send msg to browser to cleanup its state"""

        Feedback.log("loadNote")

        self._editorReference = editor
        if not self.browser:
            return

        if self._currentNote == self._editorReference.note:
            return

        self._currentNote = self._editorReference.note
        self.browser.clearContext()
        if not cfg.getConfig().keepBrowserOpened:
            self.browser.close()

    def onEditorHandle(self, webView, menu):
        """
        Wrapper to the real context menu handler on the editor;
        Also holds a reference to the editor
        """

        self._editorReference = webView.editor
        self.createEditorMenu(menu, self.handleProviderSelection)

    def setupShortcuts(self, scuts: list, editor):
        self._editorReference = editor
        scuts.append((cfg.getConfig().menuShortcut, self._showBrowserMenu))
        scuts.append((cfg.getConfig().repeatShortcut, self._repeatProviderOrShowMenu))

    # ------------------------ Addon operation -------------------------

    def _showBrowserMenu(self, parent=None):
        if not parent:
            parent = self._editorReference
        if not isinstance(parent, QWidget):
            if parent.web:
                parent = parent.web
            else:
                parent = self._ankiMw.web

        self.createEditorMenu(parent, self.handleProviderSelection)

    def _repeatProviderOrShowMenu(self):
        webView = self._editorReference.web
        if not self._curSearch:
            return self.createEditorMenu(webView, self.handleProviderSelection)

        super()._repeatProviderOrShowMenu(webView)

    def createEditorMenu(self, parent, menuFn):
        """Deletegate the menu creation and work related to providers"""

        return self._providerSelection.showCustomMenu(parent, menuFn)

    def handleProviderSelection(self, resultList: list):
        if not self._editorReference:
            raise Exception(
                "Illegal state found. It was not possible to recover the reference to Anki editor"
            )
        webview = self._editorReference.web
        query = self._getQueryValue(webview)
        self._curSearch = resultList
        if not query:
            return
        Feedback.log("Query: %s" % query)
        self._currentNote = self._editorReference.note
        self.openInBrowser(query)

    def _getQueryValue(self, webview):
        if webview.hasSelection():
            return self._filterQueryValue(webview.selectedText())

        if self._noSelectionHandler.isRepeatOption():
            noSelectionResult = self._noSelectionHandler.getValue()
            if noSelectionResult.resultType == NoSelectionResult.USE_FIELD:
                self._editorReference.currentField = noSelectionResult.value
                if noSelectionResult.value < len(self._currentNote.fields):
                    Feedback.log(
                        "USE_FIELD {}: {}".format(
                            noSelectionResult.value,
                            self._currentNote.fields[noSelectionResult.value],
                        )
                    )
                    return self._filterQueryValue(
                        self._currentNote.fields[noSelectionResult.value]
                    )

        note = webview.editor.note
        return self.prepareNoSelectionDialog(note)

    def handleNoSelectionResult(self, resultValue: NoSelectionResult):
        if not resultValue or resultValue.resultType in (
            NoSelectionResult.NO_RESULT,
            NoSelectionResult.SELECTION_NEEDED,
        ):
            Feedback.showInfo("No value selected")
            return
        value = resultValue.value
        if resultValue.resultType == NoSelectionResult.USE_FIELD:
            self._editorReference.currentField = resultValue.value  # fieldIndex
            value = self._currentNote.fields[resultValue.value]
            value = self._filterQueryValue(value)
            Feedback.log("USE_FIELD {}: {}".format(resultValue.value, value))

        return self.openInBrowser(value)

    # ---------------------------------- --------------- ---------------------------------
    def beforeOpenBrowser(self):
        self.browser.setResultHandler(ResultHandler(self._editorReference, self._currentNote))
        note = self._currentNote
        fieldList = note.model()["flds"]
        fieldsNames = {
            ind: val for ind, val in enumerate(map(lambda i: i["name"], fieldList))
        }
        self.browser.setInfoList(
            ["No action available", "Required: Text selected or link to image"]
        )
        self.browser.setFields(fieldsNames)
