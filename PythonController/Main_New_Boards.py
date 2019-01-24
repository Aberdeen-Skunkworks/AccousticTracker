# New Boards Main

## Import libraries for use in this scope 
import matplotlib.pyplot as plt
import numpy as np
import time
import math
from scipy.optimize import minimize
from mpl_toolkits.mplot3d import Axes3D
from Controller import Controller
from Functions import correlation
from Functions import read_voltages_two_pins_fastest
from Functions import find_background_voltages
from Functions import scale_around_zero
from Functions import transducer_info
from Functions import pwm_delay_to_microseconds
from Functions import read_with_resolution
from Functions import square_wave_gen
from Functions import find_temperature
from Functions import find_speed_of_sound
from Functions import optimise_location
from Functions import autoscale_axis_3d
from Functions import create_read_command
from unit_tests import run_tests
from Functions import find_samples_per_wave


V_ref = 3.302 # Voltage Reference
repetitions = 6

with Controller() as com:
    command = {"CMD":5, "repetitions":repetitions, "ADC1Channels":[39,39,39,39]}
    
    adc_0_output, adc_1_output, teensy_reply = read_voltages_two_pins_fastest(command, 1, com, 1)
    
    plt.clf()
    y_values = np.multiply(np.divide(adc_1_output[:len(adc_1_output)], 4095),V_ref)
    x_values = np.linspace(1, len(y_values), len(y_values))
    plt.subplot(1,2,1)
    plt.plot(x_values, y_values, "ro", markersize=4)
    plt.xlabel("Samples")
    plt.ylabel("Voltage V")
    
    sorted_x_values = np.zeros(len(adc_1_output))

    sample_period_mili = teensy_reply["sample_period_nano"][0]/1000000
    nop_delay_total_mili = (teensy_reply["nop_time_delay_nano"][0]*teensy_reply["nop_loops"][0])/1000000
    repetitions_counter = 0
    for reps in range(repetitions):
        for i in range(512):
            sorted_x_values[i + reps*512] = sample_period_mili*i + repetitions_counter*nop_delay_total_mili
        repetitions_counter += 1

    plt.subplot(1,2,2)
    plt.plot(sorted_x_values, y_values,"ro", markersize=4)
    plt.xlabel("Time miliseconds")
    plt.ylabel("Voltage V")
