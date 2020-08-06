from os import mkdir
from os.path import dirname, exists, isdir, join
import json

appname = 'VRC Fav UI'
applongname = 'VRC: Fav UI'

class Config(object):

	def __init__(self):
		self.app_dir = dirname(__file__)

		self.avatar_dir = join(self.app_dir, 'avatars')
		if not isdir(self.avatar_dir):
			mkdir(self.avatar_dir)

		self.app_icon = join(self.app_dir,'favicon.ico')

	def setConfigFile(self, configFile):
		jsonData = json.load(open(join(self.app_dir, configFile)))
		self.getKey = jsonData

	def setFavoritesFile(self, favoriteFile):
		jsonData = json.load(open(join(self.app_dir, favoriteFile)))
		self.getFav = jsonData

config = Config()