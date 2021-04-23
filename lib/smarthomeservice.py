import utils
from tvconnectionmanager import TvConnectionManager
from kodimonitor import KodiMonitor


class SmartHomeService:

    def __init__(self):
        utils.log("Smart Home Service starting")
        self.tvConnectionManager = TvConnectionManager()
        self.monitor = KodiMonitor(self.tvConnectionManager)

    def run(self):
        utils.log("Smart Home Service running")

        while not self.monitor.abortRequested() and self.tvConnectionManager.isRunning:
            # Sleep/wait for abort for 2 seconds
            if self.monitor.waitForAbort(2):
                # Abort was requested while waiting. We should exit
                utils.log("Kodi abort detected, stopping service execution")
                break
            self.tick()

    def tick(self):
        if self.tvConnectionManager.isConnected:
            self.monitor.checkIfTimeToSleep()
