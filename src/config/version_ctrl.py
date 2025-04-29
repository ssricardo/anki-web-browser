import os
import time

from PyQt6.QtCore import QTimer
from aqt import mw

from .. import CWD, VERSION
from ..browser_window import WebBrowserWindow

version_path = os.path.join(CWD, "version.txt")


def _create_update_version():
    with open(version_path, "w") as cfg_file:
        cfg_file.write(VERSION)

def check_version_new() -> bool:
    if not os.path.exists(version_path):
        _create_update_version()
        return True
    with open(version_path, "r") as cfg_file:
        last_version = cfg_file.read()
        if last_version.strip() != VERSION:
            _create_update_version()
            return True
    return False

def _get_welcome_page():
    with open(os.path.join(CWD, "resources", "welcome.html")) as f:
        return f.read()

def _do_show_welcome():
    time.sleep(3)
    WebBrowserWindow.singleton(mw, (600, 450)).show_welcome(_get_welcome_page())

def show_welcome():
    QTimer.singleShot(2500, _do_show_welcome)