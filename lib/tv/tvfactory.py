from sony import TvSony
from .. import utils

class TvFactory:

    def __init__(self):
        self.tvIp = utils.getSetting('tvIpAddress')
        self.tvMacAddress = utils.getSetting('tvMacAddress')
        self.availableTvs = dict(Sony=TvSony)

    def getTv(self, tv=None):
        return self.availableTvs[tv](self.tvIp, self.tvMacAddress)
