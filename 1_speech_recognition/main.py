import difflib
import logging
import os
import sys
import threading
import time

import speech_recognition as sr
from PyQt5 import QtGui
from PyQt5.QtWidgets import *

from MainWindow import *

r = sr.Recognizer()
log_format = "%(asctime)s (%(module)s:%(lineno)d) %(levelname)s:%(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)


def record(rate=16000):
    """
    Use the microphone for audio
    :return:
    """
    mic = sr.Microphone(sample_rate=rate)
    with mic as source:
        # r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        return audio


def compare_str(str1, str2):
    """
    Compare the similarity between the two words
    :param str1:
    :param str2:
    :return:
    """
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    isFinished = True  # Used to determine whether to end a speech recognition task
    words = ['play love story', 'open notepad', 'watch video', 'draw a picture', 'calculate some expressions']
    timer = None
    interval = 0.01

    def __init__(self):
        super(Window, self).__init__()
        self.setupUi(self)
        self.setWindowTitle(r"1952733-XingLiu-asr")
        self.setWindowIcon(QtGui.QIcon(r"static\icon.png"))
        _translate = QtCore.QCoreApplication.translate
        self.label_5.setText(_translate("MainWindow", self.words[1]))
        self.label_9.setText(_translate("MainWindow", self.words[3]))
        self.label_11.setText(_translate("MainWindow", self.words[4]))
        self.label_7.setText(_translate("MainWindow", self.words[2]))
        self.label_8.setText(_translate("MainWindow", self.words[0]))
        # self.set_timer()
        # self.isWaked = True

    def poor_hear(self):
        """
        The identification is not clear
        action according to whether the current state is a sleep state or a wake-up state
        :return:
        """
        if self.isWaked:  # wake state
            self.label_3_1.setText("Sorry I can not hear you clearly...\nTry to speak again~")
            # time.sleep(2.5)
            # self.label_3_1.setText("")
        else:
            self.label_3.setText("Sorry I can not hear you clearly...\nTry to speak again~")
            # time.sleep(2.5)
            # self.label_3.setText("")
        return

    def output(self, text):
        """
        Output the recognized command
        :param text:
        :return:
        """
        self.label_3_1.setGeometry(QtCore.QRect(140, 420, 600, 40))
        self.label_3_1.setText("I guess you want to "+text)
        time.sleep(2)
        self.label_3_1.setGeometry(QtCore.QRect(235, 420, 450, 40))
        self.label_3_1.setText("What can I do for you Next?")
        return

    def set_timer(self):
        """
        set timer
        The timer needs to be turned off when switching to the help interface
        The timer is used for the call of the voice recognition task
        :return:
        """
        # self.recognize()
        self.isFinished = True
        self.timer = threading.Timer(self.interval, self.recognize)
        self.timer.start()
        return

    def recognize(self):
        """
        speech recognition function
        :return:
        """
        if not self.isFinished:
            logging.info("The last speech recognition process has not ended")
            return
        else:
            self.isFinished = False
            # self.timer.blockSignals(True)
            if self.isWaked:
                try:
                    audio = record()
                except UserWarning:
                    logging.warning("Failed to read audio from microphone")
                    self.set_timer()
                    return
                else:
                    logging.info("Read audio input successfully")
                    try:
                        word = r.recognize_sphinx(audio)

                    except Warning:
                        logging.warning("speech recognition failed")
                        self.set_timer()
                        return
                    else:
                        logging.info("The recognized word is %s", word)
                        ratio_list = [compare_str(word, command) for command in self.words]
                        max_ratio = max(ratio_list)
                        max_ratio_index = ratio_list.index(max_ratio)
                        if max_ratio < 0.5:
                            logging.warning("Can't figure out what to do")
                            logging.info("The recognition similarity is %s", max_ratio)
                            self.poor_hear()
                            self.set_timer()
                            return
                        # words = ['Music', 'Notepad', 'Video', 'Paint', 'Math']
                        logging.info("The recognition similarity is %s", max_ratio)
                        logging.info("The recognized command is %s", self.words[max_ratio_index])
                        self.output(self.words[max_ratio_index])

                        if max_ratio_index == 0:
                            try:
                                os.startfile(r"static\LoveStory.mp3")
                            except ResourceWarning:
                                logging.warning("Failed to open audio")
                                self.set_timer()
                                return

                        elif max_ratio_index == 1:
                            try:
                                os.system(r"C:\Windows\System32\notepad.exe")
                            except ResourceWarning:
                                logging.warning("Failed to open notepad")
                                self.set_timer()
                                return

                        elif max_ratio_index == 2:
                            try:
                                os.startfile(r"static\video.mp4")
                            except ResourceWarning:
                                logging.warning("Failed to open video")
                                self.set_timer()
                                return

                        elif max_ratio_index == 3:
                            try:
                                os.system(r"C:\Windows\System32\mspaint.exe")
                            except ResourceWarning:
                                logging.warning("Failed to open paint tool")
                                self.set_timer()
                                return

                        elif max_ratio_index == 4:
                            try:
                                os.system(r"C:\Windows\System32\calc.exe")
                            except ResourceWarning:
                                logging.warning("Failed to open calculator")
                                self.set_timer()
                                return
                        else:
                            logging.warning("unknown error!")
                            self.set_timer()
                            return
            else:
                try:
                    audio = record()
                except UserWarning:
                    logging.warning("Failed to read audio from microphone")
                    self.set_timer()
                    return
                else:
                    logging.info("Read audio input successfully")
                    try:
                        word = r.recognize_sphinx(audio)
                        logging.info("The recognized word is %s", word)
                    except Warning:
                        logging.warning("speech recognition failed")
                        self.set_timer()
                        return
                    else:
                        wake_up_ratio = compare_str(word, "Hello")
                        logging.info("The similarity with Hello is %s", wake_up_ratio)
                        if wake_up_ratio > 0.2:
                            self.change_wake_sleep()
                        else:
                            self.poor_hear()
        self.set_timer()
        return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    window.set_timer()
    sys.exit(app.exec())
