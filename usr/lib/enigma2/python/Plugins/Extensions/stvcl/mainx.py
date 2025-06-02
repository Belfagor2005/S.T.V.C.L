#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
# Info http://t.me/tivustream
# ****************************************
# *        coded by Lululla              *
# *                                      *
# *             02/09/2024               *
# ****************************************

# === Standard Library ===
import codecs
from json import loads
from os import makedirs, listdir, rename, remove, stat, system as os_system
from re import compile, DOTALL, sub
from sys import version_info
from datetime import datetime
from os.path import exists, join, sep, isfile, splitext
from time import sleep

# === Third-party Libraries ===
from PIL import Image
from requests import get, exceptions
from requests.exceptions import HTTPError as httperror
from twisted.internet.reactor import callInThread
from twisted.web.client import downloadPage
from six import ensure_binary

# === Enigma2 Core ===
from enigma import (
    RT_VALIGN_CENTER,
    RT_HALIGN_LEFT,
    eListboxPythonMultiContent,
    eTimer,
    ePicLoad,
    eServiceCenter,
    eServiceReference,
    loadPNG,
    gFont,
    iPlayableService,
    getDesktop,
)

# === Enigma2 Components ===
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap, MovingPixmap
from Components.PluginComponent import plugins
from Components.ProgressBar import ProgressBar
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.ServiceList import ServiceList
from Components.Sources.StaticText import StaticText
from Components.config import (
    config,
    ConfigSubsection,
    ConfigSelection,
    getConfigListEntry,
    ConfigDirectory,
    ConfigYesNo,
    configfile,
    ConfigEnableDisable,
)

# === Enigma2 Screens ===
from Screens.InfoBarGenerics import (
    InfoBarMenu,
    InfoBarSeek,
    InfoBarAudioSelection,
    InfoBarNotifications,
    InfoBarSubtitleSupport,
)
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard

# === Enigma2 Tools ===
from Tools.Directories import SCOPE_PLUGINS, resolveFilename
from Tools.Downloader import downloadWithProgress

# === Moduli locali ===
from . import _, paypal, scramble, installer_url, developer_url
from . import Utils
from . import html_conv
from .Console import Console as xConsole

# === Python 2/3 Compatibility ===
PY3 = False
try:
    from urllib.parse import quote, urlparse
    from urllib.request import Request, urlopen
    from urllib.error import URLError
    import urllib.request as urllib2
    PY3 = True
    unicode = str
except ImportError:
    from urllib import quote
    from urlparse import urlparse
    from urllib2 import Request, urlopen, URLError
    import urllib2


if version_info >= (2, 7, 9):
    try:
        import ssl
        sslContext = ssl._create_unverified_context()
    except BaseException:
        sslContext = None

try:
    from twisted.internet import ssl
    from twisted.internet._sslverify import ClientTLSOptions
    sslverify = True
except BaseException:
    sslverify = False

if sslverify:
    class SNIFactory(ssl.ClientContextFactory):
        def __init__(self, hostname=None):
            self.hostname = hostname

        def getContext(self):
            ctx = self._contextFactory(self.method)
            if self.hostname:
                ClientTLSOptions(self.hostname, ctx)
            return ctx


def ssl_urlopen(url):
    if sslContext:
        return urlopen(url, context=sslContext)
    else:
        return urlopen(url)


def downloadFilest(url, target):
    try:
        if isinstance(url, bytes):
            url = url.decode('utf-8')  # Decodifica se è una byte string
        req = Request(url)
        req.add_header(
            'User-Agent',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        # response = ssl_urlopen(req)
        response = urlopen(req, None, 15)
        with open(target, 'w') as output:
            if PY3:
                output.write(response.read().decode('utf-8'))
            else:
                output.write(response.read())
            print('response: ', response)
        return True
    except httperror:
        print('HTTP Error code: ', httperror.code)
    except URLError as e:
        print('URL Error: ', e.reason)
    except ValueError as ve:
        print("Errore di valore:", ve)


# ================
global Path_Movies, defpic
# ================
sessions = []
currversion = '1.4'
title_plug = 'Smart Tv Channels List'
name_plug = '..:: Smart Tv Channels List  V.%s ::.. ' % currversion
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('stvcl'))
Maintainer2 = 'Maintener @Lululla'
dir_enigma2 = '/etc/enigma2/'
service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 31) || (type == 134) || (type == 195)'
defpic = join(plugin_path, 'res/pics/default.png')
dblank = join(plugin_path, 'res/pics/blankL.png')
Panel_list = [('S.T.V.C.L.')]

modechoices = [("4097", _("ServiceMp3(4097)")),
               ("1", _("Hardware(1)"))]
if exists("/usr/bin/gstplayer"):
    modechoices.append(("5001", _("Gstreamer(5001)")))
if exists("/usr/bin/exteplayer3"):
    modechoices.append(("5002", _("Exteplayer3(5002)")))
if exists("/usr/sbin/streamlinksrv"):
    modechoices.append(("5002", _("Streamlink(5002)")))
if exists("/usr/bin/apt-get"):
    modechoices.append(("8193", _("eServiceUri(8193)")))

config.plugins.stvcl = ConfigSubsection()
cfg = config.plugins.stvcl
cfg.pthm3uf = ConfigDirectory(default='/media/hdd/movie/')
cfg.cachefold = ConfigDirectory('/media/hdd/', False)
cfg.bouquettop = ConfigSelection(default='Bottom', choices=['Bottom', 'Top'])
cfg.services = ConfigSelection(default='4097', choices=modechoices)
cfg.filterx = ConfigYesNo(default=False)
cfg.strtext = ConfigYesNo(default=True)
cfg.strtmain = ConfigYesNo(default=True)
cfg.thumb = ConfigYesNo(default=False)
cfg.thumbpic = ConfigYesNo(default=False)

try:
    from Components.UsageConfig import defaultMoviePath
    downloadpath = defaultMoviePath()
    cfg.pthm3uf = ConfigDirectory(default=downloadpath)
    # cfg.cachefold = str(cfg.pthm3uf.value)
except BaseException:
    if exists("/usr/bin/apt-get"):
        cfg.pthm3uf = ConfigDirectory(default='/media/hdd/movie/')
        # cfg.cachefold = str(cfg.pthm3uf.value)


# tvstrvl = str(cfg.cachefold.value).replace('movie', 'stvcl')
tvstrvl = join(cfg.cachefold.value, "stvcl")
tmpfold = join(tvstrvl, "tmp")
picfold = join(tvstrvl, "pic")

Path_Movies = str(cfg.pthm3uf.value)
if not Path_Movies.endswith(sep):
    Path_Movies += sep

for folder in [tvstrvl, tmpfold, picfold]:
    if not exists(folder):
        makedirs(folder)
try:
    aspect_manager = Utils.AspectManager()
    current_aspect = aspect_manager.get_current_aspect()
except BaseException:
    pass

screenwidth = getDesktop(0).size()
if screenwidth.width() == 2560:
    skin_path = plugin_path + '/res/skins/uhd/'
    defpic = plugin_path + '/res/pics/defaultL.png'

elif screenwidth.width() == 1920:
    skin_path = plugin_path + '/res/skins/fhd/'
    defpic = plugin_path + '/res/pics/defaultL.png'
else:
    skin_path = plugin_path + '/res/skins/hd/'
    defpic = plugin_path + '/res/pics/default.png'
if exists('/var/lib/dpkg/status'):
    skin_path = join(skin_path, 'dreamOs')


# ================Gui list
class mainList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        if screenwidth.width() == 2560:
            self.l.setItemHeight(450)
            textfont = int(90)
            self.l.setFont(0, gFont('Regular', textfont))
        elif screenwidth.width() == 1920:
            self.l.setItemHeight(370)
            textfont = int(70)
            self.l.setFont(0, gFont('Regular', textfont))
        else:
            self.l.setItemHeight(240)
            textfont = int(50)
            self.l.setFont(0, gFont('Regular', textfont))


class tvList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        width = screenwidth.width()
        if width == 2560:
            self.l.setItemHeight(60)
            self.l.setFont(0, gFont("Regular", 42))
        elif width == 1920:
            self.l.setItemHeight(50)
            self.l.setFont(0, gFont("Regular", 30))
        else:
            self.l.setItemHeight(45)
            self.l.setFont(0, gFont("Regular", 24))


def m3ulistEntry(download):
    res = [download]
    png = join(plugin_path, "res/pics/setting2.png")
    width = screenwidth.width()
    if width == 2560:
        res.append(
            MultiContentEntryPixmapAlphaTest(
                pos=(
                    5, 5), size=(
                    50, 50), png=loadPNG(png)))
        res.append(
            MultiContentEntryText(
                pos=(
                    90,
                    0),
                size=(
                    1200,
                    50),
                font=0,
                text=download,
                flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    elif width == 1920:
        res.append(
            MultiContentEntryPixmapAlphaTest(
                pos=(
                    5, 5), size=(
                    50, 50), png=loadPNG(png)))
        res.append(
            MultiContentEntryText(
                pos=(
                    70,
                    0),
                size=(
                    1000,
                    50),
                font=0,
                text=download,
                flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(
            MultiContentEntryPixmapAlphaTest(
                pos=(
                    5, 0), size=(
                    50, 50), png=loadPNG(png)))
        res.append(
            MultiContentEntryText(
                pos=(
                    65,
                    0),
                size=(
                    500,
                    45),
                font=0,
                text=download,
                flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def m3ulist(data, list):
    mlist = []
    for name in data:
        mlist.append(m3ulistEntry(name))
    list.setList(mlist)


def tvListEntry(name, png):
    res = [name]
    png1 = join(plugin_path, "res/pics/defaultL.png")
    png2 = join(plugin_path, "res/pics/default.png")
    width = screenwidth.width()
    if width == 2560:
        res.append(
            MultiContentEntryPixmapAlphaTest(
                pos=(
                    5, 5), size=(
                    320, 450), png=loadPNG(png1)))
        res.append(
            MultiContentEntryText(
                pos=(
                    400,
                    5),
                size=(
                    1200,
                    70),
                font=0,
                text=name,
                flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    elif width == 1920:
        res.append(
            MultiContentEntryPixmapAlphaTest(
                pos=(
                    5, 5), size=(
                    250, 370), png=loadPNG(png1)))
        res.append(
            MultiContentEntryText(
                pos=(
                    280,
                    5),
                size=(
                    1000,
                    70),
                font=0,
                text=name,
                flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(
            MultiContentEntryPixmapAlphaTest(
                pos=(
                    3, 3), size=(
                    165, 240), png=loadPNG(png2)))
        res.append(
            MultiContentEntryText(
                pos=(
                    175,
                    3),
                size=(
                    500,
                    50),
                font=0,
                text=name,
                flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def returnIMDB(text_clear):
    TMDB = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('TMDB'))
    tmdb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('tmdb'))
    IMDb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('IMDb'))
    text = html_conv.html_unescape(text_clear)
    if exists(TMDB):
        try:
            from Plugins.Extensions.TMBD.plugin import TMBD
            _session.open(TMBD.tmdbScreen, text, 0)
        except Exception as e:
            print("[XCF] Tmdb: ", str(e))
        return True

    elif exists(tmdb):
        try:
            from Plugins.Extensions.tmdb.plugin import tmdb
            _session.open(tmdb.tmdbScreen, text, 0)
        except Exception as e:
            print("[XCF] Tmdb: ", str(e))
        return True

    elif exists(IMDb):
        try:
            from Plugins.Extensions.IMDb.plugin import main as imdb
            imdb(_session, text)
        except Exception as e:
            print("[XCF] imdb: ", str(e))
        return True
    else:
        _session.open(MessageBox, text, MessageBox.TYPE_INFO)
        return True
    return False


class StvclMain(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = join(skin_path, 'StvclMain.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self['list'] = mainList([])
        self.icount = 0
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self.setTitle(name_plug)
        self['title'] = Label(name_plug)
        self['Maintainer2'] = Label(Maintainer2)
        self['path'] = Label(_('Folder path %s' % str(Path_Movies)))
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button()
        self['key_yellow'] = Button(_('Update'))
        self["key_blue"] = Button(_('Remove'))
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self.Update = False
        self["actions"] = ActionMap(["OkCancelActions",
                                     "DirectionActions",
                                     "HotkeyActions",
                                     "InfobarEPGActions",
                                     "ChannelSelectBaseActions",
                                     "MenuActions"],
                                    {"ok": self.okRun,
                                     "menu": self.scsetup,
                                     "back": self.exit,
                                     "cancel": self.exit,
                                     "red": self.exit,
                                     "green": self.update_dev,
                                     "blue": self.msgdeleteBouquets,
                                     "yellow": self.update_me,
                                     "yellow_long": self.update_dev,
                                     "info_long": self.update_dev,
                                     "infolong": self.update_dev,
                                     "showEventInfoPlugin": self.update_dev,
                                     },
                                    -1)
        self.timer = eTimer()
        if exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.check_vers)
        else:
            self.timer.callback.append(self.check_vers)
        self.timer.start(200, True)
        self.onLayoutFinish.append(self.updateMenuList)

    def check_vers(self):
        remote_version = "0.0"
        remote_changelog = ""

        # Build request using base64-decoded installer URL
        req = Utils.Request(
            Utils.b64decoder(installer_url), headers={
                "User-Agent": "Mozilla/5.0"})

        try:
            page = Utils.urlopen(req).read()
            data = page.decode("utf-8") if PY3 else page.encode("utf-8")

            if data:
                lines = data.split("\n")
                for line in lines:
                    if line.startswith("version"):
                        # Expected format: version='1.0'
                        parts = line.split("'")
                        if len(parts) > 1:
                            remote_version = parts[1]
                    if line.startswith("changelog"):
                        parts = line.split("'")
                        if len(parts) > 1:
                            remote_changelog = parts[1]
                        break  # Stop reading after changelog

            self.new_version = remote_version
            self.new_changelog = remote_changelog

            # Compare with current version
            if currversion < remote_version:
                self.Update = True
                self["key_yellow"].show()
                self.session.open(
                    MessageBox,
                    _("New version %s is available\n\nChangelog: %s\n\nPress info_long or yellow_long button to start force updating.") %
                    (self.new_version,
                     self.new_changelog),
                    MessageBox.TYPE_INFO,
                    timeout=5)
        except Exception as e:
            self.session.open(
                MessageBox, _("Error checking version: %s") %
                str(e), MessageBox.TYPE_ERROR, timeout=5)

    def update_me(self):
        # Check if an update is available
        if getattr(self, "Update", False) is True:
            self.session.openWithCallback(
                self.install_update,
                MessageBox,
                _("New version %s is available.\n\nChangelog: %s\n\nDo you want to install it now?") %
                (self.new_version,
                 self.new_changelog),
                MessageBox.TYPE_YESNO)
        else:
            self.session.open(
                MessageBox,
                _("Congrats! You already have the latest version..."),
                MessageBox.TYPE_INFO,
                timeout=4
            )

    def update_dev(self):
        try:
            req = Utils.Request(
                Utils.b64decoder(developer_url), headers={
                    "User-Agent": "Mozilla/5.0"})
            page = Utils.urlopen(req).read()

            # Decode and parse JSON
            if PY3:
                data = loads(page.decode("utf-8"))
            else:
                data = loads(page)

            remote_date = data.get("pushed_at", "")
            if remote_date:
                strp_remote_date = datetime.strptime(
                    remote_date, "%Y-%m-%dT%H:%M:%SZ")
                formatted_date = strp_remote_date.strftime("%Y-%m-%d")

                self.session.openWithCallback(
                    self.install_update,
                    MessageBox,
                    _("Do you want to install update ( %s ) now?") %
                    formatted_date,
                    MessageBox.TYPE_YESNO)
            else:
                raise ValueError("Missing 'pushed_at' in JSON data")

        except Exception as e:
            self.session.open(
                MessageBox,
                _("Error checking developer version: %s") % str(e),
                MessageBox.TYPE_ERROR,
                timeout=5
            )

    def install_update(self, answer=False):
        if answer:
            # Execute update command using shell script from decoded
            # installer_url
            cmd1 = 'wget -q "--no-check-certificate" ' + \
                Utils.b64decoder(installer_url) + ' -O - | /bin/sh'
            self.session.open(
                xConsole,
                _("Upgrading..."),
                cmdlist=[cmd1],
                finishedCallback=self.myCallback,
                closeOnSuccess=False
            )
        else:
            self.session.open(
                MessageBox,
                _("Update Aborted!"),
                MessageBox.TYPE_INFO,
                timeout=3
            )

    def myCallback(self, result=None):
        print("Update finished. Result:", result)

    def updateMenuList(self):
        # Clear current menu list safely
        self.menu_list = []

        list = []
        png = join(plugin_path, "res/pics/setting.png")

        for x in Panel_list:
            list.append(tvListEntry(x, png))
            self.menu_list.append(x)

        self["key_green"].show()
        self["key_blue"].show()
        self["list"].setList(list)

    def okRun(self):
        self.keyNumberGlobalCB(self['list'].getSelectedIndex())

    def keyNumberGlobalCB(self, idx):
        sel = self.menu_list[idx]
        url = ''
        if sel == ("S.T.V.C.L."):
            url = Utils.b64decoder(scramble)
        else:
            return
        self.downlist(sel, url)

    def msgdeleteBouquets(self):
        self.session.openWithCallback(
            self.deleteBouquets,
            MessageBox,
            _("Remove all S.T.V.C.L. Favorite Bouquet ?"),
            MessageBox.TYPE_YESNO,
            timeout=5,
            default=True)

    def deleteBouquets(self, result):
        """
        Clean up routine to remove HasBahCa Favorites from Enigma2 bouquets.
        If confirmed (result is True), it:
        - Deletes all userbouquet files with 'stvcl_'.
        - Removes backup files named 'bouquets.tv.bak'.
        - Renames 'bouquets.tv' to 'bouquets.tv.bak'.
        - Rewrites 'bouquets.tv' excluding lines with '.stvcl_'.
        - Reloads bouquet list.
        """
        if result:
            try:
                # Remove relevant bouquet files
                for fname in listdir(dir_enigma2):
                    if "userbouquet.stvcl_" in fname or "bouquets.tv.bak" in fname:
                        Utils.purge(dir_enigma2, fname)

                # Backup original bouquets.tv
                rename(
                    join(dir_enigma2, "bouquets.tv"),
                    join(dir_enigma2, "bouquets.tv.bak")
                )

                # Create new bouquets.tv excluding HasBahCa entries
                with open(join(dir_enigma2, "bouquets.tv"), "w+") as tvfile, \
                        open(join(dir_enigma2, "bouquets.tv.bak")) as bakfile:
                    for line in bakfile:
                        if ".stvcl_" not in line:
                            tvfile.write(line)

                # Show success message and reload bouquets
                self.mbox = self.session.open(
                    MessageBox,
                    _("HasBahCa Favorites List have been removed"),
                    MessageBox.TYPE_INFO,
                    timeout=5
                )
                Utils.ReloadBouquets()

            except Exception as ex:
                print("Error deleting bouquets:", str(ex))
                raise

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (
            recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def check(self, fplug):
        self.downloading = False
        self['progresstext'].text = ''
        self.progclear = 0
        self['progress'].setValue(self.progclear)
        self["progress"].hide()

    def showError(self, error):
        self.downloading = False
        self.session.open(
            MessageBox,
            _('Download Failed!!!'),
            MessageBox.TYPE_INFO,
            timeout=5)

    def downlist(self, sel, url):
        """
        Downloads an M3U playlist from the given URL and opens it in ListM3u1.
        """
        global in_tmp
        try:
            namem3u = str(sel)
            content = Utils.checkStr(url.strip())
            if PY3:
                content.encode()  # Not used afterwards, can be removed if unnecessary

            print("urlmm33uu", content)

            # Sanitize filename
            # Replace forbidden characters
            fileTitle = sub(r'[<>:"/\\|?*\[\]]', '_', namem3u)
            # Replace spaces and symbols
            fileTitle = sub(r'[\s\(\)#\'\+\!&]', '_', fileTitle)
            # Normalize underscores and lowercase
            fileTitle = sub(r'_+', '_', fileTitle).strip('_').lower()

            # Final file path
            in_tmp = join(Path_Movies, fileTitle + '.m3u')

            # Remove existing file
            if isfile(in_tmp):
                remove(in_tmp)

            # Download new file
            downloadFilest(content, in_tmp)
            sleep(3)  # Optional: consider using async or a callback for better UX

            # Open the downloaded list
            self.session.open(ListM3u1, namem3u, content)

        except Exception as e:
            print("Error downloading list:", str(e))

    def scsetup(self):
        self.session.open(OpenConfig)

    def exit(self):
        Utils.deletetmp()
        self.close()


class ListM3u1(Screen):
    def __init__(self, session, namem3u, url):
        Screen.__init__(self, session)
        self.session = session
        skin = join(skin_path, 'ListM3u.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.list = []
        self['list'] = tvList([])
        global SREF
        SREF = self.session.nav.getCurrentlyPlayingServiceReference()
        self['title'] = Label(title_plug + ' ' + namem3u)
        self['Maintainer2'] = Label(Maintainer2)
        self['path'] = Label(_('Folder path %s' % str(Path_Movies)))
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self.convert = False
        self.url = url
        self.name = namem3u
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Select'))
        self['key_yellow'] = Button()
        self["key_blue"] = Button()
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['actions'] = ActionMap(
            [
                'OkCancelActions', 'ColorActions', 'ButtonSetupActions', 'DirectionActions'], {
                'cancel': self.cancel, 'ok': self.runList}, -2)

        if not exists(Path_Movies):
            self.mbox = self.session.open(
                MessageBox,
                _('Check in your Config Plugin - Path Movie'),
                MessageBox.TYPE_INFO,
                timeout=5)
            self.scsetup()
        # self.onFirstExecBegin.append(self.openList)
        # sleep(3)
        self.timer = eTimer()
        if exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.openList)
        else:
            self.timer.callback.append(self.openList)
        self.timer.start(200, True)
        # self.onLayoutFinish.append(self.openList2)
        self.onLayoutFinish.append(self.passing)

    def passing(self):
        pass

    def scsetup(self):
        self.session.openWithCallback(self.close, OpenConfig)

    def openList(self):
        # initialize lists
        self.names = []
        self.urls = []

        try:
            # prepare and send HTTP request
            req = urllib2.Request(self.url)
            req.add_header(
                "User-Agent",
                "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) "
                "Gecko/20080404 Firefox/2.0.0.14"
            )
            with urllib2.urlopen(req, timeout=15) as response:
                content = response.read()

            # decode bytes to unicode if necessary
            if isinstance(content, bytes):
                content = content.decode("utf-8")

            # add static Australian cities
            static_entries = [
                ("Adelaide", "https://i.mjh.nz/au/Adelaide/"),
                ("Brisbane", "https://i.mjh.nz/au/Brisbane/"),
                ("Canberra", "https://i.mjh.nz/au/Canberra/"),
                ("Darwin", "https://i.mjh.nz/au/Darwin/"),
                ("Hobart", "https://i.mjh.nz/au/Hobart/"),
                ("Melbourne", "https://i.mjh.nz/au/Melbourne/"),
                ("Perth", "https://i.mjh.nz/au/Perth/"),
                ("Sydney", "https://i.mjh.nz/au/Sydney/"),
                ("Au All", "https://i.mjh.nz/au/all")
            ]
            for name, url in static_entries:
                self.names.append(name)
                self.urls.append(url)

            # find all <a href="..."> links
            link_pattern = r"<a href=\"(.*?)\">"
            matches = compile(link_pattern, DOTALL).findall(content)

            for rel in matches:
                # skip parent dirs and donation/support links
                if ".." in rel or "DONATE" in rel or "SUPPORT" in rel:
                    continue

                # build full URL and sanitize
                full_url = self.url + rel
                clean_url = Utils.checkStr(full_url.strip())

                # derive a name from the relative path
                name = rel.strip("/").strip()
                clean_name = Utils.checkStr(name)

                self.urls.append(clean_url)
                self.names.append(clean_name)

            # populate the UI list and show the green key
            m3ulist(self.names, self["list"])
            self["key_green"].show()

        except Exception as e:
            # print error for debugging
            print("Error in openList:", e)

    def runList(self):
        i = len(self.names)
        if i < 0 or i >= len(self.names):
            return
        idx = self["list"].getSelectionIndex()
        sel = self.names[idx]
        urlm3u = self.urls[idx]
        self.session.open(ListM3u, sel, urlm3u)

    def cancel(self):
        self.close()


class ListM3u(Screen):
    def __init__(self, session, namem3u, url):
        Screen.__init__(self, session)
        self.session = session
        skin = join(skin_path, 'ListM3u.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.list = []
        self['list'] = tvList([])
        global SREF
        SREF = self.session.nav.getCurrentlyPlayingServiceReference()
        self['title'] = Label(title_plug + ' ' + namem3u)
        self['Maintainer2'] = Label(Maintainer2)
        self['path'] = Label(_('Folder path %s' % str(Path_Movies)))
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self.convert = False
        self.url = url
        self.name = namem3u
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Select'))
        self['key_yellow'] = Button()
        self["key_blue"] = Button()
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'ButtonSetupActions',
                                     'DirectionActions'],
                                    {'cancel': self.cancel,
                                     'ok': self.runList,
                                     'green': self.runList}, -2)
        if not exists(Path_Movies):
            self.mbox = self.session.open(
                MessageBox,
                _('Check in your Config Plugin - Path Movie'),
                MessageBox.TYPE_INFO,
                timeout=5)
            self.scsetup()

        self.timer = eTimer()
        if exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.openList)
        else:
            self.timer.callback.append(self.openList)
        self.timer.start(200, True)
        self.onLayoutFinish.append(self.passing)

    def passing(self):
        pass

    def scsetup(self):
        self.session.openWithCallback(self.close, OpenConfig)

    def openList(self):
        self.names = []
        self.urls = []

        try:
            req = urllib2.Request(self.url)
            req.add_header(
                "User-Agent",
                "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; "
                "rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14"
            )
            with urllib2.urlopen(req, timeout=15) as r:
                content = r.read().decode("utf-8", "ignore")

            regex = r'<a href="([^"]+\.(?:m3u8?|m3u))">'
            matches = compile(regex).findall(content)

            items = []
            for rel in matches:
                full_url = self.url + rel
                name = rel.rsplit(".", 1)[0]
                item = name + "###" + full_url
                items.append(item)

            items.sort()

            for item in items:
                name, url = item.split("###")
                name = name.strip()
                url = url.strip()
                if url not in self.urls:
                    self.names.append(Utils.checkStr(name))
                    self.urls.append(Utils.checkStr(url))

            self["key_green"].show()
            m3ulist(self.names, self["list"])

        except Exception as e:
            print("Error in openList: %s" % e)

    def runList(self):
        i = len(self.names)
        if i < 0 or i >= len(self.names):
            return
        idx = self["list"].getSelectionIndex()
        sel = self.names[idx]
        urlm3u = self.urls[idx]
        self.session.open(ChannelList, sel, urlm3u)

    def cancel(self):
        self.close()


class ChannelList(Screen):
    def __init__(self, session, name, url):
        Screen.__init__(self, session)
        self.session = session
        skin = join(skin_path, 'ChannelList.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.list = []
        self['list'] = tvList([])
        self.setTitle(title_plug + ' ' + name)
        self['title'] = Label(title_plug + ' ' + name)
        self['Maintainer2'] = Label(Maintainer2)
        self['path'] = Label(_('Folder path %s' % str(Path_Movies)))
        service = cfg.services.value
        self['service'] = Label(_('Service Reference used %s') % service)
        self['live'] = Label()
        self['poster'] = Pixmap()
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Convert ExtePlayer3'))
        self['key_yellow'] = Button(_('Convert Gstreamer'))
        self["key_blue"] = Button(_("Search"))
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self.pin = False
        global in_tmp
        global search_ok
        self.servicx = 'gst'
        search_ok = False
        in_tmp = Path_Movies
        self.search = ''
        self.name = name
        self.url = url
        self.names = []
        self.urls = []
        self.pics = []
        self['actions'] = ActionMap(
            ['OkCancelActions',
             'ColorActions',
             'InfobarInstantRecord',
             'MenuActions',
             'ButtonSetupActions',
             'TimerEditActions',
             'DirectionActions'],
            {
                'red': self.cancel,
                # 'green': self.runRec,
                'menu': self.AdjUrlFavo,
                'green': self.message2,
                'yellow': self.message1,
                'cancel': self.cancel,
                'up': self.up,
                'down': self.down,
                'left': self.left,
                'right': self.right,
                'blue': self.search_m3u,
                'rec': self.runRec,
                'instantRecord': self.runRec,
                'ShortRecord': self.runRec,
                'ok': self.runChannel
            },
            -2
        )

        self.currentList = 'list'
        print('ChannelList sleep 4 - 1')
        self.timer = eTimer()
        if exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.downlist)
        else:
            self.timer.callback.append(self.downlist)
        self.timer.start(200, True)
        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        pass

    def message1(self):
        i = len(self.names)
        if i < 0 or i >= len(self.names):
            return
        self.servicx = 'iptv'
        self.session.openWithCallback(
            self.check10,
            MessageBox,
            _("Do you want to Convert Bouquet IPTV?"),
            MessageBox.TYPE_YESNO)

    def message2(self):
        i = len(self.names)
        if i < 0 or i >= len(self.names):
            return
        self.servicx = 'gst'
        self.session.openWithCallback(
            self.check10,
            MessageBox,
            _("Do you want to Convert Bouquet GSTREAMER?"),
            MessageBox.TYPE_YESNO)

    def check10(self, result):
        if result:
            print('in folder tmp:', in_tmp)
            idx = self["list"].getSelectionIndex()

            if not idx:
                return

            self.convert = True
            service = '4097' if self.servicx == 'iptv' else '5002'
            namebouquett = self.name.replace(
                ' ', '_').replace(
                '-', '_').strip()
            print('namebouquett in folder tmp:', namebouquett)

            try:
                sleep(3)

                if isfile(in_tmp) and stat(in_tmp).st_size > 0:
                    bqtname = 'userbouquet.stvcl_%s.tv' % namebouquett.lower()
                    desk_tmp = ''
                    in_bouquets = False

                    with open('%s%s' % (dir_enigma2, bqtname), 'w') as outfile:
                        outfile.write(
                            '#NAME %s\r\n' %
                            namebouquett.capitalize())

                        for line in open(in_tmp):
                            if line.startswith(('http://', 'https')):
                                outfile.write(
                                    '#SERVICE %s:0:1:1:0:0:0:0:0:0:%s' %
                                    (service, line.replace(
                                        ':', '%3a')))
                                outfile.write('#DESCRIPTION %s' % desk_tmp)
                            elif line.startswith('#EXTINF'):
                                desk_tmp = line.split(',')[-1]
                            elif '<stream_url><![CDATA' in line:
                                outfile.write('#SERVICE %s:0:1:1:0:0:0:0:0:0:%s\r\n' % (
                                    service, line.split('[')[-1].split(']')[0].replace(':', '%3a')))
                                outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                            elif '<title>' in line:
                                if '<![CDATA[' in line:
                                    desk_tmp = line.split(
                                        '[')[-1].split(']')[0] + '\r\n'
                                else:
                                    desk_tmp = line.split('<')[1].split('>')[
                                        1] + '\r\n'

                    self.mbox = self.session.open(
                        MessageBox,
                        _('Check out the favorites list ...'),
                        MessageBox.TYPE_INFO,
                        timeout=5)

                    if isfile('/etc/enigma2/bouquets.tv'):
                        with open('/etc/enigma2/bouquets.tv') as f:
                            in_bouquets = any(bqtname in line for line in f)

                        if not in_bouquets:
                            if isfile('%s%s' % (dir_enigma2, bqtname)) and isfile(
                                    '/etc/enigma2/bouquets.tv'):
                                Utils.remove_line(
                                    '/etc/enigma2/bouquets.tv', bqtname)
                                with open('/etc/enigma2/bouquets.tv', 'a+') as outfile:
                                    outfile.write(
                                        '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' %
                                        bqtname)

                    self.mbox = self.session.open(
                        MessageBox,
                        _('Shuffle Favorite List in Progress') +
                        '\n' +
                        _('Wait please ...'),
                        MessageBox.TYPE_INFO,
                        timeout=5)
                    Utils.ReloadBouquets()

                else:
                    self.session.open(
                        MessageBox,
                        _('Conversion Failed!!!'),
                        MessageBox.TYPE_INFO,
                        timeout=5)

            except Exception as e:
                self.convert = False
                print('Error during IPTV conversion:', e)

    def cancel(self):
        if search_ok is True:
            self.resetSearch()
        else:
            self.close()

    def search_m3u(self):
        self.session.openWithCallback(
            self.filterM3u,
            VirtualKeyBoard,
            title=_("Filter this category..."),
            text=self.search)

    def filterM3u(self, result):
        if result:
            self.names = []
            self.urls = []
            self.pics = []
            pic = plugin_path + "/res/pics/default.png"
            search = result
            try:
                with open(in_tmp, "r+") as f1:
                    fpage = f1.read()
                    regexcat = "EXTINF.*?,(.*?)\\n(.*?)\\n"
                    match = compile(regexcat, DOTALL).findall(fpage)

                    for name, url in match:
                        if search.lower() in name.lower():
                            search_ok = True
                            url = url.replace(" ", "").replace("\\n", "")
                            self.names.append(name)
                            self.urls.append(url)
                            self.pics.append(pic)

                    if search_ok:
                        m3ulist(self.names, self["list"])
                        self["live"].setText(
                            "N." + str(len(self.names)) + " Stream")
                    else:
                        search_ok = False
                        self.resetSearch()

            except Exception as e:
                print('Error during M3U filter:', e)
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
        i = len(self.names)
        if i < 0 or i >= len(self.names):
            return
        global urlm3u, namem3u
        idx = self["list"].getSelectionIndex()
        namem3u = self.names[idx]
        urlm3u = self.urls[idx]
        if self.downloading is True:
            self.session.open(
                MessageBox,
                _('You are already downloading!!!'),
                MessageBox.TYPE_INFO,
                timeout=5)
        else:
            if '.mp4' in urlm3u or '.mkv' in urlm3u or '.flv' in urlm3u or '.avi' in urlm3u:
                self.downloading = True
                self.session.openWithCallback(
                    self.download_m3u,
                    MessageBox,
                    _("DOWNLOAD VIDEO?"),
                    type=MessageBox.TYPE_YESNO,
                    timeout=10,
                    default=False)
            else:
                self.downloading = False
                self.session.open(
                    MessageBox,
                    _('Only VOD Movie allowed or not .ext Filtered!!!'),
                    MessageBox.TYPE_INFO,
                    timeout=5)

    def download_m3u(self, result):
        if result:
            try:
                if self.downloading:
                    idx = self["list"].getSelectionIndex()
                    namem3u = self.names[idx]
                    urlm3u = self.urls[idx]
                    path = urlparse(urlm3u).path
                    ext = splitext(path)[1]

                    fileTitle = sub(r'[<>:"/\\|?*\[\]]', '_', namem3u)
                    fileTitle = sub(r'[\s\(\)#\'\+\!&]', '_', fileTitle)
                    # Rimuove underscore ripetuti
                    fileTitle = sub(r'_+', '_', fileTitle)
                    fileTitle = fileTitle.lower() + ext  # Aggiunge l'estensione al nome del file

                    in_tmp = join(Path_Movies, fileTitle)

                    if isfile(in_tmp):
                        remove(in_tmp)

                    self.download = downloadWithProgress(urlm3u, in_tmp)
                    self.download.addProgress(self.downloadProgress)
                    self.download.start().addCallback(self.check).addErrback(self.showError)

                else:
                    self.downloading = False
                    self.session.open(
                        MessageBox,
                        _('Download Failed!!!'),
                        MessageBox.TYPE_INFO,
                        timeout=5)

            except Exception as e:
                print('Error during m3u download:', e)

        return

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (
            recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))
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
        self.session.open(
            MessageBox,
            _('Download Failed!!!'),
            MessageBox.TYPE_INFO,
            timeout=5)
        print('ChannelList DownloadError')

    def downlist(self):
        namem3u = self.name
        urlm3u = self.url
        print("urlm3u:", urlm3u)

        try:
            # Sanitize filename
            fileTitle = sub(r'[<>:"/\\|?*\[\]]', '_', namem3u)
            fileTitle = sub(r'[\s\(\)#\'\+\!&]', '_', fileTitle)
            fileTitle = sub(r'_+', '_', fileTitle).lower()

            self.in_tmp = join(Path_Movies, fileTitle + ".m3u")
            if isfile(self.in_tmp):
                remove(self.in_tmp)

            downloadFilest(urlm3u, self.in_tmp)
            sleep(3)

            self.playList()
            print("ChannelList Downlist completed")

        except Exception as e:
            print("Error during download:", e)

    def playList(self):
        self.names = []
        self.urls = []
        self.pics = []
        self.items = []
        pic = plugin_path + "/res/pics/default.png"

        try:
            tmp = getattr(self, "in_tmp", None)
            if tmp and isfile(tmp) and stat(tmp).st_size > 0:
                print("ChannelList tmp exists in playlist:", tmp)

                with open(tmp, "r") as f1:
                    fpage = f1.read()

                regex = r'#EXTINF:[^\n]*?,\s*(.*?)\r?\n(.*?)(?=\r?\n|$)'
                matches = compile(regex, DOTALL).findall(fpage)

                for name, url in matches:
                    if url.startswith("http"):
                        clean_url = (
                            url.replace(" ", "%20")
                               .replace("\n", "")
                               .replace("%0A", "")
                        )
                        if "samsung" in self.url.lower() or cfg.filterx.value:
                            sub_regex = r'(.*?)(?:\.m3u8)?$'
                            bases = compile(
                                sub_regex, DOTALL).findall(clean_url)
                            if bases:
                                clean_url = bases[0] + ".m3u8"

                        item = name + "###" + clean_url + "###" + pic
                        self.items.append(item)

                self.items.sort()
                for item in self.items:
                    nm, url, pc = item.split("###")
                    self.names.append(Utils.checkStr(nm))
                    self.urls.append(Utils.checkStr(url))
                    self.pics.append(Utils.checkStr(pc))

                m3ulist(self.names, self["list"])

                if cfg.thumb.value:
                    self["live"].setText("N. %s Stream" % len(self.names))
                    self.gridmaint = eTimer()
                    try:
                        self.gridmaint.callback.append(self.gridpic)
                    except BaseException:
                        self.gridmaint_conn = self.gridmaint.timeout.connect(
                            self.gridpic)
                    self.gridmaint.start(3000, True)
                else:
                    self["live"].setText("N. %s Stream" % len(self.names))

                self.load_poster()
                self["key_green"].show()
                self["key_yellow"].show()
                self["key_blue"].show()
            else:
                print("Playlist file missing or empty:", tmp)

        except Exception as e:
            print("Error in playList: %s" % e)

    def gridpic(self):
        self.session.open(GridMain, self.names, self.urls, self.pics)
        # self.GridMain(self.names, self.urls, self.pics)
        self.close()

    def runChannel(self):
        i = len(self.names)
        if i < 0 or i >= len(self.names):
            return
        idx = self['list'].getSelectionIndex()
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
        self.session.openWithCallback(
            self.pinEntered2,
            PinInput,
            pinList=[
                config.ParentalControl.setuppin.value],
            triesEntry=config.ParentalControl.retries.servicepin,
            title=_("Please enter the parental control pin code"),
            windowTitle=_("Enter pin code"))

    def pinEntered2(self, result):
        if not result:
            self.pin = False
            self.session.open(
                MessageBox,
                _("The pin code you entered is wrong."),
                type=MessageBox.TYPE_ERROR,
                timeout=5)
        self.runChannel2()

    def runChannel2(self):
        try:
            i = self['list'].getSelectedIndex()
            self.currentindex = i
            if i < 0 or i >= len(self.items):
                print("Invalid index:", i)
                return

            raw_item = self.items[i]
            parts = raw_item.split("###")
            if len(parts) < 2:
                print("Item format invalid:", raw_item)
                return

            name = parts[0]
            url = parts[1]

            print("Playing:", name, url)
            self.play_that_shit(
                url,
                name,
                self.currentindex,
                raw_item,
                self.items)

        except Exception as error:
            print("Error in runChannel2:", error)

    def play_that_shit(self, url, name, index, item, items):
        if not url or not isinstance(url, str) or url.strip() == "":
            print("Empty or invalid URL:", url)
            return
        if not name or not isinstance(name, str):
            print("Empty or invalid name:", name)
            return
        print("Opening M3uPlay2 with name:", name)
        self.session.open(M3uPlay2, name, url, index, item, items)

    def AdjUrlFavo(self):
        i = len(self.names)
        if i < 0 or i >= len(self.names):
            return
        idx = self['list'].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        regexcat = '(.*?).m3u8'
        match = compile(regexcat, DOTALL).findall(url)
        for url in match:
            url = url + '.m3u8'
        self.session.open(AddIpvStream, name, url)

    def up(self):
        self[self.currentList].up()
        self.load_poster()

    def down(self):
        self[self.currentList].down()
        self.load_poster()

    def left(self):
        self[self.currentList].pageUp()
        self.load_poster()

    def right(self):
        self[self.currentList].pageDown()
        self.load_poster()

    def load_poster(self):
        i = len(self.pics)
        if i < 0 or i >= len(self.pics):
            return
        idx = self['list'].getSelectionIndex()
        pic = self.pics[idx]
        pixmaps = defpic
        if pic and pic.find('http') == -1:
            self.poster_resize(pixmaps)
            return
        else:
            if pic.startswith('http'):
                pixmaps = str(pic)
                if PY3:
                    pixmaps = ensure_binary(pixmaps)
                print('pic xxxxxxxxxxxxx', pixmaps)
                path = urlparse(pixmaps).path
                ext = splitext(path)[1]
                pictmp = '/tmp/posterst' + str(ext)
                if exists(pictmp):
                    pictmp = '/tmp/posterst' + str(ext)
                try:
                    if pixmaps.startswith(b"https") and sslverify:
                        parsed_uri = urlparse(pixmaps)
                        domain = parsed_uri.hostname
                        sniFactory = SNIFactory(domain)
                        if PY3:
                            pixmaps = ensure_binary(pixmaps)
                        print('url: ', pixmaps)
                        downloadPage(
                            pixmaps,
                            pictmp,
                            sniFactory,
                            timeout=5).addCallback(
                            self.downloadPic,
                            pictmp).addErrback(
                            self.downloadError)
                    else:
                        downloadPage(
                            pixmaps,
                            pictmp).addCallback(
                            self.downloadPic,
                            pictmp).addErrback(
                            self.downloadError)
                except Exception as e:
                    print("Error: can't find file or read data ", e)
        return

    def downloadError(self, raw):
        try:
            self.poster_resize(defpic)
        except Exception as e:
            print(e)
            print('exe downloadError')

    def downloadPic(self, data, pictmp):
        if exists(pictmp):
            try:
                self.poster_resize(pictmp)
            except Exception as e:
                print("* error ", e)
                pass

    def poster_resize(self, png):
        self["poster"].show()
        pixmaps = png
        if exists(pixmaps):
            size = self['poster'].instance.size()
            self.picload = ePicLoad()
            self.scale = AVSwitch().getFramebufferScale()
            self.picload.setPara(
                [size.width(), size.height(), self.scale[0], self.scale[1], 0, 1, '#00000000'])
            if exists('/var/lib/dpkg/status'):
                self.picload.startDecode(pixmaps, False)
            else:
                self.picload.startDecode(pixmaps, 0, 0, False)
            ptr = self.picload.getData()
            if ptr is not None:
                self['poster'].instance.setPixmap(ptr)
                self['poster'].show()
            else:
                print('no cover.. error')
            return


class TvInfoBarShowHide():
    """ InfoBar show/hide control, accepts toggleShow and hide actions, might start
    fancy animations. """
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3
    skipToggleShow = False

    def __init__(self):
        self["ShowHideActions"] = ActionMap(
            ["InfobarShowHideActions"], {
                "toggleShow": self.OkPressed, "hide": self.hide}, 0)
        self.__event_tracker = ServiceEventTracker(
            screen=self, eventmap={
                iPlayableService.evStart: self.serviceStarted})
        self.__state = self.STATE_SHOWN
        self.__locked = 0
        self.hideTimer = eTimer()
        try:
            self.hideTimer_conn = self.hideTimer.timeout.connect(
                self.doTimerHide)
        except BaseException:
            self.hideTimer.callback.append(self.doTimerHide)
        self.hideTimer.start(5000, True)
        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)

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

    def serviceStarted(self):
        if self.execing:
            if config.usage.show_infobar_on_zap.value:
                self.doShow()

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()

    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            self.hideTimer.stop()
            idx = config.usage.infobar_timeout.index
            if idx:
                self.hideTimer.start(idx * 1500, True)

    def __onHide(self):
        self.__state = self.STATE_HIDDEN

    def doShow(self):
        self.hideTimer.stop()
        self.show()
        self.startHideTimer()

    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()

    def lockShow(self):
        try:
            self.__locked += 1
        except BaseException:
            self.__locked = 0
        if self.execing:
            self.show()
            self.hideTimer.stop()
            self.skipToggleShow = False

    def unlockShow(self):
        try:
            self.__locked -= 1
        except BaseException:
            self.__locked = 0
        if self.__locked < 0:
            self.__locked = 0
        if self.execing:
            self.startHideTimer()

    def debug(obj, text=""):
        print(text + " %s\n" % obj)


class M3uPlay2(
    InfoBarBase,
    InfoBarMenu,
    InfoBarSeek,
    InfoBarAudioSelection,
    InfoBarSubtitleSupport,
    InfoBarNotifications,
    TvInfoBarShowHide,
    Screen
):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True
    ALLOW_SUSPEND = True
    screen_timeout = 5000

    def __init__(self, session, name, url, index, item, items):
        global streaml
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = 'MoviePlayer'
        streaml = False
        self.stream_running = False
        for x in InfoBarBase, \
                InfoBarMenu, \
                InfoBarSeek, \
                InfoBarAudioSelection, \
                InfoBarSubtitleSupport, \
                InfoBarNotifications, \
                TvInfoBarShowHide:
            x.__init__(self)

        try:
            self.init_aspect = aspect_manager.get_current_aspect()
        except BaseException:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect
        self['actions'] = ActionMap(
            [
                'MoviePlayerActions',
                'MovieSelectionActions',
                'MediaPlayerActions',
                'EPGSelectActions',
                'OkCancelActions',
                'InfobarShowHideActions',
                'InfobarActions',
                'DirectionActions',
                'InfobarSeekActions'
            ],
            {
                "leavePlayer": self.cancel,
                "epg": self.showIMDB,
                "info": self.showIMDB,
                "tv": self.cicleStreamType,
                "stop": self.leavePlayer,
                "cancel": self.cancel,
                "exit": self.leavePlayer,
                "channelDown": self.previousitem,
                "channelUp": self.nextitem,
                "down": self.previousitem,
                "up": self.nextitem,
                "back": self.cancel
            },
            -1
        )
        self.allowPiP = False
        self.service = None

        self.currentindex = index
        self.item = item
        self.itemscount = len(items)
        self.list = items

        self.url = url.replace('%0a', '').replace('%0A', '')
        self.pcip = 'None'
        self.name = html_conv.html_unescape(name)
        self.state = self.STATE_PLAYING
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        if '8088' in str(self.url):
            self.onFirstExecBegin.append(self.slinkPlay)
        else:
            self.onFirstExecBegin.append(
                lambda: self.cicleStreamType(
                    self.name, force=True))
        # self.onClose.append(self.cancel)

    def nextitem(self):
        self.stopStream()
        currentindex = int(self.currentindex) + 1
        if currentindex == self.itemscount:
            currentindex = 0
        self.currentindex = currentindex
        i = self.currentindex
        item_str = self.list[i]
        parts = item_str.split("###")
        if len(parts) >= 2:
            self.name = parts[0]
            self.url = parts[1]
        else:
            print("Invalid item format in list at index", i)
            self.name = ""
            self.url = ""
        self.cicleStreamType(self.name, force=False)

    def previousitem(self):
        self.stopStream()
        currentindex = int(self.currentindex) - 1
        if currentindex < 0:
            currentindex = self.itemscount - 1
        self.currentindex = currentindex
        i = self.currentindex
        item_str = self.list[i]
        parts = item_str.split("###")
        if len(parts) >= 2:
            self.name = parts[0]
            self.url = parts[1]
        else:
            print("Invalid item format in list at index", i)
            self.name = ""
            self.url = ""
        self.cicleStreamType(self.name, force=False)

    def doEofInternal(self, playing):
        self.close()

    def __evEOF(self):
        self.end = True

    def stopStream(self):
        if self.stream_running:
            self.stream_running = False
            print("Stream stopped and state reset.")
            self.session.nav.stopService()
            self.session.nav.playService(self.srefInit)
        else:
            print("No active stream to stop.")

    def cicleStreamType(self, name="", force=False):
        global streaml
        streaml = False
        from itertools import cycle, islice
        self.servicetype = str(cfg.services.value)
        print('servicetype1: ', self.servicetype)
        url = str(self.url)

        if str(splitext(self.url)[-1]) == ".m3u8":
            if self.servicetype == "1":
                self.servicetype = "4097"

        currentindex = 0
        streamtypelist = ["4097"]

        if exists("/usr/bin/apt-get"):
            streamtypelist.append("8193")

        for index, item in enumerate(streamtypelist, start=0):
            if str(item) == str(self.servicetype):
                currentindex = index
                break

        nextStreamType = islice(cycle(streamtypelist), currentindex + 1, None)
        self.servicetype = str(next(nextStreamType))
        print('servicetype2: ', self.servicetype)

        if self.stream_running and not force:
            return
        self.stream_running = True
        # Pass the name here if not already done
        self.openPlay(self.servicetype, url, name)

    def openPlay(self, servicetype, url, name):
        print(
            "openPlay called with: servicetype={}, url={}, name={}".format(
                servicetype,
                url,
                name))
        name = str(name)
        ref = "{0}:0:1:0:0:0:0:0:0:0:{1}:{2}".format(
            servicetype, url.replace(
                ":", "%3a"), name.replace(
                ":", "%3a"))
        print('reference:   ', ref)
        if streaml is True:
            url = 'http://127.0.0.1:8088/' + str(url)
            ref = "{0}:0:1:0:0:0:0:0:0:0:{1}:{2}".format(
                servicetype, url.replace(
                    ":", "%3a"), name.replace(
                    ":", "%3a"))
            print('streaml reference:   ', ref)
        print('final reference:', ref)
        sref = eServiceReference(ref)
        sref.setName(name)
        print("[M3uPlay2] Now playing:", name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback is not None:
            self.infoCallback()
        return

    def showAfterSeek(self):
        if isinstance(self, TvInfoBarShowHide):
            self.doShow()

    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def setAspect(self, aspect):
        map = {0: '4_3_letterbox',
               1: '4_3_panscan',
               2: '16_9',
               3: '16_9_always',
               4: '16_10_letterbox',
               5: '16_10_panscan',
               6: '16_9_letterbox'}
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except BaseException:
            pass

    def av(self):
        temp = aspect_manager.get_current_aspect()  # int(self.getAspect())
        temp = temp + 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)

    def showIMDB(self):
        text_clear = self.name
        if returnIMDB(text_clear):
            print('show imdb/tmdb')

    def slinkPlay(self, url):
        name = self.name
        ref = "{0}:{1}".format(
            url.replace(
                ":", "%3a"), name.replace(
                ":", "%3a"))
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(str(name))
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def cancel(self):
        self.stopStream()
        self.stream_running = False
        if isfile('/tmp/hls.avi'):
            remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(self.srefInit)
        aspect_manager.restore_aspect()  # Restore aspect on exit
        self.close()

    def leavePlayer(self):
        self.cancel()


class AddIpvStream(Screen):
    def __init__(self, session, name, url):
        Screen.__init__(self, session)
        self.session = session
        skin = join(skin_path, 'AddIpvStream.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setTitle(title_plug + ' ' + name)
        self['title'] = Label(title_plug + ' ' + name)
        self['Maintainer2'] = Label(Maintainer2)
        # self['path'] = Label(_('Folder path %s'% str(Path_Movies)))
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Ok'))
        self['key_yellow'] = Button()
        self["key_blue"] = Button()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'ButtonSetupActions',
                                     'DirectionActions'], {'ok': self.keyOk,
                                                           'cancel': self.keyCancel,
                                                           'green': self.keyOk,
                                                           'red': self.keyCancel}, -2)
        self['statusbar'] = Label()
        self.list = []
        self['list'] = MenuList([])
        self.mutableList = None
        self.servicelist = ServiceList(None)
        self.onLayoutFinish.append(self.createTopMenu)
        self.namechannel = name
        self.urlchannel = url
        return

    def initSelectionList(self):
        self.list = []
        self['list'].setList(self.list)

    def createTopMenu(self):
        self.setTitle(_('Add Stream IPTV'))
        self.initSelectionList()
        self.list = []
        self.list = self.getBouquetList()
        self['list'].setList(self.list)
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
                bouquets.append(
                    (info.getName(
                        self.bouquet_root),
                        self.bouquet_root))
            return bouquets
        return None

    def keyOk(self):
        if len(self.list) == 0:
            return
        self.name = ''
        self.url = ''
        self.session.openWithCallback(
            self.addservice,
            VirtualKeyBoard,
            title=_('Enter Name'),
            text=self.namechannel)

    def addservice(self, res):
        if res:
            self.url = res
            str = '4097:0:1:0:0:0:0:0:0:0:%s:%s' % (
                quote(self.url), quote(self.name))
            ref = eServiceReference(str)
            self.addServiceToBouquet(
                self.list[self['list'].getSelectedIndex()][1], ref)
            self.close()

    def addServiceToBouquet(self, dest, service=None):
        mutableList = self.getMutableList(dest)
        if mutableList is not None:
            if service is None:
                return
            if not mutableList.addService(service):
                mutableList.flushChanges()
        return

    def getMutableList(self, root=eServiceReference()):
        if self.mutableList is not None:
            return self.mutableList
        else:
            serviceHandler = eServiceCenter.getInstance()
            if not root.valid():
                root = self.getRoot()
            list = root and serviceHandler.list(root)
            if list is not None:
                return list.startEdit()
            return
            return

    def getRoot(self):
        return self.servicelist.getRoot()

    def keyCancel(self):
        self.close()


class OpenConfig(Screen, ConfigListScreen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = join(skin_path, 'OpenConfig.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = _("stvcl Config")
        self.onChangedEntry = []
        self.list = []
        info = '***YOUR SETUP***'
        self.setTitle(title_plug + ' ' + info)
        self['title'] = Label(title_plug + ' SETUP')
        self['Maintainer2'] = Label(Maintainer2)
        self["paypal"] = Label()
        # self['path'] = Label(_('Folder path %s'% str(Path_Movies)))
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('- - - -'))
        self["key_blue"] = Button(_('Empty Pic Cache'))
        self['key_yellow'] = Button()
        self['key_yellow'].hide()
        # self["key_blue"].hide()
        self['text'] = Label(info)
        self["description"] = Label()
        self['actions'] = ActionMap(["SetupActions",
                                     "ColorActions",
                                     'ButtonSetupActions',
                                     "VirtualKeyboardActions"], {'cancel': self.extnok,
                                                                 'red': self.extnok,
                                                                 'green': self.cfgok,
                                                                 'blue': self.cachedel,
                                                                 # 'yellow': self.msgupdt1,
                                                                 'showVirtualKeyboard': self.KeyText,
                                                                 'ok': self.Ok_edit}, -2)

        ConfigListScreen.__init__(
            self,
            self.list,
            session=self.session,
            on_change=self.changedEntry)
        self.createSetup()
        # self.onLayoutFinish.append(self.checkUpdate)
        self.onLayoutFinish.append(self.layoutFinished)
        if self.setInfo not in self['config'].onSelectionChanged:
            self['config'].onSelectionChanged.append(self.setInfo)

    def layoutFinished(self):
        payp = paypal()
        self["paypal"].setText(payp)
        self.setTitle(self.setup_title)

    def cachedel(self):
        fold = tvstrvl  # cfg.cachefold.value + "stvcl"
        cmd = "rm -rf " + tvstrvl + "/*"
        if exists(fold):
            os_system(cmd)
        self.mbox = self.session.open(
            MessageBox,
            _('All cache fold are empty!'),
            MessageBox.TYPE_INFO,
            timeout=5)

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        self.list.append(
            getConfigListEntry(
                _('IPTV bouquets location '),
                cfg.bouquettop,
                _("Configure position of the bouquets of the converted lists")))
        self.list.append(
            getConfigListEntry(
                _('Player folder List <.m3u>:'),
                cfg.pthm3uf,
                _("Folder path containing the .m3u files")))
        self.list.append(
            getConfigListEntry(
                _('Services Player Reference type'),
                cfg.services,
                _("Configure Service Player Reference")))
        self.list.append(
            getConfigListEntry(
                _('Filter M3U link regex type'),
                cfg.filterx,
                _("Set On for line link m3u full")))
        self.list.append(
            getConfigListEntry(
                _('Show thumpics?'),
                cfg.thumb,
                _("Show Thumbpics ? Enigma restart required")))
        if cfg.thumb.value is True:
            self.list.append(
                getConfigListEntry(
                    _('Download thumpics?'),
                    cfg.thumbpic,
                    _("Download thumpics in Player M3U (is very Slow)?")))
        self.list.append(
            getConfigListEntry(
                _('Folder Cache for Thumbpics:'),
                cfg.cachefold,
                _("Configure position folder for temporary Thumbpics")))
        self.list.append(
            getConfigListEntry(
                _('Link in Extensions Menu:'),
                cfg.strtext,
                _("Show Plugin in Extensions Menu")))
        self.list.append(
            getConfigListEntry(
                _('Link in Main Menu:'),
                cfg.strtmain,
                _("Show Plugin in Main Menu")))
        self['config'].list = self.list
        self["config"].l.setList(self.list)
        self.setInfo()

    def setInfo(self):
        entry = str(self.getCurrentEntry())

        if entry == _('IPTV bouquets location '):
            self['description'].setText(
                _("Configure position of the bouquets of the converted lists"))
        elif entry == _('Player folder List <.m3u>:'):
            self['description'].setText(
                _("Folder path containing the .m3u files"))
        elif entry == _('Filter M3U link regex type'):
            self['description'].setText(_("Set On for line link m3u full"))
        elif entry == _('Services Player Reference type'):
            self['description'].setText(
                _("Configure Service Player Reference"))
        elif entry == _('Show thumpics?'):
            self['description'].setText(
                _("Show Thumbpics ? Enigma restart required"))
        elif entry == _('Download thumpics?'):
            self['description'].setText(
                _("Download thumpics in Player M3U (is very Slow)?"))
        elif entry == _('Folder Cache for Thumbpics:'):
            self['description'].setText(
                _("Configure position folder for temporary Thumbpics"))
        elif entry == _('Link in Extensions Menu:'):
            self['description'].setText(_("Show Plugin in Extensions Menu"))
        elif entry == _('Link in Main Menu:'):
            self['description'].setText(_("Show Plugin in Main Menu"))

    def changedEntry(self):
        self['key_green'].instance.setText(
            _('Save') if self['config'].isChanged() else '- - - -')
        for x in self.onChangedEntry:
            x()
        try:
            if isinstance(
                self['config'].getCurrent()[1],
                ConfigEnableDisable) or isinstance(
                self['config'].getCurrent()[1],
                ConfigYesNo) or isinstance(
                self['config'].getCurrent()[1],
                    ConfigSelection):
                self.createSetup()
        except BaseException:
            pass

    def getCurrentEntry(self):
        return self['config'].getCurrent() and self['config'].getCurrent()[
            0] or ''

    def getCurrentValue(self):
        return self['config'].getCurrent() and str(
            self['config'].getCurrent()[1].getText()) or ''

    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary

    def Ok_edit(self):
        ConfigListScreen.keyOK(self)
        sel = self['config'].getCurrent()[1]
        if sel and sel == cfg.pthm3uf:
            self.setting = 'pthm3uf'
            self.openDirectoryBrowser(cfg.pthm3uf.value)
        elif sel and sel == cfg.cachefold:
            self.setting = 'cachefold'
            self.openDirectoryBrowser(cfg.cachefold.value)
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
                inhibitDirs=[
                    '/bin',
                    '/boot',
                    '/dev',
                    '/home',
                    '/lib',
                    '/proc',
                    '/run',
                    '/sbin',
                    '/sys',
                    '/var'],
                minFree=15)
        except Exception as e:
            print('error: ', e)

    def openDirectoryBrowserCB(self, path):
        if path is not None:
            if self.setting == 'pthm3uf':
                cfg.pthm3uf.setValue(path)
            elif self.setting == 'cachefold':
                path = join(path, 'stvcl')
                cfg.cachefold.setValue(path)
        return

    def cfgok(self):
        self.save()

    def save(self):
        if not exists(cfg.pthm3uf.value):
            self.mbox = self.session.open(
                MessageBox,
                _('M3u list folder not detected!'),
                MessageBox.TYPE_INFO,
                timeout=4)
            return
        if self['config'].isChanged():
            for x in self['config'].list:
                x[1].save()
            configfile.save()
            plugins.clearPluginList()
            plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
            self.mbox = self.session.open(
                MessageBox,
                _('Settings saved correctly!'),
                MessageBox.TYPE_INFO,
                timeout=5)
            self.close()
        else:
            self.close()

    def VirtualKeyBoardCallback(self, callback=None):
        if callback is not None and len(callback):
            self["config"].getCurrent()[1].setValue(callback)
            self["config"].invalidate(self["config"].getCurrent())

    def KeyText(self):
        sel = self['config'].getCurrent()
        if sel:
            self.session.openWithCallback(
                self.VirtualKeyBoardCallback,
                VirtualKeyBoard,
                title=self['config'].getCurrent()[0],
                text=self['config'].getCurrent()[1].value)

    def cancelConfirm(self, result):
        if not result:
            return
        for x in self['config'].list:
            x[1].cancel()
        self.close()

    def extnok(self):
        if self['config'].isChanged():
            self.session.openWithCallback(
                self.cancelConfirm,
                MessageBox,
                _('Really close without saving the settings?'))
        else:
            self.close()


def threadGetPage(
        url=None,
        file=None,
        key=None,
        success=None,
        fail=None,
        *args,
        **kwargs):
    print('[tivustream][threadGetPage] url, file, key, args, kwargs',
          url, "   ", file, "   ", key, "   ", args, "   ", kwargs)
    try:
        url = url.rstrip('\r\n')
        url = url.rstrip()
        url = url.replace("%0A", "")
        response = get(url, verify=False)
        response.raise_for_status()
        if file is None:
            success(response.content)
        elif key is not None:
            success(response.content, file, key)
        else:
            success(response.content, file)
    except httperror:
        print('[tivustream][threadGetPage] Http error: ', httperror)
        # fail(error)  # E0602 undefined name 'error'
    except exceptions.RequestException as error:
        print(error)


def getpics(names, pics, tmpfold, picfold):
    global defpic
    defpic = defpic
    pix = []

    if cfg.thumbpic.value == "False":
        npic = len(pics)
        i = 0
        while i < npic:
            pix.append(defpic)
            i += 1
        return pix

    cmd = "rm " + tmpfold + "/*"
    os_system(cmd)

    npic = len(pics)
    j = 0

    while j < npic:
        name = names[j]
        if name is None or name == '':
            name = "Video"
        url = pics[j]
        ext = str(splitext(url)[-1])
        picf = join(picfold, str(name + ext))
        tpicf = join(tmpfold, str(name + ext))

        if exists(picf):
            if ('stagione') in str(name.lower()):
                cmd = "rm " + picf
                os_system(cmd)

            cmd = "cp " + picf + " " + tmpfold
            print("In getpics fileExists(picf) cmd =", cmd)
            os_system(cmd)

        if not exists(picf):
            if plugin_path in url:
                try:
                    cmd = "cp " + url + " " + tpicf
                    print("In getpics not fileExists(picf) cmd =", cmd)
                    os_system(cmd)
                except BaseException:
                    pass
            else:
                # now download image
                try:
                    url = url.replace(" ", "%20").replace("ExQ", "=")
                    url = url.replace("AxNxD", "&").replace("%0A", "")
                    poster = Utils.checkRedirect(url)
                    if poster:
                        if "|" in url:
                            n3 = url.find("|", 0)
                            n1 = url.find("Referer", n3)
                            n2 = url.find("=", n1)
                            url = url[:n3]
                            referer = url[n2:]
                            p = Utils.getUrl2(url, referer)
                            with open(tpicf, 'wb') as f1:
                                f1.write(p)
                        else:
                            try:
                                try:
                                    with open(tpicf, 'wb') as f:
                                        f.write(
                                            get(url, stream=True, allow_redirects=True).content)
                                    print(
                                        '=============11111111=================\n')
                                except Exception as e:
                                    print("Error: Exception", e)
                                    print(
                                        '===========2222222222=================\n')
                                    callInThread(
                                        threadGetPage,
                                        url=poster,
                                        file=tpicf,
                                        success=downloadPic,
                                        fail=downloadError)
                            except Exception as e:
                                print("Error: Exception 2")
                                print(e)

                except BaseException:
                    cmd = "cp " + defpic + " " + tpicf
                    os_system(cmd)
                    print('cp defpic tpicf')

        if not exists(tpicf):
            cmd = "cp " + defpic + " " + tpicf
            os_system(cmd)

        if exists(tpicf):
            try:
                size = [150, 220]
                if screenwidth.width() == 2560:
                    size = [294, 440]
                elif screenwidth.width() == 1920:
                    size = [220, 330]

                file_name, file_extension = splitext(tpicf)
                try:
                    im = Image.open(tpicf).convert("RGBA")
                    # shrink if larger
                    try:
                        im.thumbnail(size, Image.Resampling.LANCZOS)
                    except BaseException:
                        im.thumbnail(size, Image.ANTIALIAS)
                    imagew, imageh = im.size
                    # enlarge if smaller
                    try:
                        if imagew < size[0]:
                            ratio = size[0] / imagew
                            try:
                                im = im.resize(
                                    (int(imagew * ratio), int(imageh * ratio)), Image.Resampling.LANCZOS)
                            except BaseException:
                                im = im.resize(
                                    (int(imagew * ratio), int(imageh * ratio)), Image.ANTIALIAS)

                            imagew, imageh = im.size
                    except Exception as e:
                        print(e)
                    """
                    # no work on PY3
                    # crop and center image
                    bg = Image.new("RGBA", size, (255, 255, 255, 0))
                    im_alpha = im.convert("RGBA").split()[-1]
                    bgwidth, bgheight = bg.size
                    bg_alpha = bg.convert("RGBA").split()[-1]
                    temp = Image.new("L", (bgwidth, bgheight), 0)
                    temp.paste(im_alpha, (int((bgwidth - imagew) / 2), int((bgheight - imageh) / 2)), im_alpha)
                    bg_alpha = ImageChops.screen(bg_alpha, temp)
                    bg.paste(im, (int((bgwidth - imagew) / 2), int((bgheight - imageh) / 2)))
                    im = bg
                    """
                    im.save(file_name + ".png", "PNG")
                except Exception as e:
                    print(e)
                    im = Image.open(tpicf)
                    try:
                        im.thumbnail(size, Image.Resampling.LANCZOS)
                    except BaseException:
                        im.thumbnail(size, Image.ANTIALIAS)
                    im.save(tpicf)
            except Exception as e:
                print("******* picon resize failed *******")
                print(e)
                tpicf = defpic
        else:
            print("******* make picon failed *******")
            tpicf = defpic

        pix.append(j)
        pix[j] = picf
        j += 1

    cmd1 = "cp " + tmpfold + "/* " + picfold
    os_system(cmd1)

    cmd1 = "rm " + tmpfold + "/* &"
    os_system(cmd1)
    return pix


def downloadPic(output, poster):
    try:
        if output is not None:
            f = open(poster, 'wb')
            f.write(output)
            f.close()
    except Exception as e:
        print('downloadPic error ', e)
    return


def downloadError(output):
    print('output error ', output)
    pass


def savePoster(dwn_poster, url_poster):
    with open(dwn_poster, 'wb') as f:
        f.write(get(url_poster, stream=True, allow_redirects=True).content)
        f.close()


class GridMain(Screen):
    def __init__(self, session, names, urls, pics=[]):
        from Components.Sources.List import List
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        skin = join(skin_path, 'GridMain.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self['title'] = Label('..:: S.T.V.C.L. ::..')
        self.pos = []

        def add_positions(coords):
            for coord in coords:
                self.pos.append(coord)

        if screenwidth.width == 2560:
            positions = [
                [180, 80], [658, 80], [1134, 80], [1610, 80], [2084, 80],
                [180, 720], [658, 720], [1134, 720], [1610, 720], [2084, 720]
            ]
            add_positions(positions)

        elif screenwidth.width == 1920:
            positions = [
                [122, 42], [478, 42], [834, 42], [1190, 42], [1546, 42],
                [122, 522], [478, 522], [834, 522], [1190, 522], [1546, 522]
            ]
            add_positions(positions)

        else:
            positions = [
                [81, 28], [319, 28], [556, 28], [793, 28], [1031, 28],
                [81, 348], [319, 348], [556, 348], [793, 348], [1031, 348]
            ]
            add_positions(positions)

        # join(str(cfg.cachefold.value), "stvcl/tmp")
        tmpfold = tvstrvl + "/tmp"
        # join(str(cfg.cachefold.value), "stvcl/pic")
        picfold = tvstrvl + " /pic"
        picx = getpics(names, pics, tmpfold, picfold)
        # print("In Gridmain pics = ", pics)
        self.urls = urls
        self.pics = picx
        self.name = "stvcl"
        self.names = names
        self["info"] = Label()
        menu_list = []
        menu_list = names
        for x in menu_list:
            print("x in list =", x)

        self["menu"] = List(menu_list)
        self["frame"] = MovingPixmap()

        self.PIXMAPS_PER_PAGE = 10
        i = 0
        while i < self.PIXMAPS_PER_PAGE:
            self["label" + str(i + 1)] = StaticText()
            self["pixmap" + str(i + 1)] = Pixmap()
            i += 1
        self.npics = len(self.names)
        self.npage = int(float(self.npics // self.PIXMAPS_PER_PAGE)) + 1
        self.index = 0
        self.maxentry = len(menu_list) - 1
        self.ipage = 1

        self["actions"] = ActionMap(["OkCancelActions",
                                     "EPGSelectActions",
                                     "MenuActions",
                                     'ButtonSetupActions',
                                     "DirectionActions",
                                     "NumberActions"],
                                    {"ok": self.okClicked,
                                     "cancel": self.cancel,
                                     "left": self.key_left,
                                     "right": self.key_right,
                                     "up": self.key_up,
                                     "down": self.key_down})
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openTest)
        # self.onShown.append(self.openTest)

    def paintFrame(self):
        try:
            # If the index exceeds the maximum number of items, it returns to
            # the first item
            if self.index > self.maxentry:
                self.index = self.minentry
            self.idx = self.index
            name = self.names[self.idx]
            self['info'].setText(str(name))
            ifr = self.index - (self.PIXMAPS_PER_PAGE * (self.ipage - 1))
            ipos = self.pos[ifr]
            self["frame"].moveTo(ipos[0], ipos[1], 1)
            self["frame"].startMoving()
        except Exception as e:
            print('Error in paintFrame: ', e)

    def openTest(self):
        if self.ipage < self.npage:
            self.maxentry = (self.PIXMAPS_PER_PAGE * self.ipage) - 1
            self.minentry = (self.ipage - 1) * self.PIXMAPS_PER_PAGE

        elif self.ipage == self.npage:
            self.maxentry = len(self.pics) - 1
            self.minentry = (self.ipage - 1) * self.PIXMAPS_PER_PAGE
            i1 = 0
            while i1 < self.PIXMAPS_PER_PAGE:
                self["label" + str(i1 + 1)].setText(" ")
                self["pixmap" + str(i1 + 1)].instance.setPixmapFromFile(dblank)
                i1 += 1
        self.npics = len(self.pics)
        i = 0
        i1 = 0
        self.picnum = 0
        ln = self.maxentry - (self.minentry - 1)
        while i < ln:
            idx = self.minentry + i
            # self["label" + str(i + 1)].setText(self.names[idx])  # this show
            # label to bottom of png pixmap
            pic = self.pics[idx]
            if not exists(self.pics[idx]):
                pic = dblank
            self["pixmap" + str(i + 1)].instance.setPixmapFromFile(pic)
            i += 1
        self.index = self.minentry
        self.paintFrame()

    def key_left(self):
        # Decrement the index only if we are not at the first pixmap
        if self.index >= 0:
            self.index -= 1
        else:
            # If we are at the first pixmap, go back to the last pixmap of the
            # last page
            self.ipage = self.npage
            self.index = self.npics - 1
        # Check if we need to change pages
        if self.index < self.minentry:
            self.ipage -= 1
            if self.ipage < 1:  # If we go beyond the first page
                self.ipage = self.npage
                self.index = self.npics - 1  # Back to the last pixmap of the last page
            self.openTest()
        else:
            self.paintFrame()

    def key_right(self):
        # Increment the index only if we are not at the last pixmap
        if self.index < self.npics - 1:
            self.index += 1
        else:
            # If we are at the last pixmap, go back to the first pixmap of the
            # first page
            self.index = 0
            self.ipage = 1
            self.openTest()
        # Check if we need to change pages
        if self.index > self.maxentry:
            self.ipage += 1
            if self.ipage > self.npage:  # If we exceed the number of pages
                self.index = 0
                self.ipage = 1  # Back to first page
            self.openTest()
        else:
            self.paintFrame()

    def key_up(self):
        if self.index >= 5:
            self.index -= 5
        else:
            if self.ipage > 1:
                self.ipage -= 1
                self.index = self.maxentry  # Back to the last line of the previous page
                self.openTest()
            else:
                # If we are on the first page, go back to the last pixmap of
                # the last page
                self.ipage = self.npage
                self.index = self.npics - 1
                self.openTest()
        self.paintFrame()

    def key_down(self):
        if self.index <= self.maxentry - 5:
            self.index += 5
        else:
            if self.ipage < self.npage:
                self.ipage += 1
                self.index = self.minentry  # Back to the top of the next page
                self.openTest()
            else:
                # If we are on the last page, go back to the first pixmap of
                # the first page
                self.index = 0
                self.ipage = 1
                self.openTest()

        self.paintFrame()

    def okClicked(self):
        itype = self.index
        url = self.urls[itype]
        name = self.names[itype]
        self.session.open(M3uPlay2, name, url)
        return

    def cancel(self):
        self.close()

    def exit(self):
        self.close()

    def info(self):
        itype = self.index
        self.inf = self.names[itype]
        # self.inf = ''
        try:
            self.inf = self.names[itype]
        except BaseException:
            pass
        if self.inf:
            try:
                self["info"].setText(self.inf)
                # print('infos: ', self.inf)
            except BaseException:
                self["info"].setText('')
                # print('except info')
        print("In GridMain infos =", self.inf)
