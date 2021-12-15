# -*- coding: utf-8 -*-
# Interface passed to browser, for receiving its result

# This files is part of anki-web-browser addon
# @author ricardo saturnino
# ------------------------------------------------

import re
import json
import base64
from datetime import datetime
from random import randint
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QImage

from .core import Feedback
from .config.main import service as cfgService


class ResultHandler:
    """
        Handles actions from the browser, that is, the assignment from the browser to Anki
    """

    _editorReference: any
    _currentNote: any
    _base64Prefix = re.compile(r"(data:image/((\w){3,4});base64,)(.+)")

    def __init__(self, ankiEditor, currentNote) -> None:
        super().__init__()
        self._editorReference = ankiEditor
        self._currentNote = currentNote
        self._config = cfgService.getConfig()

    @classmethod
    def get_media_location(cls):
        raise NotImplementedError("Method must be replaced")

    @staticmethod
    def create_image_from_url(url: str):
        raise NotImplementedError("Method must be replaced")
        # self._editorReference.urlToLink(url)

    def handle_selection(self, field_index, value, isUrl=False):
        """
            Callback from the web browser.
            Invoked when there is a selection coming from the browser. It needs to be delivered to a given field
        """

        if self._editorReference and self._currentNote != self._editorReference.note:
            Feedback.showWarn("""Inconsistent state found. 
            The current note is not the same as the Web Browser reference. 
            Try closing and re-opening the browser""")
            return

        self._editorReference.currentField = field_index

        if isUrl:
            self._handle_url_selection(field_index, value)
        else:
            self._handle_text_selection(field_index, value)

    def _handle_url_selection(self, fieldIndex: int, value: QUrl):
        """
        Imports an image from the link 'value' to the collection.
        Adds this new img tag to the given field in the current note"""

        url = value.toString() if value else ''
        Feedback.log("Selected from browser: {} || ".format(url))

        imgReference = self._handle_base64_image(url) if self._is_base64(url) \
            else ResultHandler.create_image_from_url(url)

        if (not imgReference) or not imgReference.startswith('<img'):
            Feedback.showWarn(
                'URL invalid! Only URLs with references to image files are supported (ex: http://images.com/any.jpg,  ' +
                'any.png)')
            return

        Feedback.log('handleUrlSelection.imgReference: ' + imgReference)

        self._process_pos_import(imgReference)
        self._editorReference.web.eval("focusField(%d);" % fieldIndex)
        self._editorReference.web.eval("setFormat('inserthtml', %s);" % json.dumps(imgReference))

    def _is_base64(self, value: str):
        return self._base64Prefix.match(value) is not None

    def _handle_base64_image(self, url: str):
        rgMatch = self._base64Prefix.match(url)
        byteStr = rgMatch.group(4)

        img_bytes = base64.b64decode(byteStr)
        extension = rgMatch.group(2)
        name = datetime.now().strftime('%y-%m-%d-%H-%M-%S') + str(randint(1, 300)) + ('.%s' % extension)

        with open(ResultHandler.get_media_location() + '/' + name, 'wb') as imageFile:
            print("name: " + imageFile.name)
            imageFile.write(img_bytes)

        return self._create_img_tag(name)

    @staticmethod
    def _create_img_tag(name: str):
        return '<img src="%s" />' % name

    def _process_pos_import(self, imgRef: str):
        imgTagMatch = re.compile('<img src="(.+)"( )*/?>').match(imgRef)

        if not imgTagMatch:
            Feedback.showWarn("It was not possible to import given image")
            return

        fileName = imgTagMatch.group(1)
        filePath = "%s/%s" % (ResultHandler.get_media_location(), fileName)

        im = QImage(filePath)
        originalImage = im
        Feedback.log('Image dim: %d:%d' % (im.width(), im.height()))

        if self._config.imgMaxWidth and im.width() > self._config.imgMaxWidth:
            im = im.scaledToWidth(self._config.imgMaxWidth)
        if self._config.imgMaxHeight and im.height() > self._config.imgMaxHeight:
            im = im.scaledToHeight(self._config.imgMaxHeight)
        if im is not originalImage:
            im.save(filePath)
            Feedback.log('New dim: %d:%d' % (im.width(), im.height()))

    def _handle_text_selection(self, fieldIndex, value):
        """Adds the selected value to the given field of the current note"""

        newValue = self._currentNote.fields[fieldIndex] + '\n ' + value
        self._currentNote.fields[fieldIndex] = newValue
        self._editorReference.setNote(self._currentNote)
