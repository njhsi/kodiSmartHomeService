import xbmc
import xbmcaddon
import xbmcgui

__addOnId = u'service.smarttvservice'
addOnTvClientId = u'kodismarttvservice'
__addOn = xbmcaddon.Addon(__addOnId)


def log(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log(__addOnId + ": " + message, level=loglevel)


def getAddOnName():
    return __addOn.getAddonInfo('name')


def getSetting(settingId):
    return __addOn.getSetting(settingId)


def setSetting(settingId, settingValue):
    return __addOn.setSetting(settingId, settingValue)


def notification(message, type=xbmcgui.NOTIFICATION_INFO):
    xbmcgui.Dialog().notification(getAddOnName(), message, type)


def notificationError(message):
    notification(message, xbmcgui.NOTIFICATION_ERROR)


def numberDialog(prompt):
    return xbmcgui.Dialog().numeric(0, prompt)


def yesNoDialog(line1, line2='', line3=''):
    return xbmcgui.Dialog().yesno(getAddOnName(), line1, line2, line3)


def getString(stringId):
    return __addOn.getLocalizedString(stringId)


def getTvInputSetting(self):
    input = getSetting('tvInput')
    # 0 => '', 1 => HDMI 1, etc
    return {
        '0': '',
        '1': 'HDMI 1',
        '2': 'HDMI 2',
        '3': 'HDMI 3',
        '4': 'HDMI 4'
    }.get(input, '')  # '' is default if input not found

def getTvBrandSetting(self):
    brand = getSetting('tvBrand')
    # 0 => '', 1 => Sony, etc
    return {
        '0': '',
        '1': 'Sony'
    }.get(brand, '')  # '' is default if input not found
