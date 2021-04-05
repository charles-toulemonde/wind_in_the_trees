""" Python module to determine and plot amplitude and shine evolutions """


import math


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


def update_amplitude_and_shine(chunk, numpydata,
                               frequencies, a_spectrum,
                               graph_amplitude, graph_shine):
    """ update amplitude and shine gramphs """
    amplitude_list = list(graph_amplitude.get_data()[1])
    shine_list = list(graph_shine.get_data()[1])
    sampling_ratio = 10
    sampling_memory = 10.
    length = int((sampling_memory - 1.) * chunk / float(sampling_ratio))
    if len(amplitude_list) > length:
        amplitude_list = amplitude_list[int(chunk / float(sampling_ratio)):]
        shine_list = shine_list[int(chunk / float(sampling_ratio)):]
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
