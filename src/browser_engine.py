# -*- coding: utf-8 -*-

# --------------------------------------------------
# Handles Web engine itself
# --------------------------------------------------

from aqt.qt import *

from . import CWD
from .core import Feedback

from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor

LOAD_PAGE = """
    <html>
        <style type="text/css">
            body {
                margin-top: 30px;
                background-color: transparent;
                color: #F5F5F5;
            }            
        </style>
        <body>   
            <h3>New Page...</h3>
        </body>   
    </html>
"""


# noinspection PyPep8Naming
class AwWebEngine(QWebEngineView):

    isLoading = False
    DARK_READER = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_reader_loaded = False
        self.create()
        self.interceptor = WebRequestInterceptor()
        self.page().profile().setUrlRequestInterceptor(self.interceptor)

    @classmethod
    def enableDarkReader(clz):
        if not clz.DARK_READER:
            with open(os.path.join(CWD, "resources", "darkreader.js"), "r") as ngJS:
                clz.DARK_READER = ngJS.read()
                Feedback.log("DarkReader loaded")

    def create(self):

        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
        )
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ErrorPageEnabled, True
        )
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True
        )

        self.page().loadStarted.connect(self.onStartLoading)
        self.page().loadFinished.connect(self.onLoadFinish)
        self.page().loadProgress.connect(self.onLoadProgress)

        return self

    def preLoadPage(self):
        print("Preload")
        self.setHtml(LOAD_PAGE, QUrl("about:blank"))

    # ======   Listeners ======

    def onStartLoading(self):
        self.isLoading = True
        self.dark_reader_loaded = False

    def onLoadProgress(self, progress: int):
        if progress >= 50:
            self.activate_darkreader_if_needed()

    def onLoadFinish(self, result):
        self.isLoading = False
        if not result:
            Feedback.log("No result on loading page! ")

        self.activate_darkreader_if_needed()

    def activate_darkreader_if_needed(self):
        if not AwWebEngine.DARK_READER or self.dark_reader_loaded:
            return

        self.dark_reader_loaded = True
        self.page().runJavaScript(AwWebEngine.DARK_READER)
        self.page().runJavaScript("DarkReader.setFetchMethod(window.fetch);")

        self.page().runJavaScript(
            """
                DarkReader.enable({
                    brightness: 105,
                    contrast: 90,
                    sepia: 10,
                    grayscale: 0,
                    mode: 1
                });

                console.log('Dark reader was activated');
            """
        )


class WebRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)

    def interceptRequest(self, info):
        info.setHttpHeader(b"Access-Control-Allow-Origin", b"*")
