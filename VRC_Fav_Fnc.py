# pylint: disable=E0611,E1101,W0201,W0622
import re, shutil, sys, sqlite3
from os.path import exists, join

import vrcpy, requests

from Config import config
from Logging import vrcl

client = vrcpy.Client()

def end():
	client.logout()
	vrcl.closeLog()
	sys.exit()

try:
	# Here instead of in config.py so errors are logged and client can attempt logout
	config.setConfigFile('config.toml')
except Exception as e:
	vrcl.log("Error opening config")
	vrcl.log(str(e))
	vrcl.closeLog()
	raise e

def login():
	try:
		client.login(config.getUsername, config.getPassword)
		b = client.fetch_me()
		vrcl.log("Logged in as: "+b.displayName)
	except Exception:
		vrcl.log("Failed to Login")
		vrcl.closeLog()
		sys.exit()

def getUser():
	return client.fetch_me().displayName

def dropFile(data):
	setFavorite(stringToID(data))

def stringToID(input):
	reg = re.compile("(avtr_[0-9,a-f]{8}-[0-9,a-f]{4}-[0-9,a-f]{4}-[0-9,a-f]{4}-[0-9,a-f]{12})") #tests https://regexr.com/56rb9
	#remove extra prefixes like skip_, private_, deleted_, nsfw_, etc
	result = reg.search(input)  #search full path string
	vrcl.log("re:" + str(result))
	try:
		return result.group(1)
	except Exception as e:
		vrcl.log(str(e))
		return None

def setFavorite(id):
	if(id is None):
		vrcl.log("No avtr id in string to fav")
		return

	try:
		a = client.fetch_avatar(id)
		vrcl.log("Adding "+id+" to favorites")
	except Exception as e:
		vrcl.log(str(e))
		vrcl.log("Failed to find "+id+", avatar may have been deleted")
		vrcl.log("No response received, retry later") #if vrc auth timed out, this will return no response
		return

	if(a.releaseStatus == "private" and config.getReleaseStatusCheck):
		vrcl.log("Failed to add "+id+", avatar was made private and would be unavailable in game")
		vrcl.log("You may change releaseStatusCheck in config.toml to skip this check")
		return

	try:
		a.favorite()
	except Exception as e:
		vrcl.log("Failed to add to favorites, likely at max")
		vrcl.log(str(e))

def removeFavorite(user, id):
	vrcl.log("removeFavorite: " + id)
	user.remove_favorite(id)

def removeFavoriteID(id):
	if id is None:
		return
	vrcl.log("removeFavorite: " + id)
	client.fetch_me().remove_favorite(id)

def clearFavorites():
	list = getFavoriteList()
	d = client.fetch_me()
	for favAv in list:
		removeFavorite(d, favAv.favoriteId)

def getFavoriteList():
	#seem to not get all?, got 10 of 16
	vrcl.log("Fetching favorites")
	a = client.fetch_me().fetch_favorites("avatar")

	for x in a: #log favorites
		vrcl.log(x.favoriteId)

	return a

def revertFavorites():
	clearFavorites()
	clearFavorites()

	vrcl.log("Restoring favorites from file")
	for x in range(1, 17):
		if (config.getFavorites.get([str(x)] != "")):
			setFavorite(stringToID(config.getFavorites.get([str(x)])))
		else:
			vrcl.log("Skipping favorite "+ str(x)+ " as it is not set")

def collectAvatar():
	b = client.fetch_me() #refresh user object
	avtr_name = b.currentAvatar.name
	avtr_id = b.currentAvatar.id
	img = b.currentAvatar.thumbnailImageUrl #sometimes gets api.vrchat.cloud img link instead of cloudfront thumbnail png
	vrcl.log("-"*24)
	vrcl.log("Name: "+avtr_name)
	vrcl.log("ID: "+avtr_id)
	vrcl.log("Img: "+img)
	outputFile = join(config.avatar_dir, avtr_id+".png")
	vrcl.log(outputFile)

	if not exists(outputFile):
		r = requests.get(img, allow_redirects=True, stream=True, headers={'User-Agent': ""}) #stopped by cf if useragent is missing, fine if empty, https://i.gifer.com/72nt.gif
		r.raw.decode_content = True
		with open(outputFile, 'wb') as f:
			shutil.copyfileobj(r.raw, f)
		vrcl.log("Got: "+avtr_name+":"+avtr_id)
	else:
		vrcl.log("Avatar " + avtr_name+":"+avtr_id+" has already been downloaded")
		vrcl.log("Skipping")

def collectAvatarById(id):
	if(id is None): #not needed
		vrcl.log("No avtr id in string")
		return
	b = client.fetch_avatar(id) #refresh user object
	avtr_name = b.name
	avtr_id = b.id
	img = b.thumbnailImageUrl #sometimes gets api.vrchat.cloud img link instead of cloudfront thumbnail png
	vrcl.log("-"*24)
	vrcl.log("Name: "+avtr_name)
	vrcl.log("ID: "+avtr_id)
	vrcl.log("Img: "+img)
	outputFile = join(config.avatar_dir, avtr_id+".png")
	vrcl.log(outputFile)

	if not exists(outputFile):
		r = requests.get(img, allow_redirects=True, stream=True, headers={'User-Agent': ""}) #stopped by cf if useragent is missing, fine if empty, https://i.gifer.com/72nt.gif
		r.raw.decode_content = True
		with open(outputFile, 'wb') as f:
			shutil.copyfileobj(r.raw, f)
		vrcl.log("Got: "+avtr_name+":"+avtr_id)
	else:
		vrcl.log("Avatar " + avtr_name+":"+avtr_id+" has already been downloaded")
		vrcl.log("Skipping")
