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


def draw_background():
    """ draw helicohidal background """
    figure = plt.figure(INPUT_NAME,
                        figsize=(8, 6), dpi=100,
                        facecolor='k', edgecolor='k')
    figure.patch.set_facecolor("black")
    plt.subplot(1, 2, 1)
    plt.xlim(-2., 2.)
    plt.ylim(-2., 2.)
    plt.axis('equal')
    plt.axis('off')
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
    plt.subplot(3, 2, 2)
    plt.xlim(-2., 2.)
    plt.ylim(-2., 2.)
    plt.axis('equal')
    plt.axis('off')
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
                 notes[index], fontsize=8,
                 horizontalalignment='center',
                 verticalalignment='center',
                 color="white")
    return figure


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
    possible_notes = list()
    maximum_note = 0.
    for a_maximum in possible_maxima:
        a_frequency = a_maximum[0]
        if a_frequency > 50:
            while a_frequency >= 440.:
                a_frequency /= 2.
            while a_frequency <= 220.:
                a_frequency *= 2.
            possible_notes.append([a_frequency, a_maximum[1]])
            if a_maximum[1] > maximum_note:
                maximum_note = a_maximum[1]
    notes = list()
    for a_possible_note in possible_notes:
        if a_possible_note[1] > (0.05 * maximum_note):
            index = 12. * math.log(a_possible_note[0] / 220.) / math.log(2.)
            index = round(index) # shift by -3 for saxophones
            note_frequency = 220. * 2. ** (index / 12.)
            notes.append([note_frequency,
                          a_possible_note[1] / maximum_note])
    return possible_maxima, notes


def compute_shine(frequencies, a_spectrum):
    """ compute sound shine from spectrum """
    shine = 0.
    value_sum = 0.
    for index in range(len(frequencies)):
        a_frequency = frequencies[index]
        if a_frequency > 20. and a_frequency < 3000.:
            a_value = a_spectrum[index] ** 2
            value_sum += a_value
            shine += a_frequency * a_value
    shine /= value_sum
    shine = math.log(shine)
    return shine


def compute_helicoidal_coordinates(spectrum_maxima, notes, diapason):
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
    x_coordinates_notes = list()
    y_coordinates_notes = list()
    z_coordinates_notes = list()
    for a_note in notes:
        a_frequency = a_note[0]
        an_amplitude = a_note[1]
        normalised_frequency = a_frequency / diapason
        condition_1 = (normalised_frequency >= 2 ** (-OCTAVE_BELOW))
        condition_2 = (normalised_frequency <= 2 ** (OCTAVE_ABOVE))
        if condition_1 and condition_2:
            normalised_angle = math.log(normalised_frequency) / math.log(2.)
            angle = 2. * math.pi * normalised_angle
            radius = 1.
            x_coordinate = radius * math.sin(angle)
            y_coordinate = radius * math.cos(angle)
            x_coordinates_notes.append(x_coordinate)
            y_coordinates_notes.append(y_coordinate)
            z_coordinates_notes.append(an_amplitude)
    return x_coordinates, y_coordinates, z_coordinates, x_coordinates_notes, y_coordinates_notes, z_coordinates_notes


def update_amplitude_and_shine(numpydata,
                               frequencies, a_spectrum,
                               graph_amplitude, graph_shine):
    """ update amplitude and shine gramphs """
    amplitude_list = list(graph_amplitude.get_data()[1])
    shine_list = list(graph_shine.get_data()[1])
    sampling_ratio = 10
    sampling_memory = 10.
    length = int((sampling_memory - 1.) * CHUNK / float(sampling_ratio))
    if len(amplitude_list) > length:
        amplitude_list = amplitude_list[int(CHUNK / float(sampling_ratio)):]
        shine_list = shine_list[int(CHUNK / float(sampling_ratio)):]
    shine = compute_shine(frequencies, a_spectrum)
    sign = 1.
    if len(shine_list) > 0:
        max_shine = max(shine_list)
    else:
        max_shine = 100.
    for index in range(len(numpydata)):
        if index % sampling_ratio == 0:
            amplitude_list.append(sign * abs(numpydata[index] / 2.**32))
            shine_list.append(shine / 10.)
            sign = -sign
    x_list = list()
    for index in range(len(amplitude_list)):
        x_list.append(1. * index / (len(amplitude_list) - 1.))
    graph_amplitude.set_data(x_list, amplitude_list)
    graph_shine.set_data(x_list, shine_list)
    return graph_amplitude, graph_shine 


def animate(index, animation_time,
            graph_snail_0, graph_snail_1, graph_snail_2, graph_snail_3,
            graph_notes, graph_amplitude, graph_shine):
    """ function used to refresh animation """
    if F_ID != None:
        data = F_ID.readframes(CHUNK)
    else:
        data = AUDIO_STREAM.read(CHUNK)
    numpydata = numpy.frombuffer(data, dtype=numpy.int32)
    if numpy.shape(numpydata)[0] == 0:
        AUDIO_STREAM.stop_stream()
        AUDIO_STREAM.close()
        PY_AUDIO.terminate()
        return graph_snail
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
    spectrum_maxima, notes = compute_maxima_in_spectrum(
                                                    frequencies, a_spectrum)
    x_list, y_list, z_list, x_list_notes, y_list_notes, z_list_notes = compute_helicoidal_coordinates(
        spectrum_maxima, notes, DIAPASON)
    if len(z_list) > 0:
        ratio = 1. / max(z_list)
    else:
        ratio = 1.
    graph_snail_0.set_array(graph_snail_1.get_array())
    graph_snail_0.set_offsets(graph_snail_1.get_offsets())
    graph_snail_0.set_sizes(graph_snail_1.get_sizes())
    graph_snail_1.set_array(graph_snail_2.get_array())
    graph_snail_1.set_offsets(graph_snail_2.get_offsets())
    graph_snail_1.set_sizes(graph_snail_2.get_sizes())
    graph_snail_2.set_array(graph_snail_3.get_array())
    graph_snail_2.set_offsets(graph_snail_3.get_offsets())
    graph_snail_2.set_sizes(graph_snail_3.get_sizes())
    graph_snail_3.set_array(ratio * numpy.array(z_list))
    offset_array = numpy.zeros((len(x_list), 2))
    offset_array[:, 0] = x_list
    offset_array[:, 1] = y_list
    offset_array_notes = numpy.zeros((len(x_list_notes), 2))
    offset_array_notes[:, 0] = x_list_notes
    offset_array_notes[:, 1] = y_list_notes
    graph_snail_3.set_offsets(offset_array)
    amplitudes = amplitude * 250. * numpy.array(z_list)
    graph_snail_3.set_sizes(amplitudes)
    graph_notes.set_array(numpy.ones(len(z_list_notes)))
    graph_notes.set_offsets(offset_array_notes)
    graph_notes.set_sizes(50. * numpy.ones(len(z_list_notes)))
    graph_amplitude, graph_shine = update_amplitude_and_shine(
                                        numpydata,
                                        frequencies, a_spectrum,
                                        graph_amplitude, graph_shine)
    animation_time += duration

    return graph_snail_0, graph_snail_1, graph_snail_2, graph_snail_3, graph_notes, graph_amplitude, graph_shine,


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
    FIGURE = draw_background()
    GRAPHS_SNAIL = list()
    plt.subplot(1, 2, 1)
    GRAPHS_SNAIL.append(plt.scatter([], [], cmap='RdPu', alpha=0.125))
    GRAPHS_SNAIL.append(plt.scatter([], [], cmap='RdPu', alpha=0.25))
    GRAPHS_SNAIL.append(plt.scatter([], [], cmap='RdPu', alpha=0.5))
    GRAPHS_SNAIL.append(plt.scatter([], [], cmap='RdPu', alpha=1.))
    plt.subplot(3, 2, 2)
    GRAPH_NOTES = plt.scatter([], [], cmap='RdPu', alpha=1.)
    sub_figure_2 = plt.subplot(6, 2, 12)
    sub_figure_2.patch.set_facecolor("black")
    plt.xlim(0., 1.)
    plt.ylim(-1., 1.)
    GRAPH_AMPLITUDE, = plt.plot([], [], "--", color="grey", linewidth=0.2)
    sub_figure_3 = plt.subplot(6, 2, 10)
    sub_figure_3.patch.set_facecolor("black")
    plt.xlim(0., 1.)
    plt.ylim(0., 1.)
    GRAPH_SHINE, = plt.plot([], [], "-", color="yellow", linewidth=0.2)
    ANIMATION_TIME = 0.

    y_list = list()
    MY_ANIMATION = animation.FuncAnimation(FIGURE, animate,
                                           frames=None, blit=True,
                                           interval=0, repeat=False,
                                           fargs=(ANIMATION_TIME,
                                                  GRAPHS_SNAIL[0],
                                                  GRAPHS_SNAIL[1],
                                                  GRAPHS_SNAIL[2],
                                                  GRAPHS_SNAIL[3],
                                                  GRAPH_NOTES,
                                                  GRAPH_AMPLITUDE,
                                                  GRAPH_SHINE))

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
