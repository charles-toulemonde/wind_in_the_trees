#!/usr/bin/python3


""" a Python script to play WAV sounds and visualise them like in IRCAM
snail software """


import sys
import wave
import math
import pyaudio
import numpy
from numpy.fft import fft
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button
from play_and_visualise_sound_background import draw_background
from play_and_visualise_sound_amplitude_and_shine import (
                                update_amplitude_and_shine)
from play_and_visualise_sound_peaks_and_notes import compute_peaks_and_notes
from play_and_visualise_sound_helicoidal_coordinates import (
                                compute_helicoidal_coordinates)
from play_and_visualise_sound_constants import (CHUNK, DIAPASON,
                                                BUTTON_LABEL, LANGUAGE,
                                                OCTAVE_BELOW, OCTAVE_ABOVE,
                                                OCTAVE_RADIUS)


X_LIST = list()


def animate(index, animation_time,
            graph_snail,
            graph_notes, graph_spectrum, graph_peaks,
            graph_shine, graph_amplitude):
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
    spectrum_maxima, notes = compute_peaks_and_notes(frequencies,
                                                     a_spectrum,
                                                     DIAPASON)
    x_list, y_list, z_list, x_list_notes, y_list_notes, z_list_notes = compute_helicoidal_coordinates(
        spectrum_maxima, notes, DIAPASON)
    if len(z_list) > 0:
        ratio = 1. / max(z_list)
    else:
        ratio = 1.
    graph_snail.set_array(ratio * numpy.array(z_list))
    offset_array = numpy.zeros((len(x_list), 2))
    offset_array[:, 0] = x_list
    offset_array[:, 1] = y_list
    offset_array_notes = numpy.zeros((len(x_list_notes), 2))
    offset_array_notes[:, 0] = x_list_notes
    offset_array_notes[:, 1] = y_list_notes
    graph_snail.set_offsets(offset_array)
    amplitudes = amplitude * 250. * numpy.array(z_list)
    graph_snail.set_sizes(amplitudes)
    graph_notes.set_array(numpy.ones(len(z_list_notes)))
    graph_notes.set_offsets(offset_array_notes)
    graph_notes.set_sizes(50. * numpy.ones(len(z_list_notes)))

    x_list = list()
    y_list = list()
    x_list_peaks = list()
    y_list_peaks = list()
    for index in range(len(frequencies)):
        a_frequency = frequencies[index]
        if a_frequency > 20. and index % 2 == 0:
            x_list.append(a_frequency)
            y_value = a_spectrum[index] / max(a_spectrum)
            y_list.append(y_value)
            if y_value > 0.1 :
                for a_maximum in spectrum_maxima:
                    a_frequency_maximum = a_maximum[0]
                    if abs(a_frequency_maximum - a_frequency) < 10.:
                        x_list_peaks.append(a_frequency)
                        y_list_peaks.append(y_value)
    graph_spectrum.set_data(x_list, y_list)
    graph_peaks.set_data(x_list_peaks, y_list_peaks)
    graph_amplitude, graph_shine = update_amplitude_and_shine(
                                        CHUNK, numpydata,
                                        frequencies, a_spectrum,
                                        graph_amplitude, graph_shine)
    animation_time += duration

    return graph_snail, graph_notes, graph_spectrum, graph_peaks, graph_shine, graph_amplitude,


def update_diapason_slider(val):
    """ function called when diapason slider is updated """
    DIAPASON = DIAPASON_SLIDER.val


def on_quit(val):
    """ function called when quit button is pressed """
    plt.close("all")


def init_audio_stream():
    """ initialisation of audio stream """
    if len(sys.argv) == 2:
        input_name = sys.argv[1]
        f_id = wave.open(sys.argv[1], "rb")
        sound_rate = f_id.getframerate()
        audio_stream = PY_AUDIO.open(
            format=PY_AUDIO.get_format_from_width(F_ID.getsampwidth()),
            channels=F_ID.getnchannels(),
            rate=f_id.getframerate(),
            output=True)
    else:
        input_name = "micro"
        f_id = None
        sound_rate = 44100
        audio_stream = PY_AUDIO.open(format=pyaudio.paInt16,
                                     channels=1,
                                     rate=sound_rate,
                                     input=True,
                                     frames_per_buffer=CHUNK)
    return audio_stream, f_id, input_name, sound_rate


if __name__ == "__main__":
    PY_AUDIO = pyaudio.PyAudio()
    AUDIO_STREAM, F_ID, INPUT_NAME, SOUND_RATE = init_audio_stream()
    FIGURE = draw_background(INPUT_NAME)
    plt.subplot(1, 2, 1)
    GRAPHS_SNAIL = plt.scatter([], [], cmap='RdPu', alpha=1.)

    plt.subplot(3, 2, 2)
    GRAPH_NOTES = plt.scatter([], [], cmap='RdPu', alpha=1.)

    sub_figure_2 = plt.subplot(6, 2, 8)
    sub_figure_2.patch.set_facecolor("black")
    plt.xlim(27.5, 10000.)
    plt.ylim(0., 1.)
    GRAPH_SPECTRUM, = plt.semilogx([10., 100., 1000.], [0., 1., 0.], "-",
                                   color="white", linewidth=0.2)
    plt.grid()
    GRAPH_PEAKS, = plt.semilogx([10., 100., 1000.], [0., 1., 0.], "ro",
                                markersize=2)

    sub_figure_2 = plt.subplot(6, 2, 10)
    sub_figure_2.patch.set_facecolor("black")
    plt.xlim(0., 1.)
    plt.ylim(0., 1.)
    GRAPH_SHINE, = plt.plot([], [], "-", color="yellow", linewidth=0.2)

    sub_figure_3 = plt.subplot(6, 2, 12)
    sub_figure_3.patch.set_facecolor("black")
    plt.xlim(0., 1.)
    plt.ylim(-1., 1.)
    GRAPH_AMPLITUDE, = plt.plot([], [], "--", color="grey", linewidth=0.2)

    ANIMATION_TIME = 0.
    y_list = list()

    MY_ANIMATION = animation.FuncAnimation(FIGURE, animate,
                                           frames=None, blit=True,
                                           interval=0, repeat=False,
                                           fargs=(ANIMATION_TIME,
                                                  GRAPHS_SNAIL,
                                                  GRAPH_NOTES,
                                                  GRAPH_SPECTRUM,
                                                  GRAPH_PEAKS,
                                                  GRAPH_SHINE,
                                                  GRAPH_AMPLITUDE))

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
