#!/usr/bin/python3


""" a Python script to play WAV sounds and visualise them like in IRCAM
snail software """


import sys
import wave
import math
import pyaudio
import numpy
from numpy.fft import fft
from scipy.signal import argrelextrema
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button


OCTAVE_RADIUS = 0.15
DIAPASON = 440.
OCTAVE_BELOW = 4
OCTAVE_ABOVE = 4
NOTES = {
    "US" : ["A", "A#", "B", "C", "C#", "D",
            "D#", "E", "F", "F#", "G", "G#"],
    "FR" : ["La", "La#", "Si", "Do", "Do#", "Re",
             "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#"]
    }
BUTTON_LABEL = {"US" : "Quit", "FR" : "Quitter"}
CHUNK = 8192
LANGUAGE = "FR"


def draw_background(wav_file_name):
    """ draw helicohidal background """
    plt.xlim(-3, 3.)
    plt.ylim(-2, 2.)
    plt.axis('equal')
    plt.title(wav_file_name, color="white")
    point_number = 1000
    x_coordinates = list()
    y_coordinates = list()
    for index in range(point_number):
        ratio = (1. * index) / (point_number - 1.)
        octave = -OCTAVE_BELOW + ratio * (OCTAVE_BELOW + OCTAVE_ABOVE)
        angle = 2. * math.pi * octave
        radius = 1. + OCTAVE_RADIUS * angle / (2. * math.pi)
        x_coordinate = radius * math.sin(angle)
        y_coordinate = radius * math.cos(angle)
        x_coordinates.append(x_coordinate)
        y_coordinates.append(y_coordinate)
    plt.plot(x_coordinates, y_coordinates,
             "--", color="grey", linewidth=0.2)
    plt.plot(0., 1., "o", color="grey", markersize=2)
    notes = NOTES[LANGUAGE]
    for index in range(12):
        ratio = (1. * index) / 12.
        angle = 2. * math.pi * ratio
        radius = 1.6
        x_coordinates = [0.]
        y_coordinates = [0.]
        x_coordinates.append(radius * math.sin(angle))
        y_coordinates.append(radius * math.cos(angle))
        plt.plot(x_coordinates, y_coordinates,
                 "-", color="grey", linewidth=0.4)
        radius = 1.7
        x_coordinate = radius * math.sin(angle)
        y_coordinate = radius * math.cos(angle)
        plt.text(x_coordinate, y_coordinate,
                 notes[index], fontsize=10,
                 horizontalalignment='center',
                 verticalalignment='center',
                 color="white")
    plt.axis('off')


def compute_maxima_in_spectrum(frequencies, a_spectrum):
    """ compute maxima in spectrum """
    maximum = max(a_spectrum)
    extrema_indices = list(argrelextrema(a_spectrum, numpy.greater))
    possible_maxima = list()
    for a_possible_index in extrema_indices[0]:
        if a_spectrum[a_possible_index] > 0.25 * maximum:
            a_frequency = frequencies[a_possible_index]
            possible_maxima.append([a_frequency,
                                    a_spectrum[a_possible_index]])
    return possible_maxima


def compute_helicoidal_coordinates(spectrum_maxima, diapason):
    """ convert maxima to helicoidal coordinates """
    x_coordinates = list()
    y_coordinates = list()
    z_coordinates = list()
    for a_maximum in spectrum_maxima:
        a_frequency = a_maximum[0]
        an_amplitude = a_maximum[1]
        normalised_frequency = a_frequency / diapason
        condition_1 = (normalised_frequency >= 2 ** (-OCTAVE_BELOW))
        condition_2 = (normalised_frequency <= 2 ** (OCTAVE_ABOVE))
        if condition_1 and condition_2:
            normalised_angle = math.log(normalised_frequency) / math.log(2.)
            angle = 2. * math.pi * normalised_angle
            radius = 1. + OCTAVE_RADIUS * angle / (2. * math.pi)
            x_coordinate = radius * math.sin(angle)
            y_coordinate = radius * math.cos(angle)
            x_coordinates.append(x_coordinate)
            y_coordinates.append(y_coordinate)
            z_coordinates.append(an_amplitude)
    return x_coordinates, y_coordinates, z_coordinates


def animate(index, animation_time, graph):
    """ function used to refresh animation """
    if F_ID != None:
        data = F_ID.readframes(CHUNK)
    else:
        data = AUDIO_STREAM.read(CHUNK)
    numpydata = numpy.frombuffer(data, dtype=numpy.int16)
    if numpy.shape(numpydata)[0] == 0:
        AUDIO_STREAM.stop_stream()
        AUDIO_STREAM.close()
        PY_AUDIO.terminate()
        return graph
    average = numpy.average(numpydata)
    amplitude = 1. * numpy.linalg.norm(numpydata - average) \
                / numpy.shape(numpydata)
    if F_ID != None:
        duration = 1. * numpy.shape(numpydata)[0] / F_ID.getframerate()
        AUDIO_STREAM.write(data)
    else:
        duration = 1. * numpy.shape(numpydata)[0] / 44100.
    a_spectrum = fft(numpydata)
    a_spectrum = numpy.abs(a_spectrum)
    a_spectrum = a_spectrum[:int(a_spectrum.shape[0] / 2)]
    amplitude = (float(max(a_spectrum)) / 52000000.) ** 3.

    if amplitude > 1.:
        amplitude = 1.
    a_spectrum = (1. / max(a_spectrum)) * a_spectrum
    frequencies = (1. / duration) * numpy.array(range(a_spectrum.shape[0]))
    spectrum_maxima = compute_maxima_in_spectrum(frequencies,
                                                 a_spectrum)
    x_list, y_list, z_list = compute_helicoidal_coordinates(
        spectrum_maxima, DIAPASON)
    if len(z_list) > 0:
        ratio = 1. / max(z_list)
    else:
        ratio = 1.
    graph.set_array(ratio * numpy.array(z_list))
    offset_array = numpy.zeros((len(x_list), 2))
    offset_array[:, 0] = x_list
    offset_array[:, 1] = y_list
    graph.set_offsets(offset_array)
    amplitudes = amplitude * 250. * numpy.array(z_list)
    graph.set_sizes(amplitudes)
    animation_time += duration
    return graph,


def update_diapason_slider(val):
    """ function called when diapason slider is updated """
    DIAPASON = DIAPASON_SLIDER.val


def on_quit(val):
    """ function called when quit button is pressed """
    plt.close("all")


def init_audio_stream():
    """ initialisation of audio stream """
    if len(sys.argv) == 2:
        INPUT_NAME = sys.argv[1]
        F_ID = wave.open(sys.argv[1], "rb")
        AUDIO_STREAM = PY_AUDIO.open(
            format=PY_AUDIO.get_format_from_width(F_ID.getsampwidth()),
            channels=F_ID.getnchannels(),
            rate=F_ID.getframerate(),
            output=True)
    else:
        INPUT_NAME = "micro"
        F_ID = None
        AUDIO_STREAM = PY_AUDIO.open(format=pyaudio.paInt16,
                                     channels=1,
                                     rate=44100,
                                     input=True,
                                     frames_per_buffer=CHUNK)
    return AUDIO_STREAM, F_ID, INPUT_NAME


if __name__ == "__main__":
    PY_AUDIO = pyaudio.PyAudio()
    AUDIO_STREAM, F_ID, INPUT_NAME = init_audio_stream()
    FIGURE = plt.figure()
    FIGURE.patch.set_facecolor("black")
    draw_background(INPUT_NAME)
    GRAPH = plt.scatter([], [], cmap='RdPu', alpha=0.5)
    ANIMATION_TIME = 0.

    MY_ANIMATION = animation.FuncAnimation(FIGURE, animate,
                                           frames=None, blit=True,
                                           interval=0, repeat=False,
                                           fargs=(ANIMATION_TIME, GRAPH))

    matplotlib.rcParams["text.color"] = "grey"
    matplotlib.rcParams["font.size"] = 6
    DIAPASON_SLIDER = Slider(plt.axes([0.4, 0.01, 0.22, 0.015]),
                             "diapason", 400, 480,
                             valinit=DIAPASON,
                             color="grey")
    DIAPASON_SLIDER.on_changed(update_diapason_slider)
    QUIT_BUTTON = Button(plt.axes([0.89, 0.01, 0.1, 0.08]),
                   BUTTON_LABEL[LANGUAGE])
    QUIT_BUTTON.on_clicked(on_quit)
    plt.show()
