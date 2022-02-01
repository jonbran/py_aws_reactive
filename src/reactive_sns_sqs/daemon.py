import multiprocessing as mp
from multiprocessing import Process, Value
from typing import Any


class DaemonSingleton(object):
    ''' Creates a background proess continues to run until it is stopped. '''

    _instance = None
    _p: Process = None
    _running: Value = None
    _target: Any = None


    @property
    def running(self):
        return self._running.value

    @running.setter
    def running(self, s):
        self._running.value = s
        
    @property
    def pid(self):
        pid = self._p and self._p.pid or 0
        return pid

    def __new__(cls):
        ''' Implemented as a singleton. '''
        if (cls._instance is None):
            cls._instance = super(DaemonSingleton, cls).__new__(cls)
        return cls._instance

    def pid(self):
        ''' returns the PID of the current process if any '''
        pid = self._p and self._p.pid or 0
        return pid

    def start(self, target):
        if (self._running and self._running.value == True):
            return

        self._target = target
        self._running = Value('b', True)
        self._p = Process(target=self._target, args=(self._running,))
        self._p.start()

    def stop(self):
        ''' Stops the daemon if it isn't running '''
        if (self._p == None):
            return
        self._running.value = False
        self._p.join()
        self._p = None

    def restart(self):
        ''' Restarts the daemon, if it's not running it will be started. '''
        if (self._p):
            self.stop()

        self.start(self._target)
