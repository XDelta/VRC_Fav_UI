from os import mkdir
from os.path import dirname, isdir, join

import toml

from Logging import vrcl
import __meta__ as meta

appname = 'VRC Fav UI'
applongname = 'VRC: Fav UI'
configSpec = 6

class Config(object):

	def __init__(self):
		self.app_dir = dirname(__file__)
		self.app_icon = join(self.app_dir, 'favicon.ico')
		self.version = meta.version

	# def setFavoritesFile(self, favoriteFile):
	# 	tomlData = toml.load(open(join(self.app_dir, 'config', 'favorites.toml')))
	# 	self.getFavorites = tomlData

	def getFavoritesToml(self): # gets favorites from file when needed, allows updating your favorites without restarting
		try:
			tomlData = toml.load(open(join(self.app_dir, 'config', 'favorites.toml')))
			return tomlData
		except Exception as e:
			vrcl.log(e)
			vrcl.log("Failed to load favorites.toml")
			return None

	def setValDefault(self, val, default): #set a default in case the value is missing in the config
		if(val in (None, "")):
			return default
		return val

	def setConfigFile(self, configFile):
		tomlData = toml.load(open(join(self.app_dir, 'config', configFile)))

		# print(tomlData)
		self.getUsername = self.setValDefault(tomlData.get('credentials').get('username'), "ChangeMe")
		self.getPassword = self.setValDefault(tomlData.get('credentials').get('password'), "ChangeMe")
		self.get2FARequired = self.setValDefault(tomlData.get('credentials').get('2fa'), False)
		if(self.get2FARequired):
			vrcl.log("2FA not supported yet")

		self.getAvatarFolder = self.setValDefault(tomlData.get('management').get('avatarFolder'), "avatars")
		self.writeAvatarDB = self.setValDefault(tomlData.get('management').get('writeAvatarDB'), False)
		self.getReleaseStatusCheck = self.setValDefault(tomlData.get('management').get('releaseStatusCheck'), True)
		self.failCooldown = self.setValDefault(tomlData.get('management').get('failCooldown'), 2)
		self.normalCooldown = self.setValDefault(tomlData.get('management').get('normalCooldown'), 60)
		self.longCooldown = self.setValDefault(tomlData.get('management').get('longCooldown'), 120)
		self.useGlobalKeybind = self.setValDefault(tomlData.get('management').get('useGlobalKeybind'), False)
		self.getGlobalKeyBind = self.setValDefault(tomlData.get('management').get('globalKeybind'), ["control", "k"])

		self.getDebugLogEnabled = self.setValDefault(tomlData.get('debug').get('debugLog'), False)
		self.getExtraOptions = self.setValDefault(tomlData.get('debug').get('extraOptions'), False)

		self.getSpec = tomlData.get('debug').get('configSpec')
		if(self.getSpec != configSpec):
			vrcl.log("ConfigSpec in "+configFile+" doesn't match this version, your config may be out of date")
		self.getRaw = tomlData

		if(self.getDebugLogEnabled):
			print(tomlData)
		self.updateAvatarDir()

	def updateAvatarDir(self):
		if(self.getAvatarFolder.isalnum()):
			self.avatar_dir = join(self.app_dir, self.getAvatarFolder)
		else:
			vrcl.log("Avatar folder name invalid, falling back to 'avatars'")
			self.avatar_dir = join(self.app_dir, 'avatars')

		self.dbfile = join(self.avatar_dir, 'vrcdb.sqlite')

		if not isdir(self.avatar_dir):
			mkdir(self.avatar_dir)

config = Config()
