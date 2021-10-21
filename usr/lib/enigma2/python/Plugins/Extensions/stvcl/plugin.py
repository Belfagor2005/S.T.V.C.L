#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#--------------------#
#  coded by Lululla	 #
#	skin by MMark	 #
#	  21/10/2021	 #
#--------------------#
#Info http://t.me/tivustream
from __future__ import print_function
from . import _
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ConfigList import *
from Components.HTMLComponent import *
from Components.Input import Input
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap, MultiPixmap
from Components.PluginComponent import plugins
from Components.PluginList import *
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.SelectionList import SelectionList
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.ServiceList import ServiceList
from Components.Sources.List import List
from Components.Sources.Progress import Progress
from Components.Sources.Source import Source
from Components.Sources.StaticText import StaticText
from Components.config import *
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.InfoBar import MoviePlayer, InfoBar
from Screens.InfoBarGenerics import InfoBarMenu, InfoBarSeek, InfoBarAudioSelection, \
    InfoBarSubtitleSupport, InfoBarNotifications
from Screens.InputBox import InputBox
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.PluginBrowser import PluginBrowser
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop, Standby
from Screens.VirtualKeyBoard import VirtualKeyBoard
from ServiceReference import ServiceReference
from Tools.Directories import SCOPE_PLUGINS
from Tools.Directories import resolveFilename
from Tools.Downloader import downloadWithProgress
from Tools.LoadPixmap import LoadPixmap
from enigma import *
from enigma import RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER
from enigma import eSize, eListbox, eListboxPythonMultiContent, eServiceCenter, eServiceReference, iPlayableService
from enigma import eTimer
from enigma import getDesktop, ePicLoad, gPixmapPtr
from enigma import loadPNG, gFont
from os.path import splitext
from random import choice
from sys import version_info
from time import sleep
from twisted.web.client import downloadPage, getPage, error
from xml.dom import Node, minidom
import base64
import glob
import os
import random
import re
import shutil
import six
import socket
import ssl
import sys
import time
from six.moves.urllib.request import urlopen
from six.moves.urllib.request import Request
from six.moves.urllib.error import HTTPError, URLError
from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import quote
from six.moves.urllib.parse import urlencode
from six.moves.urllib.request import urlretrieve
import six.moves.urllib.request
from Plugins.Extensions.stvcl.getpics import GridMain
from Plugins.Extensions.stvcl.getpics import getpics
try:
    import io
except:
    import StringIO
try:
    import http.cookiejar
except:
    import cookielib
try:
    import httplib
except:
    import http.client

if sys.version_info >= (2, 7, 9):
	try:
		import ssl
		sslContext = ssl._create_unverified_context()
	except:
		sslContext = None

def checkStr(txt):
    if six.PY3:
        if isinstance(txt, type(bytes())):
            txt = txt.decode('utf-8')
    else:
        if isinstance(txt, type(six.text_type())):
            txt = txt.encode('utf-8')
    return txt

try:
    from enigma import eDVBDB
except ImportError:
    eDVBDB = None

ListAgent = [
          'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15',
          'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14',
          'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
          'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
          'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1284.0 Safari/537.13',
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.8 (KHTML, like Gecko) Chrome/17.0.940.0 Safari/535.8',
          'Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
          'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
          'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
          'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2',
          'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.16) Gecko/20120427 Firefox/15.0a1',
          'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1',
          'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:15.0) Gecko/20120910144328 Firefox/15.0.2',
          'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1',
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0a2) Gecko/20111101 Firefox/9.0a2',
          'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110613 Firefox/6.0a2',
          'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110612 Firefox/6.0a2',
          'Mozilla/5.0 (Windows NT 6.1; rv:6.0) Gecko/20110814 Firefox/6.0',
          'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0',
          'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
          'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
          'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)',
          'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/4.0; InfoPath.2; SV1; .NET CLR 2.0.50727; WOW64)',
          'Mozilla/4.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)',
          'Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)',
          'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0;  it-IT)',
          'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US)'
          'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; chromeframe/13.0.782.215)',
          'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; chromeframe/11.0.696.57)',
          'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0) chromeframe/10.0.648.205',
          'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.1; SV1; .NET CLR 2.8.52393; WOW64; en-US)',
          'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; chromeframe/11.0.696.57)',
          'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/4.0; GTB7.4; InfoPath.3; SV1; .NET CLR 3.1.76908; WOW64; en-US)',
          'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.2; SV1; .NET CLR 3.3.69573; WOW64; en-US)',
          'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)',
          'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; InfoPath.1; SV1; .NET CLR 3.8.36217; WOW64; en-US)',
          'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
          'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; it-IT)',
          'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
          'Opera/12.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.02',
          'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00',
          'Opera/9.80 (Windows NT 5.1; U; zh-sg) Presto/2.9.181 Version/12.00',
          'Opera/12.0(Windows NT 5.2;U;en)Presto/22.9.168 Version/12.00',
          'Opera/12.0(Windows NT 5.1;U;en)Presto/22.9.168 Version/12.00',
          'Mozilla/5.0 (Windows NT 5.1) Gecko/20100101 Firefox/14.0 Opera/12.0',
          'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25',
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10',
          'Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko ) Version/5.1 Mobile/9B176 Safari/7534.48.3'
          ]
currversion = '1.0'
Version = currversion + ' - 15.10.2021'
title_plug = '..:: S.T.V.C.L. V.%s ::..' % Version
name_plug = 'Smart Tv Channels List'
plugin_fold    = os.path.dirname(sys.modules[__name__].__file__)
# plugin_fold = '/usr/lib/enigma2/python/Plugins/Extensions/stvcl/'
# Credits = 'http://t.me/tivustream'
Maintainer2 = 'Maintener @Lululla'
dir_enigma2 = '/etc/enigma2/'
service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'
res_plugin_fold=plugin_fold + '/res/'

#================
def RequestAgent():
    RandomAgent = choice(ListAgent)
    return RandomAgent

def add_skin_font():
    font_path = plugin_fold + '/res/fonts/'
    # addFont(font_path + 'verdana_r.ttf', 'OpenFont1', 100, 1)
    addFont(font_path + 'verdana_r.ttf', 'OpenFont2', 100, 1)

def checkInternet():
    try:
        socket.setdefaulttimeout(0.5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except:
        return False

def ReloadBouquet():
    if eDVBDB:
        eDVBDB.getInstance().reloadBouquets()
    else:
        os.system('wget -qO - http://127.0.0.1/web/servicelistreload?mode=2 > /dev/null 2>&1 &')

def OnclearMem():
    try:
        os.system("sync")
        os.system("echo 1 > /proc/sys/vm/drop_caches")
        os.system("echo 2 > /proc/sys/vm/drop_caches")
        os.system("echo 3 > /proc/sys/vm/drop_caches")
    except:
        pass

def trace_error():
    import traceback
    try:
        traceback.print_exc(file=sys.stdout)
        traceback.print_exc(file=open('/tmp/KeyAdderError.log', 'a'))
    except:
        pass

def make_request(url):
    try:
        import requests
        link = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'}).text
        print('link1: ', link)
        return link
    except ImportError:
        req = Request(url)
        req.add_header('User-Agent',RequestAgent())
        response = urlopen(req, None, 3)
        link = response.read()
        response.close()
        print('link2: ', link)
        return link
    except:
        e = URLError
        print('We failed to open "%s".' % url)
        if hasattr(e, 'code'):
            print('We failed with error code - %s.' % e.code)
        if hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        return
    return

def isExtEplayer3Available():
        return os.path.isfile(eEnv.resolve('$bindir/exteplayer3'))

def isStreamlinkAvailable():
        return os.path.isdir(eEnv.resolve('/usr/lib/python2.7/site-packages/streamlink'))

modechoices = [
                ("4097", _("ServiceMp3(4097)")),
                ("1", _("Hardware(1)")),
                ]

if os.path.exists("/usr/bin/gstplayer"):
    modechoices.append(("5001", _("Gstreamer(5001)")))
if os.path.exists("/usr/bin/exteplayer3"):
    modechoices.append(("5002", _("Exteplayer3(5002)")))
if os.path.exists("/usr/bin/apt-get"):
    modechoices.append(("8193", _("eServiceUri(8193)")))

sessions = []
config.plugins.stvcl = ConfigSubsection()
config.plugins.stvcl.pthm3uf = ConfigDirectory(default='/media/hdd/movie')
try:
    from Components.UsageConfig import defaultMoviePath
    downloadpath = defaultMoviePath()
    config.plugins.stvcl.pthm3uf  = ConfigDirectory(default=downloadpath)
except:
    if os.path.exists("/usr/bin/apt-get"):
        config.plugins.stvcl.pthm3uf  = ConfigDirectory(default='/media/hdd/movie/')
config.plugins.stvcl.bouquettop             = ConfigSelection(default='Bottom', choices=['Bottom', 'Top'])
config.plugins.stvcl.services               = ConfigSelection(default='4097', choices=modechoices)
config.plugins.stvcl.cachefold              = ConfigDirectory(default='/media/hdd/')
config.plugins.stvcl.filter                = ConfigYesNo(default=False)
config.plugins.stvcl.strtext                = ConfigYesNo(default=True)
config.plugins.stvcl.strtmain               = ConfigYesNo(default=True)
config.plugins.stvcl.thumb                  = ConfigYesNo(default=False)
config.plugins.stvcl.thumbpic               = ConfigYesNo(default=False)
tvstrvl = config.plugins.stvcl.cachefold.value + "stvcl"
tmpfold = config.plugins.stvcl.cachefold.value + "stvcl/tmp"
picfold = config.plugins.stvcl.cachefold.value + "stvcl/pic"
global Path_Movies
Path_Movies             = str(config.plugins.stvcl.pthm3uf.value) #+ "/"
if Path_Movies.endswith("\/\/"):
    Path_Movies = Path_Movies[:-1]
print('patch movies: ', Path_Movies)

if not os.path.exists(tvstrvl):
    os.system("mkdir " + tvstrvl)
if not os.path.exists(tmpfold):
    os.system("mkdir " + tmpfold)
if not os.path.exists(picfold):
    os.system("mkdir " + picfold)

global skin_fold
HD = getDesktop(0).size()
if HD.width() > 1280:
    skin_fold=res_plugin_fold + 'skins/fhd/'
else:
    skin_fold=res_plugin_fold + 'skins/hd/'
if os.path.exists('/var/lib/dpkg/status'):
    skin_fold=skin_fold + 'dreamOs/'

def remove_line(filename, what):
    if os.path.isfile(filename):
        file_read = open(filename).readlines()
        file_write = open(filename, 'w')
        for line in file_read:
            if what not in line:
                file_write.write(line)
        file_write.close()

def m3ulistEntry(download):
    res = [download]
    white = 16777215
    yellow = 16776960
    green = 3828297
    col = 16777215
    backcol = 0
    blue = 4282611429
    png = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('setting2.png'))
    # png = '/usr/lib/enigma2/python/Plugins/Extensions/stvcl/res/pics/setting2.png'
    if HD.width() > 1280:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1200, 50), font=7, text=download, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=2, text=download, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res

def m3ulist(data, list):
    icount = 0
    mlist = []
    for line in data:
        name = data[icount]
        mlist.append(m3ulistEntry(name))
        icount = icount + 1
    list.setList(mlist)

class tvList(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('OpenFont2', 20))
        self.l.setFont(1, gFont('OpenFont2', 22))
        self.l.setFont(2, gFont('OpenFont2', 24))
        self.l.setFont(3, gFont('OpenFont2', 26))
        self.l.setFont(4, gFont('OpenFont2', 28))
        self.l.setFont(5, gFont('OpenFont2', 30))
        self.l.setFont(6, gFont('OpenFont2', 32))
        self.l.setFont(7, gFont('OpenFont2', 34))
        self.l.setFont(8, gFont('OpenFont2', 36))
        self.l.setFont(9, gFont('OpenFont2', 40))
        if HD.width() > 1280:
            self.l.setItemHeight(50)
        else:
            self.l.setItemHeight(50)

def tvListEntry(name,png):
    res = [name]
    # png = '/usr/lib/enigma2/python/Plugins/Extensions/stvcl/res/pics/setting.png'
    png = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('setting.png'))
    if HD.width() > 1280:
            res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(png)))
            res.append(MultiContentEntryText(pos=(60, 0), size=(1200, 50), font=7, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
            res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(png)))
            res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=2, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res

Panel_list = [
 ('SamsungTVPlus'),
 ('PBS'),
 # ('Plex'),
 ('PlutoTV'),
 ('Stirr'),
 ('Adelaide'),
 ('Brisbane'),
 ('Canberra'),
 ('Darwin'),
 ('Hobart'),
 ('Melbourne'),
 ('Perth'),
 ('Sydney')

 ]

class OpenScript(Screen):
    def __init__(self, session):
        self.session = session
        skin = skin_fold + '/OpenScript.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        # f.close()
        Screen.__init__(self, session)
        self.setup_title = _('Smart Tv Channel List')
        self['list'] = tvList([])
        self.icount = 0
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self['title'] = Label(_(title_plug))
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['path'] = Label(_('Folder path %s') % Path_Movies)
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button('')
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'MenuActions', 'TimerEditActions'],
         {'ok': self.okRun,
         'menu': self.scsetup,
         'red': self.close,
         # 'green': self.messagereload,
         'info': self.close,
         # 'yellow': self.messagedellist,
         # 'blue': self.ChannelList,
         'back': self.close,
         'cancel': self.close}, -1)
        # self.onFirstExecBegin.append(self.updateMenuList)
        self.onLayoutFinish.append(self.updateMenuList)

    def updateMenuList(self):
        self.menu_list = []
        for x in self.menu_list:
            del self.menu_list[0]
        list = []
        idx = 0
        # png = '/usr/lib/enigma2/python/Plugins/Extensions/stvcl/res/pics/setting.png'
        png = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('setting.png'))
        for x in Panel_list:
            list.append(tvListEntry(x, png))
            self.menu_list.append(x)
            idx += 1
        self['list'].setList(list)

    def okRun(self):
        self.keyNumberGlobalCB(self['list'].getSelectedIndex())

    def keyNumberGlobalCB(self, idx):
        sel = self.menu_list[idx]
        url = ''
        if sel == ("SamsungTVPlus"):
            url = 'http://i.mjh.nz/SamsungTVPlus/'
        elif sel == ("PBS"):
            url = 'http://i.mjh.nz/PBS/'
        # elif sel == ("Plex"):
            # url = 'http://i.mjh.nz/Plex/'
        elif sel == ("PlutoTV"):
            url = 'http://i.mjh.nz/PlutoTV/'
        elif sel == ("Stirr"):
            url = 'http://i.mjh.nz/Stirr/'
        elif sel == ('Adelaide'):
            url = 'http://i.mjh.nz/au/Adelaide/'
        elif sel == ('Brisbane'):
            url = 'http://i.mjh.nz/au/Brisbane/'
        elif sel == ('Canberra'):
            url = 'http://i.mjh.nz/au/Canberra/'
        elif sel == ('Darwin'):
            url = 'http://i.mjh.nz/au/Darwin/'
        elif sel == ('Hobart'):
            url = 'http://i.mjh.nz/au/Hobart/'
        elif sel == ('Melbourne'):
            url = 'http://i.mjh.nz/au/Melbourne/'
        elif sel == ('Perth'):
            url = 'http://i.mjh.nz/au/Perth/'
        elif sel == ('Sydney'):
            url = 'http://i.mjh.nz/au/Sydney/'

        else:
            return
        self.downlist(sel, url)

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def check(self, fplug):
        self.downloading = False
        self['progresstext'].text = ''
        self.progclear = 0
        self['progress'].setValue(self.progclear)
        self["progress"].hide()

    def showError(self, error):
        self.downloading = False
        self.session.open(openMessageBox, _('Download Failed!!!'), openMessageBox.TYPE_INFO, timeout=5)

    def downlist(self, sel, url):
        global in_tmp
        namem3u = str(sel)
        urlm3u = checkStr(url.strip())
        if six.PY3:
            urlm3u.encode()
        # if six.PY3:
            # urlm3u = six.ensure_str(urlm3u)
        print('urlmm33uu ', urlm3u)

        try:
            fileTitle = re.sub(r'[\<\>\:\"\/\\\|\?\*\[\]]', '_', namem3u)
            fileTitle = re.sub(r' ', '_', fileTitle)
            fileTitle = re.sub(r'_+', '_', fileTitle)
            fileTitle = fileTitle.replace("(", "_").replace(")", "_").replace("#", "").replace("+", "_").replace("\'", "_").replace("'", "_").replace("!", "_").replace("&", "_")
            fileTitle = fileTitle.lower() #+ ext
            in_tmp = str(Path_Movies) + str(fileTitle) + '.m3u'
            if os.path.isfile(in_tmp):
                os.remove(in_tmp)
            print('in tmp' , in_tmp)
            # # self.download = downloadWithProgress(urlm3u, in_tmp)
            # # self.download.addProgress(self.downloadProgress)
            # # self.download.start().addCallback(self.check).addErrback(self.showError)
            urlretrieve(urlm3u, in_tmp)
            sleep(4)
            self.session.open(ListM3u, namem3u, urlm3u)
        except Exception as e:
            print('errore e : ', e)
            # self.mbox = self.session.open(openMessageBox, _('DOWNLOAD ERROR'), openMessageBox.TYPE_INFO, timeout=5)

    def scsetup(self):
        self.session.open(OpenConfig)

class ListM3u(Screen):
    def __init__(self, session, namem3u, url):
        self.session = session
        skin = skin_fold + '/ListM3u.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        # f.close()
        Screen.__init__(self, session)
        self.list = []
        self['list'] = tvList([])
        global srefInit
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        srefInit = self.initialservice
        self['title'] = Label(title_plug + ' ' + namem3u)
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self.convert = False
        self.url = url
        self.name = namem3u
        self['path'] = Label(_('Folder path %s') % Path_Movies)
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button('')
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'MenuActions', 'TimerEditActions'],
        {
         # 'green': self.message2,
         # 'yellow': self.message1,
         # 'blue': self.message1,
         'cancel': self.cancel,
         'ok': self.runList}, -2)
        if not os.path.exists(Path_Movies):
            self.mbox = self.session.open(openMessageBox, _('Check in your Config Plugin - Path Movie'), openMessageBox.TYPE_INFO, timeout=5)
            self.scsetup()

        self.onFirstExecBegin.append(self.openList)
        sleep(3)
        # self.onLayoutFinish.append(self.openList2)
        self.onLayoutFinish.append(self.passing)

    def passing(self):
        pass

    def scsetup(self):
        self.session.openWithCallback(self.close, OpenConfig)

    def openList(self):
        self.names = []
        self.urls = []
        content = make_request(self.url)
        if six.PY3:
            content = six.ensure_str(content)
        print('content: ',content)
        #<a href="br.xml.gz">br.xml.gz</a>  21-Oct-2021 07:05   108884
        #<a href="raw-radio.m3u8">raw-radio.m3u8</a>    22-Oct-2021 06:08   9639
        regexvideo = '<a href="(.*?)">.*?</a>.*?-(.*?)-(.*?) '
        match = re.compile(regexvideo, re.DOTALL).findall(content)
        print('ListM3u match = ', match)
        items = []
        for url, mm, aa in match:
            if '.m3u8' in url:
                name = url.replace('.m3u8', '')
                name = name + ' ' + mm + '-' + aa
                url = self.url + url
                item = name + "###" + url
                print('ListM3u url-name Items sort: ', item)
                items.append(item)
        items.sort()
        for item in items:
            name = item.split('###')[0]
            url = item.split('###')[1]
            self.names.append(checkStr(name))
            self.urls.append(checkStr(url))
        m3ulist(self.names, self['list'])

    def openList2(self):
        self.names = []
        self.urls = []
        path = Path_Movies
        AA = ['.m3u8']
        for root, dirs, files in os.walk(path):
            for name in files:
                for x in AA:
                    if x in name:
                        continue
                    self.names.append(name)
                    self.urls.append(root +'/'+name)
        pass
        m3ulist(self.names, self['list'])

    def runList(self):
        idx = self["list"].getSelectionIndex()
        sel = self.names[idx]
        urlm3u = self.urls[idx]
        if idx == -1 or None or '':
            return
        else:
            self.session.open(ChannelList, sel, urlm3u)

    def cancel(self):
        self.close()

class ChannelList(Screen):
    def __init__(self, session, name, url ):
        self.session = session
        skin = skin_fold + '/ChannelList.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        # f.close()
        Screen.__init__(self, session)
        self.list = []
        self['list'] = tvList([])
        self['title'] = Label(title_plug + ' ' + name)
        self['Maintainer2'] = Label('%s' % Maintainer2)
        service = config.plugins.stvcl.services.value
        self['service'] = Label(_('Service Reference used %s') % service)
        self['live'] = Label('')
        self['path'] = Label(_('Folder path %s') % Path_Movies)
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Convert ExtePlayer3'))
        self['key_yellow'] = Button(_('Convert Gstreamer'))
        self["key_blue"] = Button(_("Search"))
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self.pin = False
        global search_ok
        global in_tmp
        global search_ok
        global servicx
        self.servicx = ''
        search_ok = False
        in_tmp = Path_Movies
        self.search = ''
        search_ok = False
        self.name = name
        self.url = url
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'MenuActions', 'TimerEditActions', 'InfobarInstantRecord'], {'red': self.cancel,
         # 'green': self.runRec,
         'menu': self.AdjUrlFavo,
         'green': self.message2,
         'yellow': self.message1,
         'cancel': self.cancel,
         "blue": self.search_m3u,
         "rec": self.runRec,
         "instantRecord": self.runRec,
         "ShortRecord": self.runRec,
         'ok': self.runChannel}, -2)
        # if 'http' in self.url:
        self.onLayoutFinish.append(self.downlist)
        # self.onFirstExecBegin.append(self.downlist)
        print('ChannelList sleep 4 - 1')
        # self.onLayoutFinish.append(self.playList)

    def message1(self):
        global servicx
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None or '':
            return
        else:
            servicx = 'iptv'
            self.session.openWithCallback(self.check10, openMessageBox, _("Do you want to Convert Bouquet IPTV?"), openMessageBox.TYPE_YESNO)

    def message2(self):
        global servicx
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None or '':
            return
        else:
            servicx = 'gst'
            self.session.openWithCallback(self.check10, openMessageBox, _("Do you want to Convert Bouquet GSTREAMER?"), openMessageBox.TYPE_YESNO)

    def check10(self, result):
            global in_tmp, namebouquett
            print('in folder tmp : ', in_tmp)
            idx = self["list"].getSelectionIndex()
            if idx == -1 or None or '':
                return
            self.convert = True
            name = self.name + ' ' + self.names[idx]
            namebouquett = name.replace(' ','-').strip()
            print('namebouquett in folder tmp : ', namebouquett)
            try:
                sleep(3)
                if os.path.isfile(in_tmp) and os.stat(in_tmp).st_size > 0:
                    print('ChannelList is_tmp exist in playlist')
                    bqtname = 'userbouquet.%s.tv' % namebouquett.lower()
                    desk_tmp = ''
                    in_bouquets = 0
                    with open('/etc/enigma2/%s' % bqtname, 'w') as outfile:
                        outfile.write('#NAME %s\r\n' % namebouquett.capitalize())
                        if servicx == 'iptv':
                            for line in open(in_tmp):
                                if line.startswith('http://') or line.startswith('https'):
                                    outfile.write('#SERVICE 4097:0:1:1:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
                                    outfile.write('#DESCRIPTION %s' % desk_tmp)
                                elif line.startswith('#EXTINF'):
                                    desk_tmp = '%s' % line.split(',')[-1]
                                elif '<stream_url><![CDATA' in line:
                                    outfile.write('#SERVICE 4097:0:1:1:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
                                    outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                                elif '<title>' in line:
                                    if '<![CDATA[' in line:
                                        desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
                                    else:
                                        desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]
                        else:
                            if servicx == 'gst':
                                for line in open(in_tmp):
                                    if line.startswith('http://') or line.startswith('https'):
                                        outfile.write('#SERVICE 5002:0:1:1:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
                                        outfile.write('#DESCRIPTION %s' % desk_tmp)
                                    elif line.startswith('#EXTINF'):
                                        desk_tmp = '%s' % line.split(',')[-1]
                                    elif '<stream_url><![CDATA' in line:
                                        outfile.write('#SERVICE 5002:0:1:1:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
                                        outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                                    elif '<title>' in line:
                                        if '<![CDATA[' in line:
                                            desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
                                        else:
                                            desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]
                        outfile.close()
                    self.mbox = self.session.open(openMessageBox, _('Check out the favorites list ...'), openMessageBox.TYPE_INFO, timeout=5)
                    if os.path.isfile('/etc/enigma2/bouquets.tv'):
                        for line in open('/etc/enigma2/bouquets.tv'):
                            if bqtname in line:
                                in_bouquets = 1

                        if in_bouquets == 0:
                            if os.path.isfile('/etc/enigma2/%s' % bqtname) and os.path.isfile('/etc/enigma2/bouquets.tv'):
                                remove_line('/etc/enigma2/bouquets.tv', bqtname)
                                with open('/etc/enigma2/bouquets.tv', 'a') as outfile:
                                    outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % bqtname)
                                    outfile.close()
                    self.mbox = self.session.open(openMessageBox, _('Shuffle Favorite List in Progress') + '\n' + _('Wait please ...'), openMessageBox.TYPE_INFO, timeout=5)
                    ReloadBouquet()
                else:
                    self.session.open(openMessageBox, _('Conversion Failed!!!'), openMessageBox.TYPE_INFO, timeout=5)
                    return
            except Exception as e:
                print('error convert iptv ',e)

    def cancel(self):
        if search_ok == True:
            self.resetSearch()
        else:
            self.close()

    def search_m3u(self):
        text = ''
        self.session.openWithCallback(
            self.filterM3u,
            VirtualKeyBoard,
            title = _("Filter this category..."),
            text=self.search)

    def filterM3u(self, result):
        if result:
            self.names = []
            self.urls = []
            self.pics = []
            pic = plugin_fold + "/res/pics/default.png"
            search = result
            try:
                f1 = open(in_tmp, "r+")
                fpage = f1.read()
                regexcat = "EXTINF.*?,(.*?)\\n(.*?)\\n"
                match = re.compile(regexcat, re.DOTALL).findall(fpage)
                for  name, url in match:
                    if str(search).lower() in name.lower():
                        global search_ok
                        search_ok = True
                        url = url.replace(" ", "")
                        url = url.replace("\\n", "")
                        self.names.append(name)
                        self.urls.append(url)
                        self.pics.append(pic)
                if search_ok == True:
                    m3ulist(self.names, self["list"])
                    self["live"].setText('N.' + str(len(self.names)) + " Stream")
                else:
                    search_ok = False
                    self.resetSearch()
            except:
                pass
        else:
            self.playList()

    def resetSearch(self):
        global re_search
        re_search = False
        if len(self.names):
            for x in self.names:
                del x
        self.playList()

    def runRec(self):
        global urlm3u, namem3u
        idx = self["list"].getSelectionIndex()
        namem3u = self.names[idx]
        urlm3u = self.urls[idx]
        if idx == -1 or None or '':
            return
        if self.downloading == True:
            self.session.open(openMessageBox, _('You are already downloading!!!'), openMessageBox.TYPE_INFO, timeout=5)
        else:
            if '.mp4' in urlm3u or '.mkv' in urlm3u or '.flv' in urlm3u or '.avi' in urlm3u :
                self.downloading = True
                self.session.openWithCallback(self.download_m3u, openMessageBox, _("DOWNLOAD VIDEO?" ) , type=openMessageBox.TYPE_YESNO, timeout = 10, default = False)
            else:
                self.downloading = False
                self.session.open(openMessageBox, _('Only VOD Movie allowed or not .ext Filtered!!!'), openMessageBox.TYPE_INFO, timeout=5)

    def download_m3u(self, result):
        if result:
            global in_tmp
            try:
                if self.downloading == True:
                    idx = self["list"].getSelectionIndex()
                    namem3u = self.names[idx]
                    urlm3u = self.urls[idx]
                    path = urlparse(urlm3u).path
                    ext = splitext(path)[1]
                    fileTitle = re.sub(r'[\<\>\:\"\/\\\|\?\*\[\]]', '_', namem3u)
                    fileTitle = re.sub(r' ', '_', fileTitle)
                    fileTitle = re.sub(r'_+', '_', fileTitle)
                    fileTitle = fileTitle.replace("(", "_").replace(")", "_").replace("#", "").replace("+", "_")
                    fileTitle = fileTitle.replace("\'", "_").replace("'", "_").replace("!", "_").replace("&", "_")
                    fileTitle = fileTitle.lower() + ext
                    in_tmp = Path_Movies + fileTitle
                    if os.path.isfile(in_tmp):
                        os.remove(in_tmp)
                    # urlretrieve(urlm3u, in_tmp)
                    # sleep(3)
                    self.download = downloadWithProgress(urlm3u, in_tmp)
                    self.download.addProgress(self.downloadProgress)
                    self.download.start().addCallback(self.check).addErrback(self.showError)
                else:
                    self.downloading = False
                    self.session.open(openMessageBox, _('Download Failed!!!'), openMessageBox.TYPE_INFO, timeout=5)
                    pass
                return
            except Exception as e:
                print('error m3u', e)

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))
        print('ChannelList downloadprogress ok')

    def check(self, fplug):
        self.downloading = False
        self['progresstext'].text = ''
        self.progclear = 0
        self['progress'].setValue(self.progclear)
        self["progress"].hide()
        print('ChannelList check ok')
        sleep(3)
        self.playList()

    def showError(self, error):
        self.downloading = False
        self.session.open(openMessageBox, _('Download Failed!!!'), openMessageBox.TYPE_INFO, timeout=5)
        print('ChannelList DownloadError')

    def downlist(self):
        global in_tmp
        namem3u = self.name
        urlm3u = self.url
        if six.PY3:
            urlm3u = six.ensure_str(urlm3u)
        print('urlmm33uu ', urlm3u)
        try:
            fileTitle = re.sub(r'[\<\>\:\"\/\\\|\?\*\[\]]', '_', namem3u)
            fileTitle = re.sub(r' ', '_', fileTitle)
            fileTitle = re.sub(r'_+', '_', fileTitle)
            fileTitle = fileTitle.replace("(", "_").replace(")", "_").replace("#", "").replace("+", "_").replace("\'", "_").replace("'", "_").replace("!", "_").replace("&", "_")
            fileTitle = fileTitle.lower() #+ ext
            in_tmp = Path_Movies + fileTitle + '.m3u'
            if os.path.isfile(in_tmp):
                os.remove(in_tmp)
            print('path tmp : ', in_tmp)
            urlretrieve(urlm3u, in_tmp)
            sleep(5)
            self.playList()
            # self.download = downloadWithProgress(urlm3u, in_tmp)
            # self.download.addProgress(self.downloadProgress)
            # self.download.start().addCallback(self.check).addErrback(self.showError)
            print('ChannelList Downlist sleep 3 - 2')        # return

        except Exception as e:
            print('errore e : ', e)
            # self.mbox = self.session.open(openMessageBox, _('DOWNLOAD ERROR'), openMessageBox.TYPE_INFO, timeout=5)
        return

    def playList(self):
        global search_ok
        search_ok = False
        self.names = []
        self.urls = []
        self.pics = []
        items = []
        # pic = plugin_fold + "/res/pics/default.png"
        pic = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('default.png'))
        try:
            if os.path.isfile(in_tmp) and os.stat(in_tmp).st_size > 0:
                print('ChannelList is_tmp exist in playlist')
                f1 = open(in_tmp, 'r+')
                fpage = f1.read()
                # fpage.seek(0)
                if "#EXTM3U" and 'tvg-logo' in fpage:
                    print('tvg-logo in fpage: True')
                    regexcat = 'EXTINF.*?tvg-logo="(.*?)".*?,(.*?)\\n(.*?)\\n'
                    match = re.compile(regexcat, re.DOTALL).findall(fpage)
                    for pic, name, url in match:
                        if url.startswith('http'):
                            url = url.replace(' ', '%20')
                            url = url.replace('\\n', '')
                            if 'samsung' in self.url.lower() or config.plugins.stvcl.filter.value == True:
                                regexcat = '(.*?).m3u8'
                                match = re.compile(regexcat, re.DOTALL).findall(url)
                                for url in match:
                                    url = url + '.m3u8'
                            pic = pic
                            item = name + "###" + url + "###" + pic
                            print('url-name Items sort: ', item)
                            items.append(item)
                    items.sort()
                    for item in items:
                        name = item.split('###')[0]
                        url = item.split('###')[1]
                        pic = item.split('###')[2]

                        self.names.append(checkStr(name))
                        self.urls.append(checkStr(url))
                        self.pics.append(checkStr(pic))
                else:
                    regexcat = '#EXTINF.*?,(.*?)\\n(.*?)\\n'
                    match = re.compile(regexcat, re.DOTALL).findall(fpage)
                    for name, url in match:
                        if url.startswith('http'):
                            url = url.replace(' ', '%20')
                            url = url.replace('\\n', '')
                            if 'samsung' in self.url.lower() or config.plugins.stvcl.filter.value == True:
                                regexcat = '(.*?).m3u8'
                                match = re.compile(regexcat, re.DOTALL).findall(url)
                                for url in match:
                                    url = url + '.m3u8'
                            pic = pic
                            item = name + "###" + url + "###" + pic
                            print('url-name Items sort: ', item)
                            items.append(item)
                    items.sort()
                    for item in items:
                        name = item.split('###')[0]
                        url = item.split('###')[1]
                        pic = item.split('###')[2]

                        self.names.append(checkStr(name))
                        self.urls.append(checkStr(url))
                        self.pics.append(checkStr(pic))
                #####
                if config.plugins.stvcl.thumb.value == True:
                    self["live"].setText("WAIT PLEASE....")
                    self.gridmaint = eTimer()
                    try:
                        self.gridmaint.callback.append(self.gridpic)
                    except:
                        self.gridmaint_conn = self.gridmaint.timeout.connect(self.gridpic)
                    self.gridmaint.start(4000, True)
                    # self.session.open(GridMain, self.names, self.urls, self.pics)
                #####
                else:
                    m3ulist(self.names, self['list'])
                self["live"].setText('N.' + str(len(self.names)) + " Stream")

        except Exception as ex:
            print('error exception: ', ex)

    def gridpic(self):
        self.session.open(GridMain, self.names, self.urls, self.pics)
        self.close()

    def runChannel(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None or '':
            return
        else:
            self.pin = True
            if config.ParentalControl.configured.value:
                a = '+18', 'adult', 'hot', 'porn', 'sex', 'xxx'
                if any(s in str(self.names[idx]).lower() for s in a):
                    self.allow2()
                else:
                    self.pin = True
                    self.pinEntered2(True)
            else:
                self.pin = True
                self.pinEntered2(True)

    def allow2(self):
        from Screens.InputBox import PinInput
        self.session.openWithCallback(self.pinEntered2, PinInput, pinList = [config.ParentalControl.setuppin.value], triesEntry = config.ParentalControl.retries.servicepin, title = _("Please enter the parental control pin code"), windowTitle = _("Enter pin code"))

    def pinEntered2(self, result):
        if not result:
            self.pin = False
            self.session.open(openMessageBox, _("The pin code you entered is wrong."), type=openMessageBox.TYPE_ERROR, timeout=5)
        self.runChannel2()

    def runChannel2(self):
        if self.pin is False:
            return
        else:
            idx = self['list'].getSelectionIndex()
            name = self.names[idx]
            url = self.urls[idx]
            self.session.open(M3uPlay2, name, url)
            return

    def play2(self):
        if os.path.isfile("/usr/sbin/streamlinksrv"):
            idx = self['list'].getSelectionIndex()
            name = self.names[idx]
            url = self.urls[idx]
            url = url.replace(':', '%3a')
            print('In revolution url =', url)
            ref = '5002:0:1:0:0:0:0:0:0:0:' + 'http%3a//127.0.0.1%3a8088/' + str(url)
            sref = eServiceReference(ref)
            print('SREF: ', sref)
            sref.setName(name)
            self.session.open(M3uPlay2, name, sref)
            self.close()
        else:
            self.session.open(MessageBox, _('Install Streamlink first'), MessageBox.TYPE_INFO, timeout=5)

    def AdjUrlFavo(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None or '':
            return
        else:
            name = self.names[idx]
            url = self.urls[idx]
            regexcat = '(.*?).m3u8'
            match = re.compile(regexcat, re.DOTALL).findall(url)
            for url in match:
                url = url + '.m3u8'
            self.session.open(AddIpvStream, name, url)

class TvInfoBarShowHide():
    """ InfoBar show/hide control, accepts toggleShow and hide actions, might start
    fancy animations. """
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3
    skipToggleShow = False
    def __init__(self):
        self["ShowHideActions"] = ActionMap(["InfobarShowHideActions"], {"toggleShow": self.OkPressed,
         "hide": self.hide}, 0)
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.serviceStarted})
        self.__state = self.STATE_SHOWN
        self.__locked = 0
        self.hideTimer = eTimer()
        try:
            self.hideTimer_conn = self.hideTimer.timeout.connect(self.doTimerHide)
        except:
            self.hideTimer.callback.append(self.doTimerHide)
        self.hideTimer.start(5000, True)
        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)

    def serviceStarted(self):
        if self.execing:
            if config.usage.show_infobar_on_zap.value:
                self.doShow()

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()

    def __onHide(self):
        self.__state = self.STATE_HIDDEN

    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            self.hideTimer.stop()
            idx = config.usage.infobar_timeout.index
            if idx:
                self.hideTimer.start(idx * 1500, True)

    def doShow(self):
        self.hideTimer.stop()
        self.show()
        self.startHideTimer()

    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()

    def OkPressed(self):
        self.toggleShow()

    def toggleShow(self):
        if self.skipToggleShow:
            self.skipToggleShow = False
            return

        if self.__state == self.STATE_HIDDEN:
            self.show()
            self.hideTimer.stop()
        else:
            self.hide()
            self.startHideTimer()

    def lockShow(self):
        try:
            self.__locked += 1
        except:
            self.__locked = 0
        if self.execing:
            self.show()
            self.hideTimer.stop()
            self.skipToggleShow = False

    def unlockShow(self):
        try:
            self.__locked -= 1
        except:
            self.__locked = 0
        if self.__locked < 0:
            self.__locked = 0
        if self.execing:
            self.startHideTimer()

    def debug(obj, text = ""):
        print(text + " %s\n" % obj)

class M3uPlay2(InfoBarBase, InfoBarMenu, InfoBarSeek, InfoBarAudioSelection, InfoBarSubtitleSupport, InfoBarNotifications, TvInfoBarShowHide, Screen):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    screen_timeout = 5000
    def __init__(self, session, name, url):
        global SREF, streml
        Screen.__init__(self, session)
        self.session = session
        self.skinName = 'MoviePlayer'
        title = name
        streaml = False
        for x in InfoBarBase, \
                InfoBarMenu, \
                InfoBarSeek, \
                InfoBarAudioSelection, \
                InfoBarSubtitleSupport, \
                InfoBarNotifications, \
                TvInfoBarShowHide:
            x.__init__(self)
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect
        self['actions'] = ActionMap(['WizardActions',
         'MoviePlayerActions',
         'MovieSelectionActions',
         'MediaPlayerActions',
         'EPGSelectActions',
         'MediaPlayerSeekActions',
         'SetupActions',
         'ColorActions',
         'InfobarShowHideActions',
         'InfobarActions',
         'InfobarSeekActions'], {'leavePlayer': self.leavePlayer,
         'epg': self.showIMDB,
         'info': self.showIMDB,
         # 'info': self.cicleStreamType,
         'tv': self.cicleStreamType,
         'stop': self.leavePlayer,
         'cancel': self.leavePlayer,
         'back': self.leavePlayer}, -1)
        url = url.replace(':', '%3a')
        self.url = url
        self.name = name
        self.state = self.STATE_PLAYING
        SREF = self.session.nav.getCurrentlyPlayingServiceReference()
        if '8088' in str(self.url):
            self.onFirstExecBegin.append(self.slinkPlay)
        else:
            self.onFirstExecBegin.append(self.cicleStreamType)
        self.onClose.append(self.cancel)

    def showIMDB(self):
        TMDB = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('TMDB'))
        IMDb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('IMDb'))
        if os.path.exists(TMDB):
            from Plugins.Extensions.TMBD.plugin import TMBD
            text_clear = self.name
            text = charRemove(text_clear)
            self.session.open(TMBD, text, False)
        elif os.path.exists(IMDb):
            from Plugins.Extensions.IMDb.plugin import IMDB
            text_clear = self.name
            text = charRemove(text_clear)
            HHHHH = text
            self.session.open(IMDB, HHHHH)
        else:
            text_clear = self.name
            self.session.open(openMessageBox, text_clear, openMessageBox.TYPE_INFO)

    def slinkPlay(self, url):
        ref = str(url)
        ref = ref.replace(':', '%3a').replace(' ','%20')
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(self.name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def openPlay(self, servicetype, url):
        url = url.replace(':', '%3a').replace(' ','%20')
        ref = str(servicetype) + ':0:1:0:0:0:0:0:0:0:' + str(url)
        if streaml == True:
            ref = str(servicetype) + ':0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/' + str(url)
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(self.name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def cicleStreamType(self):
        global streaml
        streaml = False
        from itertools import cycle, islice
        self.servicetype = str(config.plugins.stvcl.services.value) +':0:1:0:0:0:0:0:0:0:'#  '4097'
        print('servicetype1: ', self.servicetype)
        url = str(self.url)
        if str(os.path.splitext(self.url)[-1]) == ".m3u8":
            if self.servicetype == "1":
                self.servicetype = "4097"
        currentindex = 0
        streamtypelist = ["4097"]
        # if "youtube" in str(self.url):
            # self.mbox = self.session.open(MessageBox, _('For Stream Youtube coming soon!'), MessageBox.TYPE_INFO, timeout=5)
            # return
        if os.path.exists("/usr/sbin/streamlinksrv"):
            streamtypelist.append("5002") #ref = '5002:0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/' + url
            streaml = True
        if os.path.exists("/usr/bin/gstplayer"):
            streamtypelist.append("5001")
        if os.path.exists("/usr/bin/exteplayer3"):
            streamtypelist.append("5002")
        if os.path.exists("/usr/bin/apt-get"):
            streamtypelist.append("8193")
        for index, item in enumerate(streamtypelist, start=0):
            if str(item) == str(self.servicetype):
                currentindex = index
                break
        nextStreamType = islice(cycle(streamtypelist), currentindex + 1, None)
        self.servicetype = str(next(nextStreamType))
        print('servicetype2: ', self.servicetype)
        self.openPlay(self.servicetype, url)

    def keyNumberGlobal(self, number):
        self['text'].number(number)

    def keyLeft(self):
        self['text'].left()

    def keyRight(self):
        self['text'].right()

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback != None:
            self.infoCallback()
        return

    def showAfterSeek(self):
        if isinstance(self, TvInfoBarShowHide):
            self.doShow()

    def cancel(self):
        if os.path.isfile('/tmp/hls.avi'):
            os.remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(SREF)
        if not self.new_aspect == self.init_aspect:
            try:
                self.setAspect(self.init_aspect)
            except:
                pass
        self.close()

    def leavePlayer(self):
        self.close()

class AddIpvStream(Screen):

    def __init__(self, session, name, url):
        self.session = session
        skin = skin_fold + '/AddIpvStream.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self['title'] = Label(_(title_plug))
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Ok'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.keyOk,
         'cancel': self.keyCancel,
         'green': self.keyOk,
         'red': self.keyCancel}, -2)
        self['statusbar'] = Label()
        self.list = []
        self['menu'] = MenuList([])
        self.mutableList = None
        self.servicelist = ServiceList(None)
        self.onLayoutFinish.append(self.createTopMenu)
        self.namechannel = name
        self.urlchannel = url
        return

    def initSelectionList(self):
        self.list = []
        self['menu'].setList(self.list)

    def createTopMenu(self):
        self.setTitle(_('Add Stream IPTV'))
        self.initSelectionList()
        self.list = []
        tmpList = []
        self.list = self.getBouquetList()
        self['menu'].setList(self.list)
        self['statusbar'].setText(_('Select the Bouquet and press OK to add'))

    def getBouquetList(self):
        self.service_types = service_types_tv
        if config.usage.multibouquet.value:
            self.bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
        else:
            self.bouquet_rootstr = '%s FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet' % self.service_types
        self.bouquet_root = eServiceReference(self.bouquet_rootstr)
        bouquets = []
        serviceHandler = eServiceCenter.getInstance()
        if config.usage.multibouquet.value:
            list = serviceHandler.list(self.bouquet_root)
            if list:
                while True:
                    s = list.getNext()
                    if not s.valid():
                        break
                    if s.flags & eServiceReference.isDirectory:
                        info = serviceHandler.info(s)
                        if info:
                            bouquets.append((info.getName(s), s))
                return bouquets
        else:
            info = serviceHandler.info(self.bouquet_root)
            if info:
                bouquets.append((info.getName(self.bouquet_root), self.bouquet_root))
            return bouquets
        return None

    def keyOk(self):
        if len(self.list) == 0:
            return
        self.name = ''
        self.url = ''
        self.session.openWithCallback(self.addservice, VirtualKeyBoard, title=_('Enter Name'), text=self.namechannel)

    def addservice(self, res):
        if res:
            self.url = res
            str = '4097:0:0:0:0:0:0:0:0:0:%s:%s' % (quote(self.url), quote(self.name))
            ref = eServiceReference(str)
            self.addServiceToBouquet(self.list[self['menu'].getSelectedIndex()][1], ref)
            self.close()

    def addServiceToBouquet(self, dest, service = None):
        mutableList = self.getMutableList(dest)
        if mutableList != None:
            if service is None:
                return
            if not mutableList.addService(service):
                mutableList.flushChanges()
        return

    def getMutableList(self, root = eServiceReference()):
        if self.mutableList != None:
            return self.mutableList
        else:
            serviceHandler = eServiceCenter.getInstance()
            if not root.valid():
                root = self.getRoot()
            list = root and serviceHandler.list(root)
            if list != None:
                return list.startEdit()
            return
            return

    def getRoot(self):
        return self.servicelist.getRoot()

    def keyCancel(self):
        self.close()

class OpenConfig(Screen, ConfigListScreen):
        def __init__(self, session):
            skin = skin_fold + '/OpenConfig.xml'
            f = open(skin, 'r')
            self.skin = f.read()
            f.close()
            Screen.__init__(self, session)
            self.setup_title = _("stvcl Config")
            self.onChangedEntry = [ ]
            self.list = []
            self.session = session
            info = '***YOUR SETUP***'
            self['title'] = Label(_(title_plug))
            self['Maintainer2'] = Label('%s' % Maintainer2)
            self['key_red'] = Button(_('Back'))
            self['key_green'] = Button(_('Save'))
            self["key_blue"] = Button(_('Empty Pic Cache'))
            self['key_yellow'] = Button('')
            self['key_yellow'].hide()
            # self["key_blue"].hide()
            self['text'] = Label(info)
            self["description"] = Label(_(''))
            self['actions'] = ActionMap(["SetupActions", "ColorActions", "VirtualKeyboardActions"  ], {
                'cancel': self.extnok,
                "red": self.extnok,
                "green": self.cfgok,
                "blue": self.cachedel,
                # 'yellow': self.msgupdt1,
                'showVirtualKeyboard': self.KeyText,
                'ok': self.Ok_edit,
            }, -2)

            ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
            self.createSetup()
            # self.onLayoutFinish.append(self.checkUpdate)
            self.onLayoutFinish.append(self.layoutFinished)
            if self.setInfo not in self['config'].onSelectionChanged:
                self['config'].onSelectionChanged.append(self.setInfo)

        def layoutFinished(self):
            self.setTitle(self.setup_title)

        def cachedel(self):
            fold = config.plugins.stvcl.cachefold.value + "stvcl"
            cmd = "rm -rf " + tvstrvl + "/*"
            if os.path.exists(fold):
                os.system(cmd)
            self.mbox = self.session.open(MessageBox, _('All cache fold are empty!'), MessageBox.TYPE_INFO, timeout=5)

        def createSetup(self):
            self.editListEntry = None
            self.list = []
            self.list.append(getConfigListEntry(_('IPTV bouquets location '), config.plugins.stvcl.bouquettop, _("Configure position of the bouquets of the converted lists")))
            self.list.append(getConfigListEntry(_('Player folder List <.m3u>:'), config.plugins.stvcl.pthm3uf, _("Folder path containing the .m3u files")))
            self.list.append(getConfigListEntry(_('Services Player Reference type'), config.plugins.stvcl.services, _("Configure Service Player Reference")))
            self.list.append(getConfigListEntry(_('Filter M3U link regex type'), config.plugins.stvcl.filter, _("Set On for line link m3u full")))
            self.list.append(getConfigListEntry(_('Show thumpics?'), config.plugins.stvcl.thumb,  _("Show Thumbpics ? Enigma restart required")))
            if config.plugins.stvcl.thumb.value == True:
                self.list.append(getConfigListEntry(_('Download thumpics?'), config.plugins.stvcl.thumbpic, _("Download thumpics in Player M3U (is very Slow)?")))
            self.list.append(getConfigListEntry(_('Folder Cache for Thumbpics:'), config.plugins.stvcl.cachefold, _("Configure position folder for temporary Thumbpics")))
            self.list.append(getConfigListEntry(_('Link in Extensions Menu:'), config.plugins.stvcl.strtext, _("Show Plugin in Extensions Menu")))
            self.list.append(getConfigListEntry(_('Link in Main Menu:'), config.plugins.stvcl.strtmain, _("Show Plugin in Main Menu")))
            self['config'].list = self.list
            self["config"].setList(self.list)
            self.setInfo()

        def setInfo(self):
            entry = str(self.getCurrentEntry())
            if entry == _('IPTV bouquets location '):
                self['description'].setText(_("Configure position of the bouquets of the converted lists"))
                return
            if entry == _('Player folder List <.m3u>:'):
                self['description'].setText(_("Folder path containing the .m3u files"))
                return
            if entry == _('Filter M3U link regex type'):
                self['description'].setText(_("Set On for line link m3u full"))
                return
            if entry == _('Services Player Reference type'):
                self['description'].setText(_("Configure Service Player Reference"))
                return
            if entry == _('Show thumpics?'):
                self['description'].setText(_("Show Thumbpics ? Enigma restart required"))
                return
            if entry == _('Download thumpics?'):
                self['description'].setText(_("Download thumpics in Player M3U (is very Slow)?"))
                return
            if entry == _('Folder Cache for Thumbpics:'):
                self['description'].setText(_("Configure position folder for temporary Thumbpics"))
                return
            if entry == _('Link in Extensions Menu:'):
                self['description'].setText(_("Show Plugin in Extensions Menu"))
                return
            if entry == _('Link in Main Menu:'):
                self['description'].setText(_("Show Plugin in Main Menu"))
            return

        def changedEntry(self):
            sel = self['config'].getCurrent()
            for x in self.onChangedEntry:
                x()
            try:
                if isinstance(self['config'].getCurrent()[1], ConfigEnableDisable) or isinstance(self['config'].getCurrent()[1], ConfigYesNo) or isinstance(self['config'].getCurrent()[1], ConfigSelection):
                    self.createSetup()
            except:
                pass

        def getCurrentEntry(self):
            return self['config'].getCurrent() and self['config'].getCurrent()[0] or ''

        def getCurrentValue(self):
            return self['config'].getCurrent() and str(self['config'].getCurrent()[1].getText()) or ''

        def createSummary(self):
            from Screens.Setup import SetupSummary
            return SetupSummary

        def Ok_edit(self):
            ConfigListScreen.keyOK(self)
            sel = self['config'].getCurrent()[1]
            if sel and sel == config.plugins.stvcl.pthm3uf:
                self.setting = 'pthm3uf'
                self.openDirectoryBrowser(config.plugins.stvcl.pthm3uf.value)
            elif sel and sel == config.plugins.stvcl.cachefold:
                self.setting = 'cachefold'
                self.openDirectoryBrowser(config.plugins.stvcl.cachefold.value)
            else:
                pass

        def openDirectoryBrowser(self, path):
            try:
                self.session.openWithCallback(
                 self.openDirectoryBrowserCB,
                 LocationBox,
                 windowTitle=_('Choose Directory:'),
                 text=_('Choose Directory'),
                 currDir=str(path),
                 bookmarks=config.movielist.videodirs,
                 autoAdd=False,
                 editDir=True,
                 inhibitDirs=['/bin', '/boot', '/dev', '/home', '/lib', '/proc', '/run', '/sbin', '/sys', '/var'],
                 minFree=15)
            except Exception as ex:
                print(ex)

        def openDirectoryBrowserCB(self, path):
            if path != None:
                if self.setting == 'pthm3uf':
                    config.plugins.stvcl.pthm3uf.setValue(path)
                elif self.setting == 'cachefold':
                    config.plugins.stvcl.cachefold.setValue(path)
            return

        def cfgok(self):
            self.save()

        def save(self):
            if not os.path.exists(config.plugins.stvcl.pthm3uf.value):
                self.mbox = self.session.open(openMessageBox, _('M3u list folder not detected!'), openMessageBox.TYPE_INFO, timeout=4)
                return
            if self['config'].isChanged():
                for x in self['config'].list:
                    x[1].save()
                configfile.save()
                plugins.clearPluginList()
                plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
                self.mbox = self.session.open(openMessageBox, _('Settings saved correctly!'), openMessageBox.TYPE_INFO, timeout=5)
                self.close()
            else:
                self.close()

        def VirtualKeyBoardCallback(self, callback = None):
            if callback != None and len(callback):
                self["config"].getCurrent()[1].setValue(callback)
                self["config"].invalidate(self["config"].getCurrent())

        def KeyText(self):
            sel = self['config'].getCurrent()
            if sel:
                self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self['config'].getCurrent()[0], text=self['config'].getCurrent()[1].value)

        def cancelConfirm(self, result):
            if not result:
                return
            for x in self['config'].list:
                x[1].cancel()
            self.close()

        def extnok(self):
            if self['config'].isChanged():
                self.session.openWithCallback(self.cancelConfirm, openMessageBox, _('Really close without saving the settings?'))
            else:
                self.close()

class openMessageBox(Screen):
    TYPE_YESNO = 0
    TYPE_INFO = 1
    TYPE_WARNING = 2
    TYPE_ERROR = 3
    TYPE_MESSAGE = 4

    def __init__(self, session, text, type = TYPE_YESNO, timeout = -1, close_on_any_key = False, default = True, enable_input = True, msgBoxID = None, picon = None, simple = False, list = [], timeout_default = None):
        self.type = type
        self.session = session
        skin = skin_fold + '/OpenMessageBox.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self.msgBoxID = msgBoxID
        self['text'] = Label(text)
        self['Text'] = StaticText(text)
        self['selectedChoice'] = StaticText()
        self.text = text
        self.close_on_any_key = close_on_any_key
        self.timeout_default = timeout_default
        self['ErrorPixmap'] = Pixmap()
        self['QuestionPixmap'] = Pixmap()
        self['InfoPixmap'] = Pixmap()
        self['WarningPixmap'] = Pixmap()
        self.timerRunning = False
        self.initTimeout(timeout)
        picon = picon or type
        if picon != self.TYPE_ERROR:
                self['ErrorPixmap'].hide()
        if picon != self.TYPE_YESNO:
                self['QuestionPixmap'].hide()
        if picon != self.TYPE_INFO:
                self['InfoPixmap'].hide()
        if picon != self.TYPE_WARNING:
                self['WarningPixmap'].hide()
        self.title = self.type < self.TYPE_MESSAGE and [_('Question'),
         _('Information'),
         _('Warning'),
         _('Error')][self.type] or _('Message')
        if type == self.TYPE_YESNO:
            if list:
                self.list = list
            elif default == True:
                self.list = [(_('Yes'), True), (_('No'), False)]
            else:
                self.list = [(_('No'), False), (_('Yes'), True)]
        else:
            self.list = []
        self['list'] = MenuList(self.list)

        if self.list:
            self['selectedChoice'].setText(self.list[0][0])
        else:
            self['list'].hide()
        if enable_input:
            self['actions'] = ActionMap(['MsgBoxActions', 'DirectionActions'], {'cancel': self.cancel,
             'ok': self.ok,
             'alwaysOK': self.alwaysOK,
             'up': self.up,
             'down': self.down,
             'left': self.left,
             'right': self.right,
             'upRepeated': self.up,
             'downRepeated': self.down,
             'leftRepeated': self.left,
             'rightRepeated': self.right}, -1)
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(self.title)

    def initTimeout(self, timeout):
        self.timeout = timeout
        if timeout > 0:
            self.timer = eTimer()
            if os.path.exists('/var/lib/dpkg/status'):
                self.timer_conn = self.timer.timeout.connect(self.timerTick)
            else:
                self.timer.callback.append(self.timerTick)
            self.onExecBegin.append(self.startTimer)
            self.origTitle = None
            if self.execing:
                self.timerTick()
            else:
                self.onShown.append(self.__onShown)
            self.timerRunning = True
        else:
            self.timerRunning = False
        return

    def __onShown(self):
        self.onShown.remove(self.__onShown)
        self.timerTick()

    def startTimer(self):
            self.timer.start(1000)

    def stopTimer(self):
        if self.timerRunning:
            del self.timer
            self.onExecBegin.remove(self.startTimer)
            self.setTitle(self.origTitle)
            self.timerRunning = False

    def timerTick(self):
        if self.execing:
            self.timeout -= 1
            if self.origTitle is None:
                self.origTitle = self.instance.getTitle()
            self.setTitle(self.origTitle + ' (' + str(self.timeout) + ')')
            if self.timeout == 0:
                self.timer.stop()
                self.timerRunning = False
                self.timeoutCallback()
        return

    def timeoutCallback(self):
        if self.timeout_default != None:
            self.close(self.timeout_default)
        else:
            self.ok()
        return

    def cancel(self):
        self.close(False)

    def ok(self):
        if self.list:
            self.close(self['list'].getCurrent()[1])
        else:
            self.close(True)

    def alwaysOK(self):
        self.close(True)

    def up(self):
        self.move(self['list'].instance.moveUp)

    def down(self):
        self.move(self['list'].instance.moveDown)

    def left(self):
        self.move(self['list'].instance.pageUp)

    def right(self):
        self.move(self['list'].instance.pageDown)

    def move(self, direction):
        if self.close_on_any_key:
            self.close(True)
        self['list'].instance.moveSelection(direction)
        if self.list:
            self['selectedChoice'].setText(self['list'].getCurrent()[0])
        self.stopTimer()

    def __repr__(self):
        return str(type(self)) + '(' + self.text + ')'

def checks():
    chekin= False
    if checkInternet():
            chekin = True
    return

def main(session, **kwargs):
    if checks:
        add_skin_font()
        session.open(OpenScript)
    else:
        session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)

def cfgmain(menuid):
    if menuid == 'mainmenu':
        return [('S.T.V.C.L.',
         main,
         'Smart TV Channels List',
         44)]
    else:
        return []

def Plugins(**kwargs):
    piclogox = 'logo.png'
    if not os.path.exists('/var/lib/dpkg/status'):
        piclogox = skin_fold + '/logo.png'
    extDescriptor = PluginDescriptor(name=name_plug, description=_(title_plug), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon=piclogox, fnc=main)
    mainDescriptor = PluginDescriptor(name=name_plug, description=_(title_plug), where=PluginDescriptor.WHERE_MENU, icon=piclogox, fnc=cfgmain)
    result = [PluginDescriptor(name=name_plug, description=_(title_plug), where=[PluginDescriptor.WHERE_PLUGINMENU], icon=piclogox, fnc=main)]
    if config.plugins.stvcl.strtext.value:
        result.append(extDescriptor)
    if config.plugins.stvcl.strtmain.value:
        result.append(mainDescriptor)
    return result

def charRemove(text):
    char = ["1080p",
     "2018",
     "2019",
     "2020",
     "2021",
     "480p",
     "4K",
     "720p",
     "ANIMAZIONE",
     "APR",
     "AVVENTURA",
     "BIOGRAFICO",
     "BDRip",
     "BluRay",
     "CINEMA",
     "COMMEDIA",
     "DOCUMENTARIO",
     "DRAMMATICO",
     "FANTASCIENZA",
     "FANTASY",
     "FEB",
     "GEN",
     "GIU",
     "HDCAM",
     "HDTC",
     "HDTS",
     "LD",
     "MAFIA",
     "MAG",
     "MARVEL",
     "MD",
     "ORROR",
     "NEW_AUDIO",
     "POLIZ",
     "R3",
     "R6",
     "SD",
     "SENTIMENTALE",
     "TC",
     "TEEN",
     "TELECINE",
     "TELESYNC",
     "THRILLER",
     "Uncensored",
     "V2",
     "WEBDL",
     "WEBRip",
     "WEB",
     "WESTERN",
     "-",
     "_",
     ".",
     "+",
     "[",
     "]"]

    myreplace = text
    for ch in char:
            myreplace = myreplace.replace(ch, "").replace("  ", " ").replace("       ", " ").strip()
    return myreplace
