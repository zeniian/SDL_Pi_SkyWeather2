import logging
import sys

from systemd import journal


def Logger(name, debug=False):
    # Setup logger
    logger = logging.getLogger(name)
    logger.handlers = []
    logger.propagate = False
    logger.addHandler(logging.NullHandler())

    # Add journald handler
    journal_formatter = logging.Formatter(name + ': %(levelname)s %(message)s') 
    journal_handler = journal.JournalHandler()
    logger.setLevel(logging.INFO)
    journal_handler.setFormatter(journal_formatter)
    logger.addHandler(journal_handler)

    if debug:
      # Add stdout debug handler
      stdout_handler = logging.StreamHandler(sys.stdout)
      logger.setLevel(logging.DEBUG)
      stdout_formatter = logging.Formatter('DEBUG ' + name + ': %(levelname)s %(message)s')
      stdout_handler.setFormatter(stdout_formatter)
      logger.addHandler(stdout_handler)
      logging.info('DEBUG mode')

    return logger