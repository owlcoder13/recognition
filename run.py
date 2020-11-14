from __future__ import division
from PyQt5 import QtWidgets, QtCore
import sys  # We need sys so that we can pass argv to QApplication
import os
from PyQt5.QtCore import QTimer, QThread, Qt
import pyaudio
import sounddevice as sd
import wave
from pprint import pprint
import numpy as np
import time
import threading
from myplot import MyPlot, Spec
from widgets import VContainer, HContainer, LogWrite
from freq import calc_freq
import math
from make_sound import OSC

import matplotlib.pyplot as plt

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "file.wav"

frames = []


def find_devices():
    i = 0
    for a in sd.query_devices():
        yield i, a['name']


class PlayFileThread(QtCore.QThread):
    plotting = QtCore.pyqtSignal(object)
    logging = QtCore.pyqtSignal(object)

    def __init__(self, parent, play_device_number):
        QtCore.QThread.__init__(self, parent)
        self.dn = play_device_number
        self.p = pyaudio.PyAudio()
        self.stream = None

    def create_output_stream(self, channels=None, samplewidth=None, framerate=None):
        self.stream = self.p.open(
            format=self.p.get_format_from_width(samplewidth),
            channels=channels,
            rate=framerate,
            output=True,
            output_device_index=self.dn
        )

    def close_stream(self):
        self.stream.stop_stream()
        self.stream.close()

    def run(self):
        self.logging.emit('start playing')

        spf = wave.open("test.wav", "rb")

        self.create_output_stream(
            channels=spf.getnchannels(),
            samplewidth=spf.getsampwidth(),
            framerate=spf.getframerate()
        )

        signal = spf.readframes(CHUNK)

        while signal:
            self.stream.write(signal)
            signal = spf.readframes(CHUNK)
            display_signal = np.frombuffer(signal, 'int16')
            self.plotting.emit(display_signal)

        self.close_stream()


class PlayOSC(PlayFileThread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.osc = OSC()
        self.stop = False

    def set_freq(self, freq):
        self.osc.frequency = freq

    def run(self):
        self.logging.emit('start playing')

        self.create_output_stream(
            channels=1,
            samplewidth=2,
            framerate=self.osc.frame_rate
        )

        while self.stop is False:
            signal = np.frombuffer(self.osc.get_next(), 'int16')
            self.plotting.emit(signal)
            self.stream.write(signal)

        self.close_stream()


class Wnd(HContainer):
    def inputCBox(self):
        c_box = QtWidgets.QComboBox()
        for i, name in find_devices():
            c_box.addItem(name)
            if 'USB' in name:
                c_box.setCurrentText(name)
        self.input_cbox = c_box
        return self.input_cbox

    def outputCBox(self):
        c_box = QtWidgets.QComboBox()
        for i, name in find_devices():
            c_box.addItem(name)
            if 'default' in name:
                c_box.setCurrentText(name)
        self.output_cbox = c_box
        return self.output_cbox

    def plot(self, signal):
        self.graphWidget.clear()
        self.graphWidget.plot(signal)

        freq_coef = calc_freq(signal, 11024)
        freq_coef.sort(key=lambda x: x[0])
        # plt.plot([f for f, c in freq_coef], [c for f, c in freq_coef])
        # plt.show()
        # coef_list = [c for f, c in freq_coef]
        self.fft.setXRange(0, 1000)
        self.fft.clear()
        self.fft.plot([f for f, c in freq_coef], [c for f, c in freq_coef])

    def __init__(self, *args, **kwargs):
        super(Wnd, self).__init__(*args, **kwargs)

        self.t = None
        self.osc = None

        self.input_cbox = None
        self.output_cbox = None

        left = VContainer()
        right = VContainer()

        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.slider.setMinimum(20)
        self.slider.setMaximum(500)
        left.addWidget(self.slider)
        self.slider.valueChanged.connect(self.change_freq)

        self.addWidget(left)
        self.addWidget(right)

        devices = HContainer()
        devices.addWidget(self.inputCBox())
        devices.addWidget(self.outputCBox())
        left.addWidget(devices)

        spf = wave.open("wav.wav", "r")
        signal = spf.readframes(-1)
        signal = np.frombuffer(signal, "int16")
        self.signal = signal

        self.graphWidget = MyPlot()
        left.addWidget(self.graphWidget)

        self.fft = Spec()
        # self.fft.setYRange(0, 100000, padding=0)
        left.addWidget(self.fft)

        self.buttons = HContainer()

        btn = QtWidgets.QPushButton()
        btn.setText('Record')
        self.buttons.addWidget(btn)
        btn.clicked.connect(self.get_device_num)

        btn = QtWidgets.QPushButton()
        btn.setText('Play')
        self.buttons.addWidget(btn)
        btn.clicked.connect(self.play_file)

        left.addWidget(self.buttons)

        self.logger = LogWrite()
        right.addWidget(self.logger)

    def get_device_num(self):
        index = self.input_cbox.currentIndex()
        self.logger.addMessage('device index is %d' % index)
        record_audio(index)

    def get_output_num(self):
        index = self.output_cbox.currentIndex()
        self.logger.addMessage('device index is %d' % index)
        return index

    def play_file(self):

        self.osc = OSC()

        self.t = PlayOSC(self, self.get_output_num())
        # self.t = PlayFileThread(self, self.get_output_num())
        self.t.plotting.connect(self.plot)
        self.t.logging.connect(self.logger.addMessage)
        self.change_freq()
        self.t.start()

    def change_freq(self):
        new_freq = self.slider.value()
        print('change freq', new_freq)
        self.t.set_freq(new_freq)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setFixedWidth(1000)
        self.setFixedHeight(800)

        wnd = Wnd()
        self.setCentralWidget(wnd)


def record_audio(input_device):
    # def play_thread():
    #
    #     # output_stream = pa.open(
    #     #     format=FORMAT,
    #     #     channels=CHANNELS,
    #     #     rate=RATE,
    #     #     output=True,
    #     #     frames_per_buffer=CHUNK,
    #     #     output_device_index=find_output_device()
    #     # )
    #
    #     time.sleep(0.1)
    #
    #     while 1:
    #         if len(frames) > 0:
    #             f = frames.pop(0)
    #             output_stream.write(f, CHUNK)

    # pt = threading.Thread(target=play_thread)
    # pt.start()

    # def callback(in_data, frame_count, time_info, status):
    #     frames.append(in_data)
    #     return (in_data, pyaudio.paContinue)

    pa = pyaudio.PyAudio()

    stream = pa.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=input_device,
        # stream_callback=callback
    )

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        print('record', i)
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

    stream.stop_stream()
    stream.close()

    # output_stream.stop_stream()
    # output_stream.close()

    pa.terminate()

    wf = wave.open('wav.wav', 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pa.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\nexit from application")
        exit()


if __name__ == '__main__':
    main()
