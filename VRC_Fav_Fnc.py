# pylint: disable=E0611,E1101,W0201,W0622
import re, shutil, sys, sqlite3
from os.path import exists, join
from datetime import datetime

import vrcpy, requests

from Config import config
from Logging import vrcl

client = vrcpy.Client()

def end():
	try: #client may not be logged in
		client.logout()
	except:
		pass
	vrcl.closeLog()
	sys.exit()

try:
	config.setConfigFile('config.toml')
except Exception as e:
	vrcl.log("Error opening config")
	vrcl.log(str(e))
	end()

try:
	conn = sqlite3.connect(join(config.app_dir, 'vrcdb.sqlite'))
	print("Opened database successfully")
except Exception as e:
	vrcl.log("Unable to open vrcdb.sqlite")
	vrcl.log(str(e))
	end()

def login():
	try:
		client.login(config.getUsername, config.getPassword)
		b = client.fetch_me()
		vrcl.log("Logged in as: "+b.displayName)
	except Exception as e:
		vrcl.log(type(e)+":"+e)
		vrcl.log("Failed to Login")
		end()

def getUser():
	return client.fetch_me().displayName

def checkAuth():
	print("Checking Auth")
	try:
		c = client.api.call("/auth")
		print("["+str(c.get('status'))+"] Authed?: "+str(c.get('data').get('ok')))
	except Exception:
		print("Failed connection, retrying")
		c = client.api.call("/auth")
		print("["+str(c.get('status'))+"] Authed?: "+str(c.get('data').get('ok')))

def dropFile(data):
	setFavorite(stringToID(data))

def stringToID(input):
	reg = re.compile("(avtr_[0-9,a-f]{8}-[0-9,a-f]{4}-[0-9,a-f]{4}-[0-9,a-f]{4}-[0-9,a-f]{12})") #tests https://regexr.com/56rb9
	#removes extra prefixes like skip_, private_, deleted_, nsfw_, etc
	result = reg.search(input) #search full path string
	vrcl.log("re:" + str(result))
	try:
		return result.group(1)
	except Exception as e:
		vrcl.log(str(e))
		return None

def setFavorite(id):
	if(id is None):
		vrcl.log("No avtr id in string to favorite")
		return

	try:
		a = client.fetch_avatar(id)
		vrcl.log("Adding "+id+" to favorites")
	except Exception as e:
		vrcl.log(str(e))
		vrcl.log("Failed to find "+id+", avatar may have been deleted")
		vrcl.log("No response received, retry later") #if vrc auth timed out, this will return no response. vrc might also just not have found it in time
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

def removeFavoriteID(id):
	if id is None:
		return
	vrcl.log("removeFavorite: " + id)
	client.fetch_me().remove_favorite(id)

def clearFavorites():
	try:
		list = getFavoriteList()
		user = client.fetch_me()
		for favAv in list:
			vrcl.log("removeFavorite: " + favAv.favoriteId) #id - fvrt_4b216a69-3159-49bb-a1c1-0fb2408883f6
			user.remove_favorite(favAv.favoriteId)
	except Exception as e:
		print(str(e))


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
	f = config.getFavoritesToml()

	print(str(f))
	try:
		print(config.getFavoritesToml().get(1)) #no str needed?
		print("BHEHB: " + str(config.getFavoritesToml().get(str(1))))
	except Exception as e:
		print(str(e))

	for x in range(1, 17):
		ta = config.getFavoritesToml().get(str(x))
		if (ta != ""):
			setFavorite(stringToID(ta))
		else:
			vrcl.log("Skipping favorite "+ str(x)+ " as it is not set")

def collectAvatar(): #get currently worn avatar and pass id to collect
	b = client.fetch_me() #refresh user object
	avtr_id = b.currentAvatar.id
	collectAvatarById(avtr_id)

def collectAvatarById(idInput):
	a = client.fetch_avatar(idInput) #refresh user object
	avtr_id = a.id
	avtr_name = a.name
	avtr_desc = a.description
	avtr_img = a.thumbnailImageUrl #sometimes gets api.vrchat.cloud img link instead of cloudfront thumbnail png
	user_id = a.author().id
	user_name = a.author().displayName
	user_username = a.author().username
	date_collected = datetime.now().strftime("%m/%d/%y-%H:%M:%S")
	release_status = a.releaseStatus

	vrcl.log("-"*24) #show console message of avatar info
	vrcl.log("Name: "+avtr_name)
	vrcl.log("ID: "+avtr_id)
	vrcl.log("Img: "+avtr_img)
	outputFile = join(config.avatar_dir, avtr_id+".png")
	vrcl.log(outputFile)

	if config.writedb: # write to sqlite db if configured
		ac = conn.cursor()
		if ac.execute("SELECT EXISTS(SELECT 1 FROM AVATARS WHERE avtr_id=?)", (idInput, )).fetchone()[0] > 0: #check if id is already in db
			print("Found "+idInput+" in db")
		else: #if not, add try to add it to db
			print(idInput+" was not found in db")
			try:
				ac.execute("INSERT INTO AVATARS (avtr_id, avtr_name, avtr_desc, avtr_img, user_id, user_name, user_username, date_collected, release_status) VALUES (?,?,?,?,?,?,?,?,?)",
				           (avtr_id, avtr_name, avtr_desc, avtr_img, user_id, user_name, user_username, date_collected, release_status))
				conn.commit()
				ac.close()
				vrcl.log("Saved: "+avtr_id+" to db")
			except Exception as e:
				vrcl.log(e)
				vrcl.log("Error in insert")
				raise e

	if not exists(outputFile): #check if image already exists if not, download it
		r = requests.get(avtr_img, allow_redirects=True, stream=True, headers={'User-Agent': ""}) #stopped by cf if useragent is missing, fine if empty, https://i.gifer.com/72nt.gif
		r.raw.decode_content = True
		with open(outputFile, 'wb') as f:
			shutil.copyfileobj(r.raw, f)
		vrcl.log("Got: "+avtr_name+":"+avtr_id)
	else:
		vrcl.log("Avatar " + avtr_name+":"+avtr_id+" has already been downloaded")
		vrcl.log("Skipping")

def generate():
	gc = conn.cursor()
	gc.execute('''CREATE TABLE IF NOT EXISTS "AVATARS" (
		"avtr_id"	TEXT NOT NULL CHECK(length(avtr_id) = 41) UNIQUE COLLATE NOCASE,
		"avtr_name"	TEXT NOT NULL,
		"avtr_desc"	TEXT,
		"avtr_img"	TEXT,
		"user_id"	TEXT NOT NULL CHECK(length(user_id) = 40),
		"user_name"	TEXT NOT NULL COLLATE NOCASE,
		"user_username"	TEXT NOT NULL COLLATE NOCASE,
		"date_collected"	TEXT,
		"release_status"	TEXT COLLATE NOCASE,
		"mark"	TEXT COLLATE NOCASE,
		"notes"	TEXT,
		"nsfw"	INTEGER DEFAULT 0,
		PRIMARY KEY("avtr_id")
		);
	''')
	conn.commit()
	gc.close()
	print("Generated tables")
