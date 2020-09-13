from os import mkdir
from os.path import dirname, isdir, join
import toml

from Logging import vrcl

appname = 'VRC Fav UI'
applongname = 'VRC: Fav UI'

class Config(object):

	def __init__(self):
		self.app_dir = dirname(__file__)

		self.app_icon = join(self.app_dir,'favicon.ico')

	def setFavoritesFile(self, favoriteFile):
		tomlData = toml.load(open(join(self.app_dir, 'config', favoriteFile)))
		self.getFavorites = tomlData

	def setConfigFile(self, configFile):
		tomlData = toml.load(open(join(self.app_dir, 'config', configFile)))
		print(tomlData)
		self.getUsername = tomlData.get('credentials').get('username')
		self.getPassword = tomlData.get('credentials').get('password')
		self.get2FARequired = tomlData.get('credentials').get('2fa')
		if(self.get2FARequired):
			vrcl.log("2FA not supported yet")
			vrcf.end()
		self.getAvatarFolder = tomlData.get('management').get('avatarFolder')
		self.getReleaseStatusCheck = tomlData.get('management').get('releaseStatusCheck')
		self.getDebugLogEnabled = tomlData.get('debug').get('enableDebugLog')
		self.failCooldown = self.setValDefault(tomlData.get('management').get('failCooldown'), 2)
		self.normalCooldown = self.setValDefault(tomlData.get('management').get('normalCooldown'), 60)
		self.longCooldown = self.setValDefault(tomlData.get('management').get('longCooldown'), 120)
		self.getSpec = tomlData.get('debug').get('configSpec')
		self.getRaw = tomlData
		self.updateAvatarDir()

	def updateAvatarDir(self):
		if(self.getAvatarFolder.isalnum()):
			self.avatar_dir = join(self.app_dir, self.getAvatarFolder)
		else:
			vrcl.log("Avatar folder name invalid, falling back to 'avatars'")
			self.avatar_dir = join(self.app_dir, 'avatars')

		if not isdir(self.avatar_dir):
			mkdir(self.avatar_dir)

config = Config()