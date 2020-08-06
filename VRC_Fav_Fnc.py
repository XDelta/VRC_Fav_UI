# pylint: disable=W0622,E1101
import re, shutil, sys
from os.path import exists, join
from datetime import datetime

import vrcpy, requests

from Config import config

client = vrcpy.Client()
client.log_to_console = False
log_file = open(join(config.app_dir, 'VRChat_Fav.log'), mode='a+', encoding='utf-8', errors='ignore', buffering=1)

def end():
	client.logout()
	log_file.close()
	sys.exit()

def log(text):
	log_text = datetime.now().strftime("%m/%d/%y - %H:%M:%S")
	con = datetime.now().strftime("%H:%M:%S") #console doesn't need day
	log_file.write("["+log_text+"] "+text+'\n')
	print("["+con+"] "+text)

try:
	# Here instead of in config.py so errors are logged and client can attempt logout
	config.setConfigFile('config.json')
	config.setFavoritesFile('favorites.json')
except Exception as e:
	log("Error opening config.json or favorites.json")
	log(str(e))
	log_file.close()
	raise e

def login():
	try:
		client.login(config.getKey["username"], config.getKey["password"])
		b = client.fetch_me()
		log("Logged in as: "+b.displayName)
	except Exception:
		log("Failed to Login")
		log_file.close()
		sys.exit()

def getUser():
	return client.fetch_me().displayName

def dropFile(data):
	setFavorite(stringToID(data))

def stringToID(input):
	reg = re.compile("(avtr_[0-9,a-f]{8}-[0-9,a-f]{4}-[0-9,a-f]{4}-[0-9,a-f]{4}-[0-9,a-f]{12})") #tests https://regexr.com/56rb9
	#remove extra prefixes like skip_, private_, deleted_, nsfw_, etc
	result = reg.search(input)  #search full path string
	log("sID:" + str(result))
	try:
		return result.group(1)
	except Exception as e:
		log(str(e))
		return None

def setFavorite(id):
	if(id is None):
		log("No avtr id in string to fav")
		return

	try:
		a = client.fetch_avatar(id)
		log("Adding "+id+" to favorites")
	except Exception as e:
		log(str(e))
		log("Failed to find "+id+", avatar may have been deleted")
		return

	if(a.releaseStatus == "private" and config.getKey["releaseStatusCheck"]):
		log("Failed to add "+id+", avatar was made private and would be unavailable in game")
		log("You may change releaseStatusCheck in config.json to skip this check")
		return

	try:
		a.favorite()
	except Exception as e:
		log("Failed to add to favorites, likely at max")
		log(str(e))

def removeFavorite(user, id):
	log("removeFavorite: " + id)
	user.remove_favorite(id)

def removeAllFavorites():
	list = getFavoriteList()
	d = client.fetch_me()
	for favAv in list:
		removeFavorite(d, favAv.favoriteId)

def getFavoriteList():
	#seem to not get all?, got 10 of 16
	log("Fetching favorites")
	a = client.fetch_me().fetch_favorites("avatar")

	for x in a: #log favorites
		log(x.favoriteId)

	return a

def revertFavorites():
	log("Removing Favorites pass 1")
	removeAllFavorites()
	log("Removing Favorites pass 2")
	removeAllFavorites()

	log("Restoring favorites from file")
	for x in range(1, 17):
		if (config.getFav[str(x)] != ""):
			setFavorite(config.getFav[str(x)])
		else:
			log("Skipping favorite "+ str(x)+ " as it is not set")

def collectAvatar():
	b = client.fetch_me() #refresh user object
	avtr_name = b.currentAvatar.name
	avtr_id = b.currentAvatar.id
	img = b.currentAvatar.thumbnailImageUrl #sometimes gets api.vrchat.cloud img link instead of cloudfront thumbnail png
	log("-"*24)
	log("Name: "+avtr_name)
	log("ID: "+avtr_id)
	log("Img: "+img)
	outputFile = join(config.avatar_dir, avtr_id+".png")
	log(outputFile)

	if not exists(outputFile):
		r = requests.get(img, allow_redirects=True, stream=True, headers={'User-Agent': ""}) #stopped by cf if useragent is missing, fine if empty, https://i.gifer.com/72nt.gif
		r.raw.decode_content = True
		with open(outputFile, 'wb') as f:
			shutil.copyfileobj(r.raw, f)
		log("Got: "+avtr_name+":"+avtr_id)
	else:
		log("Avatar " + avtr_name+":"+avtr_id+" has already been downloaded")
		log("Skipping")

def collectAvatarById(id):
	if(id is None): #not needed
		log("No avtr id in string")
		return
	b = client.fetch_avatar(id) #refresh user object
	avtr_name = b.name
	avtr_id = b.id
	img = b.thumbnailImageUrl #sometimes gets api.vrchat.cloud img link instead of cloudfront thumbnail png
	log("-"*24)
	log("Name: "+avtr_name)
	log("ID: "+avtr_id)
	log("Img: "+img)
	outputFile = join(config.avatar_dir, avtr_id+".png")
	log(outputFile)

	if not exists(outputFile):
		r = requests.get(img, allow_redirects=True, stream=True, headers={'User-Agent': ""}) #stopped by cf if useragent is missing, fine if empty, https://i.gifer.com/72nt.gif
		r.raw.decode_content = True
		with open(outputFile, 'wb') as f:
			shutil.copyfileobj(r.raw, f)
		log("Got: "+avtr_name+":"+avtr_id)
	else:
		log("Avatar " + avtr_name+":"+avtr_id+" has already been downloaded")
		log("Skipping")