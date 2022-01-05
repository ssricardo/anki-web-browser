# -*- coding: utf-8 -*-
# Plugin: anki-web-browser - Context menu for notes
# Responsible for adding options in the context menu on Anki notes
# Shows registered providers (websites) to search for the selected sentence
# --------------------------------------------
from typing import List

from aqt.qt import *

from .config.main import Provider, SearchGroup
from .config.main import service as cfgService
from .core import Label, Style


class ProviderSelectionController:
    _providerList = List[Provider]
    _groupList: List[SearchGroup]

    def __init__(self):
        self._providerList = cfgService.getConfig().providers
        self._groupList = cfgService.getConfig().groups

    def showCustomMenu(self, menuParent, menuFn):
        """Builds the addon entry in the context menu, adding options according to the providers"""

        if not menuFn:
            raise AttributeError("Callback Fn must be not null")

        if not menuParent:
            raise AttributeError("menuParent must be not null")

        submenu = QMenu(Label.CARD_MENU, menuParent)
        submenu.setStyleSheet(Style.MENU_STYLE)

        indexShortcut = 0
        grList = self._groupList
        for group in grList:
            providerList = list(map(self._getProviderUrl, group.providerList))

            indexShortcut += 1
            numShortcut = "(&" + str(indexShortcut) + ") " if indexShortcut < 10 else ""

            act = QAction(
                numShortcut + group.name,
                submenu,
                triggered=self._makeMenuAction(providerList, menuFn),
            )
            submenu.addAction(act)

        if grList:
            submenu.addSeparator()

        pList = self._providerList
        for prov in pList:
            indexShortcut += 1
            numShortcut = "(&" + str(indexShortcut) + ") " if indexShortcut < 10 else ""
            act = QAction(
                numShortcut + prov.name,
                submenu,
                triggered=self._makeMenuAction([prov.url], menuFn),
            )
            submenu.addAction(act)

        if not isinstance(menuParent, QMenu):
            submenu.popup(menuParent.mapToGlobal(menuParent.pos()))
        else:
            menuParent.addMenu(submenu)

    def _getProviderUrl(self, name: str) -> str:
        return next((p.url for p in self._providerList if p.name == name), "")

    def _makeMenuAction(self, valueList: list, menuCallback):
        """
        Creates correct action for the context menu selection. Otherwise, it would repeat only the last element
        """
        return lambda: menuCallback(valueList)


# -----------------------------------------------------------------------------
