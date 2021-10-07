# -------------------------------------------------------------
# Module for anki-web-browser addon
# -------------------------------------------------------------

__version__ = "5.0"

import sys
import os

CWD = os.path.dirname(os.path.realpath(__file__))


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
        from .review_controller import run
        run()
except ImportError as ie:
    print(""" [WARNING] Anki-web-browser ::: It wasn\'t possible to resolve imports. 
        Probably anki was not found, duo to: Running In test mode !!! """)

    print(ie)
    # raise ie