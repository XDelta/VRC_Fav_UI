import sys, ctypes
from os.path import join
from os import environ
from time import time
import threading

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGridLayout, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from system_hotkey import SystemHotkey

from Config import applongname, config
import VRC_Fav_Fnc as vrcf
from Logging import vrcl

hk = SystemHotkey()
appid = 'tk.deltawolf.vrc_fav_ui' # unique id string for windows to show taskbar icon
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

class DropTarget(QLabel):
	def __init__(self):
		super().__init__()
		self.setAlignment(Qt.AlignCenter)
		self.setText('\n\n Drop Avatar Here \n\n')
		self.setStyleSheet('''
			QLabel{
				border: 1px dashed #00ff00;
				background-color: #0A0A0A;
			}
		''')

class AppWindow(QWidget):
	def __init__(self):
		super().__init__()

		self.setWindowTitle(applongname)
		self.setAcceptDrops(True)
		self.setContentsMargins(0, 0, 0, 0)
		self.setWindowIcon(QIcon(config.app_icon))
		self.setStyleSheet('''
			QLabel {
				padding:2px;
				font: 10pt 'Euro Caps';
				color: #00ff00;
				background-color: #0A0A0A;
			}
			QLineEdit {
				color: #00ff00;
				background-color: #0F0F0F;
			}
			QPushButton {
				font: 10pt 'Euro Caps';
				color: #00ff00;
				background-color: #0A0A0A;
			}
			QPushButton:hover {
				color: #0A0A0A;
				background-color: #00ff00;
			}
			QPushButton:pressed {
				color: #00cc00;
				background-color: #0A0A0A;
			}
			QPushButton:disabled {
				color: #00aa00;
				background-color: #1A1A1A;
			}
		''')

		layout = QGridLayout()
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)

		layout.addWidget(QLabel('Logged in as: '), 1, 0)
		vrcf.login()

		layout.addWidget(QLabel(vrcf.getUser()), 1, 1)

		layout.addWidget(DropTarget(), 2, 0, 1, 2)#avatar drag and drop

		idLabel = QLabel('ID:', self)
		layout.addWidget(idLabel, 3, 0)

		self.idEntry = QLineEdit('')
		layout.addWidget(self.idEntry, 3, 1)

		self.addIdFavBtn = QPushButton('Add Id to Favorites', self)
		self.addIdFavBtn.clicked.connect(self.btnFavAvatarID)
		layout.addWidget(self.addIdFavBtn, 4, 0, 1, 2)

		self.collectAvtrBtn = QPushButton('Collect Current Avatar', self)
		self.collectAvtrBtn.clicked.connect(self.btnCollectAvtr)
		layout.addWidget(self.collectAvtrBtn, 5, 0, 1, 2)

		self.collectAvtrIdBtn = QPushButton('Collect Id', self)
		self.collectAvtrIdBtn.clicked.connect(self.btnCollectAvtrById)
		layout.addWidget(self.collectAvtrIdBtn, 6, 0, 1, 2)

		if config.getExtraOptions: # alternatively may use .hide() instead of not making button
			self.removeAvtrIdBtn = QPushButton('Remove Fav by Id', self)
			self.removeAvtrIdBtn.clicked.connect(self.btnRemoveAvtrById)
			layout.addWidget(self.removeAvtrIdBtn, 7, 0, 1, 2)

		self.clearFavBtn = QPushButton('[Clear All Favorites]', self)
		self.clearFavBtn.clicked.connect(self.btnClearFav)
		layout.addWidget(self.clearFavBtn, 8, 0, 1, 2)

		self.revertFavBtn = QPushButton('[Revert Favorites]', self)
		self.revertFavBtn.clicked.connect(self.btnRevertFav)
		layout.addWidget(self.revertFavBtn, 9, 0, 1, 2)

		self.statusLabel = QLabel('Ready', self)
		layout.addWidget(self.statusLabel, 10, 0, 1, 2)
		self.onCooldown = False
		self.allowDrop = True
		self.setLayout(layout)
		vrcf.checkdb()

	def dragEnterEvent(self, event):
		if event.mimeData().hasImage:
			event.accept()
		else:
			event.ignore()

	def dragMoveEvent(self, event):
		if event.mimeData().hasImage:
			event.accept()
		else:
			event.ignore()

	def dropEvent(self, event):
		if(event.mimeData().hasImage and self.allowDrop == True):
			event.setDropAction(Qt.CopyAction)
			file_path = event.mimeData().urls()[0].toLocalFile()
			sID = vrcf.stringToID(file_path)
			self.clearId()
			if(sID is None):
				vrcl.log("No avtr_id in file_path")
				self.setCooldown(config.failCooldown)
			else:
				vrcf.setFavorite(sID)
				self.setCooldown(config.normalCooldown)
			self.cooldown()

			event.accept()
		else:
			event.ignore()

	def btnFavAvatarID(self):
		sID = vrcf.stringToID(self.idEntry.text())
		self.clearId()
		if(sID is None):
			vrcl.log("No avtr_id in string to favorite")
			self.setCooldown(config.failCooldown)
		else:
			vrcf.setFavorite(sID)
			self.setCooldown(config.normalCooldown)
		self.cooldown()

	def btnRevertFav(self):
		self.setCooldown(config.longCooldown)
		vrcf.revertFavorites()
		self.cooldown()

	def btnClearFav(self):
		self.setCooldown(config.longCooldown)
		vrcf.clearFavorites()
		self.cooldown()

	def btnCollectAvtr(self):
		if not self.onCooldown:
			self.setCooldown(config.normalCooldown)
			vrcf.collectAvatar()
			self.cooldown()

	def btnCollectAvtrById(self):
		sID = vrcf.stringToID(self.idEntry.text())
		self.clearId()
		if(sID is None):
			vrcl.log("ID field was empty or doesn't have a valid ID")
			self.setCooldown(config.failCooldown)
		else:
			self.setCooldown(config.normalCooldown)
			vrcf.collectAvatarById(sID)
		self.cooldown()

	def btnRemoveAvtrById(self):
		sID = vrcf.stringToID(self.idEntry.text())
		self.clearId()
		if(sID is None):
			vrcl.log("No avtr_id in string to remove")
			self.setCooldown(config.failCooldown)
		else:
			self.setCooldown(config.normalCooldown)
			vrcf.removeFavoriteID(sID)
		self.cooldown()

	def setCooldown(self, waitTime):
		self.querytime = int(time()) + waitTime

	def clearId(self):
		self.idEntry.setText("") #clear id

	def btnState(self, state):
		if state == "disable":
			self.addIdFavBtn.setEnabled(False)
			self.collectAvtrBtn.setEnabled(False)
			self.collectAvtrIdBtn.setEnabled(False)
			if config.getExtraOptions:
				self.removeAvtrIdBtn.setEnabled(False)
			self.revertFavBtn.setEnabled(False)
			self.clearFavBtn.setEnabled(False)
			self.allowDrop = False
		else:
			self.addIdFavBtn.setEnabled(True)
			self.collectAvtrBtn.setEnabled(True)
			self.collectAvtrIdBtn.setEnabled(True)
			if config.getExtraOptions:
				self.removeAvtrIdBtn.setEnabled(True)
			self.revertFavBtn.setEnabled(True)
			self.clearFavBtn.setEnabled(True)
			self.allowDrop = True

	def cooldown(self):
		if(time() < self.querytime):
			self.onCooldown = True
			self.btnState("disable")
			threading.Timer(1.0, self.cooldown).start()
			self.statusLabel.setText("Cooldown " + str((self.querytime) - int(time())) + "s")
		else:
			self.onCooldown = False
			self.statusLabel.setText("Ready")
			self.btnState("enable")

if(config.getDebugLogEnabled):
	sys.stdout = open(join(config.app_dir, 'debug.log'), mode='a+', encoding='utf-8', errors='ignore', buffering=1)
	#sys.stderr = open(join(config.app_dir,'debug.err.log'), mode='a+', encoding='utf-8', errors='ignore', buffering=1)
	#not catching sys.stderr using debug.bat to catch just err

def suppress_qt_warnings():
	environ["QT_DEVICE_PIXEL_RATIO"] = "0"
	environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
	environ["QT_SCREEN_SCALE_FACTORS"] = "1"
	environ["QT_SCALE_FACTOR"] = "1"

suppress_qt_warnings()
app = QApplication(sys.argv)
vrcf.updatecheck()
appWindow = AppWindow()
appWindow.show()

if(config.useGlobalKeybind):
	try:
		hk.register((config.getGlobalKeyBind), callback=lambda x: appWindow.btnCollectAvtr())
	except SystemHotkey.InvalidKeyError:
		vrcl.log("Invalid key combo, using default ctrl+k")
		hk.register(('control', 'k'), callback=lambda x: appWindow.btnCollectAvtr())
	except Exception as e:
		print(str(e))

sys.exit(app.exec_())
