# -*- coding: utf-8 -*-
# Interface between Anki's Editor and this addon's components
# This files is part of anki-web-browser addon
# @author ricardo saturnino
# ------------------------------------------------

# ---------------------------------- Editor Control -----------------------------------
# ---------------------------------- ================ ---------------------------------

import json
from typing import List, Optional

from aqt import gui_hooks
from aqt.editor import Editor
from aqt import mw
from aqt.qt import *

from .base_controller import BaseController
from .browser_context_menu import DataImportListener
from .config.main import config_service as cfg
from .core import Feedback
from .no_selection import NoSelectionResult


def __assert_consistent_state(editor):
    # if editor_controller is None or editor_controller.current_editor != editor:
    #     raise Exception("Unexpected component state. Controller isnt initialized or has stale reference")
    pass

def on_editor_ctx_menu_shown(editor_webview, menu):
    """
    Wrapper to the real context menu handler on the editor;
    Also holds a reference to the editor
    """
    __assert_consistent_state(editor_webview.editor)
    editor_controller.createEditorMenu(menu)


def setup_shortcuts(scuts: list, editor):
    __assert_consistent_state(editor)
    scuts.append((cfg.getConfig().menuShortcut, editor_controller.show_browser_menu))
    scuts.append((cfg.getConfig().repeatShortcut, editor_controller.repeat_provider_or_show_menu))

def delegate_node_loaded(editor: Editor):
    __assert_consistent_state(editor)
    editor_controller.handle_note_loaded()

def setup_editor_bindings():
    gui_hooks.editor_will_show_context_menu.append(on_editor_ctx_menu_shown)
    gui_hooks.editor_did_init_shortcuts.append(setup_shortcuts)
    gui_hooks.editor_did_load_note.append(delegate_node_loaded)

def set_new_editor(editor: Editor):
    editor_controller.setup_view(editor.parentWindow)
    editor_controller.current_editor = editor


# noinspection PyPep8Naming
class EditorController(BaseController, DataImportListener):
    current_editor = None
    _curSearch: List[str] = None

    def init_configurable_components(self):
        super().init_configurable_components()
        self._result_handler.create_image_from_url = lambda url: self.current_editor.urlToLink(url)

    def getCurrentSearch(self) -> List[str]:
        return self._curSearch

    # ------------------------ Anki interface ------------------

    def handle_note_loaded(self):
        """Listens when the current showed card is changed.
        Send msg to browser to cleanup its state"""

        Feedback.log("loadNote")

        if not self.browser:
            return

        if self._currentNote == self.current_editor.note:
            return

        self._currentNote = self.current_editor.note
        self.browser.clearContext()
        self.update_fields_from_note()
        if not cfg.getConfig().keepBrowserOpened:
            self.browser.close()

    # ------------------------ Addon operation -------------------------

    def show_browser_menu(self, parent=None):
        if not parent:
            parent = self.current_editor
        if not isinstance(parent, QWidget):
            if parent.web:
                parent = parent.web
            else:
                parent = mw.web

        self.createEditorMenu(parent)

    def repeat_provider_or_show_menu(self):
        webView = self.current_editor.web
        if not self._curSearch:
            return self.createEditorMenu(webView)

        super()._repeat_provider_or_show_menu_for_view(webView)

    def createEditorMenu(self, parent):
        """Delegate the menu creation and work related to providers"""
        return self._providerSelection.showCustomMenu(parent, self.handleProviderSelection)

    def handleProviderSelection(self, resultList: list):
        if not self.current_editor:
            raise Exception(
                "Illegal state found. It was not possible to recover the reference to Anki editor"
            )
        webview = self.current_editor.web
        query = self._getQueryValue(webview)
        self._curSearch = resultList
        if not query:
            return
        Feedback.log("Query: %s" % query)
        self._currentNote = self.current_editor.note
        self.openInBrowser(query)

    def handleNoSelectionResult(self, resultValue: NoSelectionResult):
        if not resultValue or resultValue.resultType in (
            NoSelectionResult.NO_RESULT,
            NoSelectionResult.SELECTION_NEEDED,
        ):
            Feedback.showInfo("No value selected")
            return
        value = resultValue.value
        if resultValue.resultType == NoSelectionResult.USE_FIELD:
            self.current_editor.currentField = resultValue.value  # fieldIndex
            value = self._currentNote.fields[resultValue.value]
            value = self._filterQueryValue(value)
            Feedback.log("USE_FIELD {}: {}".format(resultValue.value, value))

        return self.openInBrowser(value)

    def handle_selection(self, field: int, value: any, isUrl=False):
        imported_content = self._result_handler.handle_selection(value, isUrl)
        if imported_content is None:
            Feedback.log("No content was imported")
            return
        editor = self.current_editor

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

editor_controller = EditorController()