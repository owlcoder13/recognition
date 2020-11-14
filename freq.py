import numpy as np
import math


def calc_freq(x, rate):
    X = np.fft.fft(x)
    freqs = np.fft.fftfreq(len(x))
    # absX = np.abs(X)

    idx = np.argmax(np.abs(X))
    freq = freqs[idx]
    # freq_in_hertz = abs(freq * rate)

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

    print('max freq', max_freq)

    return freq_coef
