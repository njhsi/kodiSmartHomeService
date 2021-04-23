from braviarc import BraviaRC
from .. import utils


class TvSony: # implements TV contract

    def __init__(self, ipAddress='', macAddress=''):
        self.ipAddress = ipAddress
        self.macAddress = macAddress
        self.tv = BraviaRC(self.ipAddress, self.macAddress)

    def getName(self):
        return "Sony Bravia TV"

    def getInput(self):
        playing_content = self.tv.get_playing_info()
        return playing_content.get('title')

    def setInput(self, input=''):
        if not input == '':
            self.tv.select_source(input)

    def turnOff(self):
        self.tv.turn_off()

    def isOff(self):
        return self.tv.get_power_status() == u'standby'

    def turnOn(self):
        self.tv.turn_on()

    def isOn(self):
        return self.tv.get_power_status() == u'active'

    def promptForConnection(self):
        return utils.yesNoDialog(utils.getString(30011), utils.getString(30012), utils.getString(30013))

    def configureConnection(self):

        utils.log("Requesting PIN from TV")
        self.connect()

        pinFromTv = self.getPinFromUserPrompt()
        if pinFromTv is False:
            return False

        utils.log("PIN " + pinFromTv + " entered")

        self.connect(pinFromTv)

        if not self.tv.is_connected():
            utils.log("PIN incorrect, exiting")
            utils.notificationError(utils.getString(30015))
            return False
        else:
            utils.log("PIN correct, saving to plugin settings")
            utils.setSetting('tvPin', pinFromTv)
            utils.log("New PIN is " + utils.getSetting('tvPin'))
            return self.connect()

    # Get a pin from the user when setting up the TV
    def getPinFromUserPrompt(self):
        pinFromTv = ''

        while not self.validatePin(pinFromTv):
            pinFromTv = utils.numberDialog(utils.getString(30014))
            if not self.validatePin(pinFromTv):
                userWantsToTryAgain = utils.yesNoDialog('PIN incorrect, it needs to be exactly 4 digits.', 'Try again?')
                if not userWantsToTryAgain:
                    break

        if pinFromTv == '':
            return False
        else:
            return pinFromTv

    def connect(self, pin=utils.getSetting('tvPin')):
        if not self.validatePin(pin):
            return False

        return self.tv.connect(pin, utils.addOnTvClientId, utils.getAddOnName())

    def validatePin(self, pinFromTv=''):
        return pinFromTv != '' and pinFromTv.isdigit() and len(pinFromTv) == 4

    def isConfigured(self):
        return utils.getSetting('tvPin') != "0000"
