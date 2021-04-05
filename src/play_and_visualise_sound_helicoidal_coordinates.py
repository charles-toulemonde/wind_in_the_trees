""" Python module to compute the helicohidal coordinates of peaks and notes """


import math
from play_and_visualise_sound_constants import (OCTAVE_BELOW, OCTAVE_ABOVE,
                                                OCTAVE_RADIUS)


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
