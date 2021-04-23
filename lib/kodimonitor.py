import time
import xbmc
from lib import utils
from lib.tvconnectionmanager import TvConnectionManager

# Extend the xbmc.Monitor class to do our bidding
class KodiMonitor(xbmc.Monitor):

    def __init__(self, tvConnection):
        # type: (TvConnectionManager) -> void
        self.tvConnection = tvConnection
        self.timeScreensaverActivated = 0
        self.TIME_TO_TV_SLEEP = (60 * int(utils.getSetting('timeUntilSleep')))  # Default setting is 5 minutes

    def onScreensaverDeactivated(self):
        utils.log("Screensaver deactivated")
        self.tvConnection.wakeUpTv()
        xbmc.sleep(2000)  # Let the TV turn on before ending the method's execution
        self.tvConnection.setTvToKodiInput()

    def onScreensaverActivated(self):
        utils.log("Screensaver activated")
        self.resetScreensaverActivationTime()

    def resetScreensaverActivationTime(self):
        self.timeScreensaverActivated = int(time.time())

    def isTimeToSleep(self):
        currentTime = int(time.time())
        return (currentTime - self.timeScreensaverActivated) > self.TIME_TO_TV_SLEEP

    def checkIfTimeToSleep(self):
        utils.log("Checking if going to sleep")
        if self.tvConnection.tvIsOff():
            self.resetScreensaverActivationTime()
        if xbmc.getCondVisibility("System.ScreenSaverActive") and self.tvConnection.tvIsOn():

            if self.tvConnection.isTvSetToKodiInput() and self.isTimeToSleep():
                utils.log("Input is " + self.tvConnection.getTvInput() + " and its past our bedtime, going to sleep")
                self.tvConnection.turnOff()

            # Reset the screensaver activated time because we're using another input and if
            # we switch inputs manually afterwards, the TV will turn off almost instantly lol
            if not self.tvConnection.isTvSetToKodiInput():
                utils.log("Input is not " + self.tvConnection.getTvInput() + ", resetting screensaver timer")
                self.resetScreensaverActivationTime()
