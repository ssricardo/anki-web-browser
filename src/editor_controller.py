# -*- coding: utf-8 -*-
# Interface between Anki's Editor and this addon's components
import json
# This files is part of anki-web-browser addon
# @author ricardo saturnino
# ------------------------------------------------

# ---------------------------------- Editor Control -----------------------------------
# ---------------------------------- ================ ---------------------------------

from typing import List

from aqt import gui_hooks
from aqt.editor import Editor
from aqt import mw
from aqt.qt import *

from .base_controller import BaseController
from .browser_context_menu import DataImportListener
from .config.main import service as cfg
from .core import Feedback
from .no_selection import NoSelectionResult


# noinspection PyPep8Naming
class EditorController(BaseController, DataImportListener):
    _editorReference = None
    _curSearch: List[str] = None

    def __init__(self, ankiMw):
        super(EditorController, self).__init__(ankiMw)

        self.setupBindings()

    def getCurrentSearch(self) -> List[str]:
        return self._curSearch

    # ------------------------ Anki interface ------------------

    def setupBindings(self):
        gui_hooks.editor_will_show_context_menu.append(self.onEditorHandle)
        gui_hooks.editor_did_init_shortcuts.append(self.setupShortcuts)
        gui_hooks.editor_did_load_note.append(self.handle_note_loaded)

        self._result_handler.create_image_from_url = lambda url: self._editorReference.urlToLink(url)

    def handle_note_loaded(self, editor: Editor):
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
        self.update_fields_from_note()
        if not cfg.getConfig().keepBrowserOpened:
            self.browser.close()

    def onEditorHandle(self, editor_webview, menu):
        """
        Wrapper to the real context menu handler on the editor;
        Also holds a reference to the editor
        """

        self._editorReference = editor_webview.editor
        self.createEditorMenu(menu, self.handleProviderSelection)

    def setupShortcuts(self, scuts: list, editor):
        self._editorReference = editor
        scuts.append((cfg.getConfig().menuShortcut, self._showBrowserMenu))
        scuts.append((cfg.getConfig().repeatShortcut, self._repeat_provider_or_show_menu))

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

    def _repeat_provider_or_show_menu(self):
        webView = self._editorReference.web
        if not self._curSearch:
            return self.createEditorMenu(webView, self.handleProviderSelection)

        super()._repeat_provider_or_show_menu_for_view(webView)

    def createEditorMenu(self, parent, menuFn):
        """Delegate the menu creation and work related to providers"""
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

        self._currentNote = webview.editor.note
        return self.prepareNoSelectionDialog()

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

    def handle_selection(self, field: int, value: any, isUrl=False):
        imported_content = self._result_handler.handle_selection(value, isUrl)
        if imported_content is None:
            Feedback.log("No content was imported")
            return
        editor = self._editorReference

        editor.currentField = field

        editor.web.eval("focusField(%d);" % field)
        imported_content = "<br/>" + imported_content # need to keep extra <br>, otherwise div is striped
        editor.web.eval("setFormat('inserthtml', %s);" % json.dumps(imported_content))
        Feedback.showInfo("Anki Web Browser: Content imported to note")


    # ---------------------------------- --------------- ---------------------------------

    def beforeOpenBrowser(self):
        self.browser.set_import_listener(self)
        self.browser.setInfoList(
            ["No action available", "Required: Text selected or link to image"]
        )

    def update_fields_from_note(self):
        if not self._currentNote:
            return
        note = self._currentNote
        fieldList = note.model()["flds"]
        fieldsNames = {
            ind: val for ind, val in enumerate(map(lambda i: i["name"], fieldList))
        }
        self.browser.setFields(fieldsNames)