#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext
import os
from os import environ as os_environ
PluginLanguageDomain = 'stvcl'
PluginLanguagePath = 'Extensions/stvcl/res/locale'


def paypal():
    conthelp = "If you like what I do you\n"
    conthelp += "can contribute with a coffee\n"
    conthelp += "scan the qr code and donate € 1.00"
    return conthelp


def localeInit():
    if os.path.isfile('/var/lib/dpkg/status'):
        # getLanguage returns e.g. "fi_FI" for "language_country"
        lang = language.getLanguage()[:2]
        # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs
        # it!
        os_environ["LANGUAGE"] = lang
    gettext.bindtextdomain(
        PluginLanguageDomain,
        resolveFilename(
            SCOPE_PLUGINS,
            PluginLanguagePath))


if os.path.isfile('/var/lib/dpkg/status'):
    def _(txt):
        return gettext.dgettext(PluginLanguageDomain, txt) if txt else ""
    localeInit()
    language.addCallback(localeInit)
else:
    def _(txt):
        if gettext.dgettext(PluginLanguageDomain, txt):
            return gettext.dgettext(PluginLanguageDomain, txt)
        else:
            print(("[%s] fallback to default translation for %s" %
                  (PluginLanguageDomain, txt)))
            return gettext.gettext(txt)
    language.addCallback(localeInit())


scramble = 'aHR0cHM6Ly9pLm1qaC5uei8='
installer_url = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL0JlbGZhZ29yMjAwNS9TLlQuVi5DLkwtL21haW4vaW5zdGFsbGVyLnNo'
developer_url = 'aHR0cHM6Ly9hcGkuZ2l0aHViLmNvbS9yZXBvcy9CZWxmYWdvcjIwMDUvUy5ULlYuQy5MLQ=='
