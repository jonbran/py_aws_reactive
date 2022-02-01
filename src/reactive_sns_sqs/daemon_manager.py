
from typing import Callable

from .daemon import DaemonSingleton


class DaemonManager():

    # private members
    _start: Callable

    def __init__(self, start_function: Callable) -> None:
        if (not start_function):
            raise ValueError('start_function is required')
        self._start = start_function

    def get_daemon_pid(self):
        daemon = DaemonSingleton()
        return daemon.pid()

    def start(self):
        daemon = DaemonSingleton()
        daemon.start(self._start)
        pid = daemon.pid()
        return pid and f'Listener started with PID:{pid}' or 'Listener failed to start PID:{pid}'

    def stop(self):
        deamon = DaemonSingleton()
        if (self._stop):
            self._stop()
        deamon.stop()
        pid = deamon.pid()
        return not pid and "Listener successfully stopped" or "There was a problem stopping the listener"

    def restart(self):
        deamon = DaemonSingleton()
        deamon.restart()
        pid = deamon.pid()
        return pid and f'Listener restarted. New PID:{pid}'
