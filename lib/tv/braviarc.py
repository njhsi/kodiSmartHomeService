u"""
Sony Bravia RC API

By Antonio Parraga Navarro

dedicated to Isabel

"""
from __future__ import absolute_import
import os
import sys
import requests

import logging
import base64
import collections
import json
import socket
import struct


TIMEOUT = 10

_LOGGER = logging.getLogger(__name__)


class BraviaRC(object):

    def __init__(self, host, mac=None):  # mac address is optional but necessary if we want to turn on the TV
        u"""Initialize the Sony Bravia RC class."""

        self._host = host
        self._mac = mac
        self._cookies = None
        self._commands = []
        self._content_mapping = []

    def _jdata_build(self, method, params):
        if params:
            ret = json.dumps({u"method": method, u"params": [params], u"id": 1, u"version": u"1.0"})
        else:
            ret = json.dumps({u"method": method, u"params": [], u"id": 1, u"version": u"1.0"})
        return ret

    def connect(self, pin, clientid, nickname):
        u"""Connect to TV and get authentication cookie.

        Parameters
        ---------
        pin: str
            Pin code show by TV (or 0000 to get Pin Code).
        clientid: str
            Client ID.
        nickname: str
            Client human friendly name.

        Returns
        -------
        bool
            True if connected.
        """
        authorization = json.dumps(
            {u"method": u"actRegister",
             u"params": [{u"clientid": clientid,
                         u"nickname": nickname,
                         u"level": u"private"},
                        [{u"value": u"yes",
                          u"function": u"WOL"}]],
             u"id": 1,
             u"version": u"1.0"}
        ).encode(u'utf-8')

        headers = {}
        if pin:
            username = u''
            base64string = base64.encodestring((u'%s:%s' % (username, pin)).encode()) \
                .decode().replace(u'\n', u'')
            headers[u'Authorization'] = u"Basic %s" % base64string
            headers[u'Connection'] = u"keep-alive"

        try:
            response = requests.post(u'http://'+self._host+u'/sony/accessControl',
                                     data=authorization, headers=headers, timeout=TIMEOUT)
            response.raise_for_status()

        except requests.exceptions.HTTPError, exception_instance:
            _LOGGER.error(u"[W] HTTPError: " + unicode(exception_instance))
            return False

        except Exception, exception_instance:  # pylint: disable=broad-except
            _LOGGER.error(u"[W] Exception: " + unicode(exception_instance))
            return False

        else:
            resp = response.json()
            _LOGGER.debug(json.dumps(resp, indent=4))
            if resp is None or not resp.get(u'error'):
                self._cookies = response.cookies
                return True

        return False

    def is_connected(self):
        if self._cookies is None:
            return False
        else:
            return True

    def _wakeonlan(self):
        if self._mac is not None:
            addr_byte = self._mac.split(u':')
            hw_addr = struct.pack(u'BBBBBB', int(addr_byte[0], 16),
                                  int(addr_byte[1], 16),
                                  int(addr_byte[2], 16),
                                  int(addr_byte[3], 16),
                                  int(addr_byte[4], 16),
                                  int(addr_byte[5], 16))
            msg = '\xff' * 6 + hw_addr * 16
            socket_instance = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_instance.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            socket_instance.sendto(msg, (u'<broadcast>', 9))
            socket_instance.close()

    def send_req_ircc(self, params, log_errors=True):
        u"""Send an IRCC command via HTTP to Sony Bravia."""
        headers = {u'SOAPACTION': u'"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"'}
        data = (u"<?xml version=\"1.0\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org" +
                u"/soap/envelope/\" " +
                u"s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body>" +
                u"<u:X_SendIRCC " +
                u"xmlns:u=\"urn:schemas-sony-com:service:IRCC:1\"><IRCCCode>" +
                params+u"</IRCCCode></u:X_SendIRCC></s:Body></s:Envelope>").encode(u"UTF-8")
        try:
            response = requests.post(u'http://' + self._host + u'/sony/IRCC',
                                     headers=headers,
                                     cookies=self._cookies,
                                     data=data,
                                     timeout=TIMEOUT)
        except requests.exceptions.HTTPError, exception_instance:
            if log_errors:
                _LOGGER.error(u"HTTPError: " + unicode(exception_instance))

        except Exception, exception_instance:  # pylint: disable=broad-except
            if log_errors:
                _LOGGER.error(u"Exception: " + unicode(exception_instance))
        else:
            content = response.content
            return content

    def bravia_req_json(self, url, params, log_errors=True):
        u""" Send request command via HTTP json to Sony Bravia."""
        try:
            response = requests.post(u'http://'+self._host+u'/'+url,
                                     data=params.encode(u"UTF-8"),
                                     cookies=self._cookies,
                                     timeout=TIMEOUT)
        except requests.exceptions.HTTPError, exception_instance:
            if log_errors:
                _LOGGER.error(u"HTTPError: " + unicode(exception_instance))

        except Exception, exception_instance:  # pylint: disable=broad-except
            if log_errors:
                _LOGGER.error(u"Exception: " + unicode(exception_instance))

        else:
            html = json.loads(response.content.decode(u'utf-8'))
            return html

    def send_command(self, command):
        u"""Sends a command to the TV."""
        self.send_req_ircc(self.get_command_code(command))

    def get_source(self, source):
        u"""Returns list of Sources"""
        original_content_list = []
        content_index = 0
        while True:
            resp = self.bravia_req_json(u"sony/avContent",
                                        self._jdata_build(u"getContentList", {u"source": source, u"stIdx": content_index}))
            if not resp.get(u'error'):
                if len(resp.get(u'result')[0]) == 0:
                    break
                else:
                    content_index = resp.get(u'result')[0][-1][u'index']+1
                original_content_list.extend(resp.get(u'result')[0])
            else:
                break
        return original_content_list

    def load_source_list(self):
        u""" Load source list from Sony Bravia."""
        original_content_list = []
        resp = self.bravia_req_json(u"sony/avContent",
                                    self._jdata_build(u"getSourceList", {u"scheme": u"tv"}))
        if not resp.get(u'error'):
            results = resp.get(u'result')[0]
            for result in results:
                if result[u'source'] in [u'tv:dvbc', u'tv:dvbt']:  # tv:dvbc = via cable, tv:dvbt = via DTT
                    original_content_list.extend(self.get_source(result[u'source']))

        resp = self.bravia_req_json(u"sony/avContent",
                                    self._jdata_build(u"getSourceList", {u"scheme": u"extInput"}))
        if not resp.get(u'error'):
            results = resp.get(u'result')[0]
            for result in results:
                if result[u'source'] in (u'extInput:hdmi', u'extInput:composite', u'extInput:component'):  # physical inputs
                    resp = self.bravia_req_json(u"sony/avContent",
                                                self._jdata_build(u"getContentList", result))
                    if not resp.get(u'error'):
                        original_content_list.extend(resp.get(u'result')[0])

        return_value = collections.OrderedDict()
        for content_item in original_content_list:
            return_value[content_item[u'title']] = content_item[u'uri']
        return return_value

    def get_playing_info(self):
        return_value = {}
        resp = self.bravia_req_json(u"sony/avContent", self._jdata_build(u"getPlayingContentInfo", None))
        if resp is not None and not resp.get(u'error'):
            playing_content_data = resp.get(u'result')[0]
            return_value[u'programTitle'] = playing_content_data.get(u'programTitle')
            return_value[u'title'] = playing_content_data.get(u'title')
            return_value[u'programMediaType'] = playing_content_data.get(u'programMediaType')
            return_value[u'dispNum'] = playing_content_data.get(u'dispNum')
            return_value[u'source'] = playing_content_data.get(u'source')
            return_value[u'uri'] = playing_content_data.get(u'uri')
            return_value[u'durationSec'] = playing_content_data.get(u'durationSec')
            return_value[u'startDateTime'] = playing_content_data.get(u'startDateTime')
        return return_value

    def get_power_status(self):
        u"""Get power status: off, active, standby"""
        return_value = u'off' # by default the TV is turned off
        try:
            resp = self.bravia_req_json(u"sony/system", self._jdata_build(u"getPowerStatus", None), False)
            if resp is not None and not resp.get(u'error'):
                power_data = resp.get(u'result')[0]
                return_value = power_data.get(u'status')
        except:  # pylint: disable=broad-except
            pass
        return return_value

    def _refresh_commands(self):
        resp = self.bravia_req_json(u"sony/system", self._jdata_build(u"getRemoteControllerInfo", None))
        if not resp.get(u'error'):
            self._commands = resp.get(u'result')[1]
        else:
            _LOGGER.error(u"JSON request error: " + json.dumps(resp, indent=4))

    def get_command_code(self, command_name):
        if len(self._commands) == 0:
            self._refresh_commands()
        for command_data in self._commands:
            if command_data.get(u'name') == command_name:
                return command_data.get(u'value')
        return None

    def get_volume_info(self):
        u"""Get volume info."""
        resp = self.bravia_req_json(u"sony/audio", self._jdata_build(u"getVolumeInformation", None))
        if not resp.get(u'error'):
            results = resp.get(u'result')[0]
            for result in results:
                if result.get(u'target') == u'speaker':
                    return result
        else:
            _LOGGER.error(u"JSON request error:" + json.dumps(resp, indent=4))
        return None

    def set_volume_level(self, volume):
        u"""Set volume level, range 0..1."""
        self.bravia_req_json(u"sony/audio", self._jdata_build(u"setAudioVolume", {u"target": u"speaker",
                                                                                u"volume": volume * 100}))

    def turn_on(self):
        u"""Turn the media player on."""
        #self._wakeonlan()
        self.send_req_ircc(self.get_command_code(u'TvPower'))
        # Try using the power on command incase the WOL doesn't work
        if self.get_power_status() != u'active':
            self.send_req_ircc(self.get_command_code(u'TvPower'))

    def turn_off(self):
        u"""Turn off media player."""
        self.send_req_ircc(self.get_command_code(u'PowerOff'))

    def volume_up(self):
        u"""Volume up the media player."""
        self.send_req_ircc(self.get_command_code(u'VolumeUp'))

    def volume_down(self):
        u"""Volume down media player."""
        self.send_req_ircc(self.get_command_code(u'VolumeDown'))

    def mute_volume(self, mute):
        u"""Send mute command."""
        self.send_req_ircc(self.get_command_code(u'Mute'))

    def select_source(self, source):
        u"""Set the input source."""
        if len(self._content_mapping) == 0:
            self._content_mapping = self.load_source_list()
        if source in self._content_mapping:
            uri = self._content_mapping[source]
            self.play_content(uri)

    def play_content(self, uri):
        u"""Play content by URI."""
        self.bravia_req_json(u"sony/avContent", self._jdata_build(u"setPlayContent", {u"uri": uri}))

    def media_play(self):
        u"""Send play command."""
        self.send_req_ircc(self.get_command_code(u'Play'))

    def media_pause(self):
        u"""Send media pause command to media player."""
        self.send_req_ircc(self.get_command_code(u'Pause'))

    def media_next_track(self):
        u"""Send next track command."""
        self.send_req_ircc(self.get_command_code(u'Next'))

    def media_previous_track(self):
        u"""Send the previous track command."""
        self.send_req_ircc(self.get_command_code(u'Prev'))
