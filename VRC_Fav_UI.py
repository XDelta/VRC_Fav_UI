# pylint: disable=W0622,E0611
import sys, ctypes
from os.path import join
from time import time

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGridLayout, QLineEdit#, QCheckBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from Config import applongname, config
import VRC_Fav_Fnc as vrcf
from Logging import vrcl

myappid = 'tk.deltawolf.vrcfav_qt' # unique id string for windows to show taskbar icon
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

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

		self.clearFavBtn = QPushButton('[Clear All Favorites]', self)
		self.clearFavBtn.clicked.connect(self.btnClearFav)
		layout.addWidget(self.clearFavBtn, 7, 0, 1, 2)

		self.revertFavBtn = QPushButton('[Revert Favorites.json]', self)
		self.revertFavBtn.clicked.connect(self.btnRevertFav)
		layout.addWidget(self.revertFavBtn, 8, 0, 1, 2)

		self.statusLabel = QLabel('Ready', self)
		layout.addWidget(self.statusLabel, 9, 0, 1, 2)

		# OnTop = QCheckBox("On Top")
		# OnTop.toggled.connect(toggleTop())
		# layout.addWidget(OnTop,7,0)

		# if (OnTop.isChecked()):
		# 	print("checked")
			# flags.append(Qt.WindowStaysOnTopHint)

		self.setLayout(layout)

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
		if(event.mimeData().hasImage):# and self.allowDrop == True
			event.setDropAction(Qt.CopyAction)
			file_path = event.mimeData().urls()[0].toLocalFile()
			sID = vrcf.stringToID(file_path)
			if(sID is None):
				vrcl.log("No avtr id in file_path")
				self.idEntry.setText("")
				self.setCooldown(config.failCooldown)
			else:
				vrcf.setFavorite(sID)
				self.idEntry.setText("")
				self.setCooldown(config.normalCooldown)
			self.cooldown()

			event.accept()
		else:
			event.ignore()

	def btnFavAvatarID(self):
		sID = vrcf.stringToID(self.idEntry.text())
		if(sID is None):
			vrcl.log("No avtr id in string")
			self.idEntry.setText("") #clear id
			self.setCooldown(config.failCooldown)
		else:
			vrcf.setFavorite(sID)
			self.idEntry.setText("") #clear id
			self.setCooldown(config.normalCooldown)
		self.cooldown()

	def btnRevertFav(self):
		vrcf.revertFavorites()
		self.setCooldown(config.longCooldown)
		self.cooldown()

	def btnClearFav(self):
		vrcf.clearFavorites()
		self.setCooldown(config.longCooldown)
		self.cooldown()

	def btnCollectAvtr(self):
		vrcf.collectAvatar()
		self.setCooldown(config.normalCooldown)
		self.cooldown()

	def btnCollectAvtrById(self):
		sID = vrcf.stringToID(self.idEntry.text())
		if(sID is None):
			vrcl.log("No avtr id in string to collect")
			self.idEntry.setText("") #clear id
			self.setCooldown(config.failCooldown)
		else:
			vrcf.collectAvatarById(sID)
			self.idEntry.setText("") #clear id
			self.setCooldown(config.normalCooldown)
		self.cooldown()

	def setCooldown(self, waitTime):
		self.querytime = int(time()) + waitTime


	def btnState(self, state):
		if state == "disable":
			self.addIdFavBtn.setEnabled(False)
			self.revertFavBtn.setEnabled(False)
			self.clearFavBtn.setEnabled(False)
			self.collectAvtrBtn.setEnabled(False)
			self.collectAvtrIdBtn.setEnabled(False)
			# self.allowDrop = False
		else:
			self.addIdFavBtn.setDisabled(False)
			self.revertFavBtn.setDisabled(False)
			self.clearFavBtn.setDisabled(False)
			self.collectAvtrBtn.setDisabled(False)
			self.collectAvtrIdBtn.setDisabled(False)
			# self.allowDrop = True

	def cooldown(self):
		if(time() < self.querytime):
			self.btnState("disable")
			QTimer.singleShot(1000, lambda: self.cooldown())
			self.statusLabel.setText("Cooldown " + str((self.querytime) - int(time())) + "s")
		else:
			self.statusLabel.setText("Ready")
			self.btnState("enable")

if(config.getDebugLogEnabled):
	sys.stdout = open(join(config.app_dir, 'debug.log'), mode='a+', encoding='utf-8', errors='ignore', buffering=1)
	#sys.stderr = open(join(config.app_dir,'debug.err.log'), mode='a+', encoding='utf-8', errors='ignore', buffering=1)
	#not catching sys.stderr using debug.bat to catch just err

app = QApplication(sys.argv)
appWindow = AppWindow()
appWindow.show()
sys.exit(app.exec_())
