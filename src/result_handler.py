# -*- coding: utf-8 -*-
# Interface passed to browser, for receiving its result

# This files is part of anki-web-browser addon
# @author ricardo saturnino
# ------------------------------------------------

import re
import base64
from datetime import datetime
from random import randint
from typing import Optional

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QImage


from .core import Feedback
from .config.main import config_service as cfgService


class ResultHandler:
    """
        Handles actions from the browser, that is, the assignment from the browser to Anki
    """

    _base64Prefix = re.compile(r"(data:image/((\w){3,4});base64,)(.+)")

    def __init__(self) -> None:
        self._config = cfgService.getConfig()

    @classmethod
    def get_media_location(cls):
        raise NotImplementedError("Method must be replaced")

    def create_image_from_url(self, url: str):
        raise NotImplementedError("Method must be replaced")

    def handle_selection(self, value, isUrl=False) -> Optional[str]:
        """
            Callback from the web browser.
            Invoked when there is a selection coming from the browser. It needs to be delivered to a given field
        """

        if isUrl:
            return self._handle_url_selection(value)
        else:
            return self._handle_text_selection(value)

    def _handle_url_selection(self, value: QUrl) -> Optional[str]:
        """
        Imports an image from the link 'value' to the collection.
        Adds this new img tag to the given field in the current note"""

        url = value.toString() if value else ''
        Feedback.log("Selected from browser: {} || ".format(url))

        img_reference = self._handle_base64_image(url) if self._is_base64(url) \
            else self.create_image_from_url(url)

        if (not img_reference) or not img_reference.startswith('<img'):
            Feedback.showWarn(
                'URL invalid! Only URLs with references to image files are supported (ex: http://images.com/any.jpg, any.png)')
            Feedback.log(img_reference)
            return None

        Feedback.log('handleUrlSelection.imgReference: ' + img_reference)

        self._process_pos_import(img_reference)
        result = "<div class='webb_insert'>{}</div>".format(img_reference)
        return result

    def _is_base64(self, value: str):
        return self._base64Prefix.match(value) is not None

    def _handle_base64_image(self, url: str):
        rgMatch = self._base64Prefix.match(url)
        byteStr = rgMatch.group(4)

        img_bytes = base64.b64decode(byteStr)
        extension = rgMatch.group(2)
        name = datetime.now().strftime('%y-%m-%d-%H-%M-%S') + str(randint(1, 300)) + ('.%s' % extension)

        with open(ResultHandler.get_media_location() + '/' + name, 'wb') as imageFile:
            Feedback.log("name: " + imageFile.name)
            imageFile.write(img_bytes)

        return ResultHandler._create_img_tag(name)

    @staticmethod
    def _create_img_tag(name: str):
        return '<img src="%s" />' % name

    def _process_pos_import(self, img_reference: str):
        img_tag_match = re.compile('<img src="(.+)"( )*/?>').match(img_reference)

        if not img_tag_match:
            Feedback.showWarn("It was not possible to import given image")
            return

        file_name = img_tag_match.group(1)
        file_path = "%s/%s" % (ResultHandler.get_media_location(), file_name)

        im = QImage(file_path)
        original_image = im
        Feedback.log('Image dim: %d:%d' % (im.width(), im.height()))

        if self._config.imgMaxWidth and im.width() > self._config.imgMaxWidth:
            im = im.scaledToWidth(self._config.imgMaxWidth)
        if self._config.imgMaxHeight and im.height() > self._config.imgMaxHeight:
            im = im.scaledToHeight(self._config.imgMaxHeight)
        if im is not original_image:
            im.save(file_path)
            Feedback.log('New dim: %d:%d' % (im.width(), im.height()))

    def _handle_text_selection(self, value) -> Optional[str]:
        """Adds the selected value to the given field of the current note"""

        new_value = "<div class='webb_insert'>{}</div>".format(value)
        return new_value
