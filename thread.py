import os
import sys
import datetime

from ultralytics import YOLO
import cv2

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QMessageBox

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from twilio.rest import Client

from config import password, from_email, email_list, rtsp_address, phone_num_list, account_sid, auth_token, twilio_number


class Thread(QThread):
    updateFrame = Signal(QImage)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.status = True
        self.cap = True

        self.rtsp = rtsp_address
        self.target_email = email_list
        self.timeout = 0

        self.server = smtplib.SMTP('smtp.gmail.com: 587')
        self.server.starttls()
        self.server.login(from_email, password)

        self.client = Client(account_sid, auth_token)
        self.target_phone_num = phone_num_list

        #Yolov8 Constants
        self.CONFIDENCE_THRESHOLD = 0.25
        self.RED = (0, 0, 255)

        self.model = YOLO("yolov8n_fire.pt")
        print("Initial Address: " + self.rtsp)

    def change_rtsp(self, address):
        self.rtsp = address
        print("RTSP changes to... " + self.rtsp)

    def run(self):
        print("Connecting to " + self.rtsp + " ...")
        self.cap = cv2.VideoCapture(self.rtsp) # Start Capture of IP Camera
        
        
        while self.status:
            yolov8 = self.model

            ret, frame = self.cap.read()
            if not ret:
                self.timeout -= 1
                continue
            
            detections = yolov8(frame)[0]

            for data in detections.boxes.data.tolist():

                confidence = data[4]

                if float(confidence) < self.CONFIDENCE_THRESHOLD:
                    continue

                xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), self.RED, 2)

                print("FIRE!")
                self.send_email(self.target_email, from_email)
                self.send_sms(self.target_phone_num, twilio_number)
                self.timeout -= 1

            # Reading the image in RGB to display it
            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


            # Creating and scaling QImage
            h, w, ch = color_frame.shape
            img = QImage(color_frame.data, w, h, ch * w, QImage.Format_RGB888)
            scaled_img = img.scaled(640, 480, Qt.KeepAspectRatio)

            # Emit signal
            self.updateFrame.emit(scaled_img)

        sys.exit(-1)
    
    def send_email(self, to_email, from_email):

        if self.timeout == 0:
            for email in to_email:
                message = MIMEMultipart()
                message['From'] = from_email
                message['To'] = email
                message['Subject'] = "Fire Alert!"

                message.attach(MIMEText(f'ALERT - Fire has been detected inside your home! Check your IP Cameras for Confirmation!'))
                self.server.sendmail(from_email, email, message.as_string())

    def send_sms(self, to_phone_num, twilio_number):

        if self.timeout == 0:
            for num in to_phone_num:
                """message = self.client.messages.create(
                     body="ALERT - Fire has been detected inside your home! Check your IP Cameras for Confirmation!",
                     from_= twilio_number,
                     to= num
                 )
                
                print(message.body)"""

            self.timeout = 1000