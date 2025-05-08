#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
****************************************
*        coded by Lululla              *
*             skin by MMark            *
*             10/07/2022               *
*   Thank's                            *
*      stvcl, Levi45, KiddaC           *
****************************************
'''

# Standard library imports
import os
import gettext

# Third-party imports
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import SCOPE_PLUGINS, resolveFilename
from Components.config import config

# Local imports
from . import mainx
from . import Utils

currversion = '1.4'
title_plug = 'Smart Tv Channels List'
desc_plugin = '..:: Smart Tv Channels List  V.%s ::.. ' % currversion
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('stvcl'))
_ = gettext.gettext


def mainw(session, **kwargs):
	try:
		from six.moves import reload_module
		reload_module(Utils)
		reload_module(mainx)
		session.open(mainx.StvclMain)
	except:
		import traceback
		traceback.print_exc()
		pass


def cfgmain(menuid, **kwargs):
	if menuid == 'mainmenu':
		from Tools.BoundFunction import boundFunction
		return [(title_plug,
				 boundFunction(mainw, showExtentionMenuOption=True),
				 desc_plugin,
				 -1)]
	else:
		return []


def Plugins(**kwargs):
	piclogox = 'logo.png'

	if not os.path.exists('/var/lib/dpkg/status'):
		piclogox = plugin_path + '/res/skins/hd/logo.png'

	extDescriptor = PluginDescriptor(
		name=title_plug,
		description=_(desc_plugin),
		where=PluginDescriptor.WHERE_EXTENSIONSMENU,
		icon=piclogox,
		fnc=mainw
	)

	mainDescriptor = PluginDescriptor(
		name=title_plug,
		description=_(desc_plugin),
		where=PluginDescriptor.WHERE_MENU,
		icon=piclogox,
		fnc=cfgmain
	)

	result = [
		PluginDescriptor(
			name=title_plug,
			description=desc_plugin,
			where=PluginDescriptor.WHERE_PLUGINMENU,
			icon=piclogox,
			fnc=mainw
		)
	]

	if config.plugins.stvcl.strtext.value:
		result.append(extDescriptor)

	if config.plugins.stvcl.strtmain.value:
		result.append(mainDescriptor)

	return result
