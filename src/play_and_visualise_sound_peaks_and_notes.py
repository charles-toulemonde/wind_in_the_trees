""" Python module to compute peaks and notes in a given spectrum """


import math
import numpy
from scipy.signal import argrelextrema


def compute_peaks_and_notes(frequencies, a_spectrum, diapason):
    """ compute maxima in spectrum """
    maximum = max(a_spectrum)
    extrema_indices = list(argrelextrema(a_spectrum, numpy.greater))
    possible_maxima = list()
    for a_possible_index in extrema_indices[0]:
        if a_spectrum[a_possible_index] > 0.2 * maximum:
            a_frequency = frequencies[a_possible_index]
            possible_maxima.append([a_frequency,
                                    a_spectrum[a_possible_index]])
    possible_notes = list()
    maximum_note = 0.
    for a_maximum in possible_maxima:
        a_frequency = a_maximum[0]
        if a_frequency > 27.5:
            x = 12. * (math.log(a_frequency) - math.log(diapason)) \
                / math.log(2.)
            x = round(x) # shift by -3 for saxophones
            possible_notes.append([x, a_maximum[1]])
            if a_maximum[1] > maximum_note:
                maximum_note = a_maximum[1]
    notes = list()
    for a_possible_note in possible_notes:
        if a_possible_note[1] > (0.05 * maximum_note):
            index = a_possible_note[0]
            note_frequency = (diapason / 2.) * 2. ** (index / 12.)
            notes.append([note_frequency,
                          a_possible_note[1] / maximum_note])
    return possible_maxima, notes
