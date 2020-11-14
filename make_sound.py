import math
import wave
import struct

if __name__ == '__main__':
    # http://stackoverflow.com/questions/3637350/how-to-write-stereo-wav-files-in-python
    # http://www.sonicspot.com/guide/wavefiles.html
    freq = 440.0
    data_size = 40000
    fname = "test.wav"
    frate = 11025.0
    amp = 64000.0
    nchannels = 1
    sampwidth = 2
    framerate = int(frate)
    nframes = data_size
    comptype = "NONE"
    compname = "not compressed"
    data = [math.sin(2 * math.pi * freq * (x / frate))
            for x in range(data_size)]
    wav_file = wave.open(fname, 'w')
    wav_file.setparams(
        (nchannels, sampwidth, framerate, nframes, comptype, compname))
    for v in data:
        wav_file.writeframes(struct.pack('h', int(v * amp / 2)))
    wav_file.close()


class OSC(object):
    def __init__(self, frequency=440.0, frame_rate=11025):
        self.frequency = frequency
        self.frame_rate = frame_rate
        self.chunk = 1024
        self.t = 0

    def get_next(self):
        amp = 64000.0

        data = [
            math.sin(2 * math.pi * self.frequency * (t / self.frame_rate))
            for t in
            range(self.t, self.t + self.chunk)
        ]

        self.t += self.chunk

        return b''.join([struct.pack('h', int(v * amp / 2)) for v in data])
