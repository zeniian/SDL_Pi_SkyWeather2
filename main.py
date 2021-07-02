#!/usr/bin/python3

import signal
import sys
import time

import daemon
import lockfile
import systemd.daemon

import logger


log = logger.Logger('skyweather2', debug=True)


def start():
    # Start actual process
    # Start background process
    # Open DB connections
    log.info('Starting SkyWeather 2')
    systemd.daemon.notify('READY=1')

    # Do stuff
    while True:
        time.sleep(1)


def shutdown(signum, frame):
    # Close out db connection
    # Kill processes
    systemd.daemon.notify('STOPPING=1')
    log.info('Stopping Skyweather 2')
    sys.exit(0)


def run():
    with daemon.DaemonContext(
            pidfile=lockfile.FileLock('/tmp/skyweather2.pid'),
            stdout=sys.stdout,
            stderr=sys.stderr,
            signal_map={
                signal.SIGTERM: shutdown,
                signal.SIGTSTP: shutdown,
                signal.SIGINT: shutdown
            }):
        start()


if __name__ == '__main__':
    run()
