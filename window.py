import os
import sys
import time

import cv2
from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QLineEdit)

from thread import Thread
import config


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        # Title and dimensions
        self.setWindowTitle("Fire Detection")
        self.setGeometry(0, 0, 800, 500)

        # Main menu bar
        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu("File")
        exit = QAction("Exit", self, triggered=qApp.quit)
        self.menu_file.addAction(exit)

        self.menu_about = self.menu.addMenu("&About")
        about = QAction("About Qt", self, shortcut=QKeySequence(QKeySequence.HelpContents),
                        triggered=qApp.aboutQt)
        self.menu_about.addAction(about)

        # Create a label for the display camera
        self.label = QLabel(self)
        self.label.setFixedSize(640, 480)

        # Thread in charge of updating the image
        self.th = Thread(self)
        self.th.finished.connect(self.close)
        self.th.updateFrame.connect(self.setImage)


        self.model_label = QLabel("YOLOv8n Fire Detection Model")
        self.model_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)


        # Email Block
        self.email_label = QLabel("Add Receiving Email: " )
        self.email_input = QLineEdit()
        self.add_email = QPushButton("Add Email")
        self.add_email.clicked.connect(self.add_email_event)


        # SMS Block
        self.sms_label = QLabel("Add Receiving Phone Num.: " )
        self.sms_input = QLineEdit()
        self.add_sms = QPushButton("Add Number")
        self.add_sms.clicked.connect(self.add_sms_event)


        #RTSP Block
        self.rtsp_label = QLabel("Camera Address: " )
        self.rtsp_current = QLabel(self.th.rtsp)

        self.rtsp_change = QLabel("Change Camera Address: " )
        self.rtsp_input = QLineEdit("rtsp://admin:WURYXC@192.168.1.29:554/h264")
        self.rtsp_change_button = QPushButton("Change Camera Address")
        self.rtsp_change_button.clicked.connect(self.rtsp_change_event)



        #Layout    

        rtsp_block = QHBoxLayout()
        rtsp_block.addWidget(self.rtsp_label)
        rtsp_block.addWidget(self.rtsp_current)

        # Block Layout
        block_layout = QVBoxLayout()
        block_layout.addWidget(self.model_label)
        block_layout.addWidget(self.email_label)
        block_layout.addWidget(self.email_input)
        block_layout.addWidget(self.add_email)
        block_layout.addWidget(self.sms_label)
        block_layout.addWidget(self.sms_input)
        block_layout.addWidget(self.add_sms)
        block_layout.addLayout(rtsp_block)
        block_layout.addWidget(self.rtsp_change)
        block_layout.addWidget(self.rtsp_input)
        block_layout.addWidget(self.rtsp_change_button)


        # Buttons layout
        buttons_layout = QHBoxLayout()
        self.button1 = QPushButton("Start")
        self.button2 = QPushButton("Stop/Close")
        self.button1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.button2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        buttons_layout.addWidget(self.button2)
        buttons_layout.addWidget(self.button1)

        right_layout = QHBoxLayout()
        right_layout.addLayout(block_layout, 1)
        right_layout.addLayout(buttons_layout, 1)




        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(right_layout)

        # Central widget
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Connections
        self.button1.clicked.connect(self.start)
        self.button2.clicked.connect(self.kill_thread)
        self.button2.setEnabled(False)

    @Slot()
    def kill_thread(self):
        print("Finishing...")
        self.button2.setEnabled(False)
        self.button1.setEnabled(True)
        self.th.cap.release()
        cv2.destroyAllWindows()
        self.status = False
        self.th.terminate()
        self.th.server.quit()
        # Give time for the thread to finish
        time.sleep(1)

    @Slot()
    def start(self):
        print("Starting...")
        self.button2.setEnabled(True)
        self.button1.setEnabled(False)
        self.th.start()

    @Slot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    
    def add_email_event(self):
        if self.email_input.text() != '':
            
            config.email_list.append(self.email_input.text())
            self.email_input.clear()

            index = 1
            for email in config.email_list:
                print(f"{index} - {email}")
                index += 1
        
        else:
            print("Please input a valid email address...")

    def add_sms_event(self):
        if self.sms_input.text() != '':
            
            config.phone_num_list.append(self.sms_input.text())
            self.sms_input.clear()

            index = 1
            for num in config.phone_num_list:
                print(f"{index} - {num}")
                index += 1
        
        else:
            print("Please input a valid number...")

    def rtsp_change_event(self):
        if self.rtsp_input.text() != '':
            
            config.rtsp_address = self.rtsp_input.text()
            self.th.change_rtsp(config.rtsp_address)
            self.rtsp_current.setText(config.rtsp_address)
            self.rtsp_input.clear()
        
        else:
            print("Please input a valid camera address...")