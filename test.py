import wave
import numpy as np
import math

spf = wave.open("test.wav", "r")
rate = spf.getframerate()  # 11025  in Hz
sw = spf.getsampwidth()  # sample width in bytes
frames = spf.getnframes()
channels = spf.getnchannels()

seconds = frames / rate

print('frame rate', rate)
print('sample width', sw)
print('frames', frames)
print('channels', channels)
print('seconds', seconds)

signal = spf.readframes(512 * 2)
x = np.frombuffer(signal, 'int16')
print('count of frames', len(x))

# s = signal[0]
X = np.fft.fft(x)
freqs = np.fft.fftfreq(len(x))
absX = np.abs(X)

idx = np.argmax(np.abs(X))
freq = freqs[idx]
freq_in_hertz = abs(freq * rate)

freq_coef = list()

for coef, freq in zip(X, freqs):
    value = math.sqrt(coef.real ** 2 + coef.imag ** 2)
    freq_coef.append((abs(freq * rate), value))

max_coef = 0
max_freq = 0
for f, c in freq_coef:
    if c > max_coef:
        max_coef = c
        max_freq = f

