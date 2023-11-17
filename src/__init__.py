# -------------------------------------------------------------
# Module for anki-web-browser addon

# Initial interface between Anki and this addon components

# This files is part of anki-web-browser addon
# @author ricardo saturnino
# -------------------------------------------------------------

__version__ = "7.1"

import sys
import os
from .config import main

CWD = os.path.dirname(os.path.realpath(__file__))

main.addon_home = lambda: CWD


def logToConsole(*args, **kargs):
    try:
        print(args, kargs)
    except Exception as e:
        print(e)

try:
    # Uncomment to produce more logs on console
    # from .core import Feedback
    # Feedback.log = logToConsole

    if not sys.argv.__contains__('-awb-test'):
        from .runner import run
        run()
except ImportError as ie:
    print(""" [WARNING] Anki-web-browser ::: It wasn\'t possible to resolve imports. 
        Probably anki was not found, duo to: Running In test mode !!! """)

    print(ie)
    # raise ie