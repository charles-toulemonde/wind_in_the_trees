""" Python module to draw the background of the visualisation tool """


import math
import matplotlib.pyplot as plt
from play_and_visualise_sound_constants import (OCTAVE_BELOW, OCTAVE_ABOVE,
                                                OCTAVE_RADIUS, NOTES, LANGUAGE)


def draw_background(input_name):
    """ draw helicohidal background """
    figure = plt.figure(input_name,
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
