"""
Sets up a basic logger for projects.
The file writing handler writes explicit date/time/loglevel/msg to debug.log.
The console handler just prints the msg to console.
"""

import datetime
import logging
import os

LOGDIR = 'logs/'


def setup_logger():
    if not os.path.exists(LOGDIR):
        os.mkdir(LOGDIR)

    # Setup logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # setup filename:
    dt = datetime.datetime
    file_stamp = 'session {}'.format(dt.now().strftime('%m-%d-%Y %H:%M:%S'))
    DEBUG_FILE = 'logs/{}.log'.format(file_stamp)

    # Setup file handlers
    debug_fh = logging.FileHandler(DEBUG_FILE)
    debug_fh.setLevel(logging.DEBUG)

    # Setup console stream handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)  # Only INFO or higher printers to console.

    # Setup formatting
    debug_fmt = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s',
                                  "%d-%m-%y %H:%M:%S")

    ch_fmt = logging.Formatter('%(message)s')

    debug_fh.setFormatter(debug_fmt)
    ch.setFormatter(ch_fmt)

    # Add handlers to logger
    logger.addHandler(debug_fh)
    logger.addHandler(ch)

    return logger
