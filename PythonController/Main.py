## Main program for the acoustic tracker project
## Controller function that communicates witht the teensy is stored in Controller.py
## To keep this clean functions are kept in Functions.py



## Import libraries for use in this scoepe 
import matplotlib.pyplot as plt
import numpy as np
from Controller import Controller
from Functions import correlation
from Functions import target_wave
from Functions import read_voltages_two_pins_fastest
from Functions import average_waves
from Functions import find_background_voltages
from Functions import scale_around_zero
from unit_tests import run_tests



# Run unit tests to check for errors
print(" ")
if run_tests():
    pass
else:
     raise Exception('Error some or multiple tests failed, aborting')



# Define Constatns
target = target_wave() # Define the target wave, for the correlation funciton, as the saved recieved wave.
adc_resolution = 12
target_wave_adc0_or_adc1 = 0
distance_correction = - 6.15 



# Ask User to choose a mode to run
print(" ")
print("Control modes:")
print("(1) = Distance between 2 transducers")
print("(2) = Three transdcuer triangulation")
print(" ")
choose = input("Please choose a mode from above: ")



## -------------------- Distance between 2 transducers ------------------- ##

if choose == ("1"):

    # Set up plotting axis
    ax = plt.gca()
    li = [plt.plot([1,1], 'x-')[0] for i in range(8)]
    
    while True:
        #Trigger the average funvtion to take readings with the following command
        command = {"CMD":2, "ADC0Channels":[23,23,23,23], "ADC1Channels":[38,38,38,38], "PWM_pin":23, "PWMwidth":6}
        background_voltage_0, background_voltage_1 = find_background_voltages(command, adc_resolution)
        voltages_adc_0_not_scaled, voltages_adc_1_not_scaled = average_waves(25, adc_resolution, command)
        voltages_adc_0, voltages_adc_1 = scale_around_zero(background_voltage_0, background_voltage_1, voltages_adc_0_not_scaled, voltages_adc_1_not_scaled, adc_resolution)
    
        # Allow the choice of what ADC the target signal comes from
        if target_wave_adc0_or_adc1 == 0:
            target_wave = []
            # Take some percentage of the target wave to use as the target wave
            for i in range(int(0.2*len(voltages_adc_0))):
                target_wave.append(voltages_adc_0[i])
            recieved_signal = voltages_adc_1
                
        elif target_wave_adc0_or_adc1 == 1:
            target_wave = []
            # Take some percentage of the target wave to use as the target wave
            for i in range(int(0.2*len(voltages_adc_1))):
                target_wave.append(voltages_adc_1[i])
            recieved_signal = voltages_adc_0
        else:
            raise Exception('Pick ADC 1 or 0')
                
        # Plot the voltage data to the graph as lines
        li[0].set_ydata(voltages_adc_0)
        li[0].set_xdata(range(len(voltages_adc_0)))
        li[0].set_label("Signal from ADC 0")
        
        li[1].set_ydata(voltages_adc_1)
        li[1].set_xdata(range(len(voltages_adc_1)))
        li[1].set_label("Signal from ADC 1")
        
        # Send the recieved wave and the target wave to the correlation function
        sample_number_of_echo, correlation_signal = correlation(recieved_signal, target_wave)
        correlation_signal = np.multiply(correlation_signal, 0.5) # scale so it is nicer to plot
        li[2].set_ydata(correlation_signal)
        li[2].set_xdata(range(len(correlation_signal)))
        li[2].set_label("Correlation Fuction")
        
        # Calculate the distance to the transducer, knowing that sample rate is 12 per 40kHz wave and assuming speed of sound in air is 343 m/s
        time_to_first_echo = (sample_number_of_echo)/(480000)
        distance_between_transducers = (343 * time_to_first_echo * 100) + distance_correction  # 100 to convert to cm and correction to allow callibration
        print("Sample Number = ", sample_number_of_echo)
        print("Distance = ", "%.2f" % distance_between_transducers, " cm")
        distance_str = str("%.2f" % distance_between_transducers)
        distance_label = "Estimated distance: " + distance_str + " cm"
    
        # Plot vertical line at the distance so it is visiable on the graph
        li[3].set_ydata([-5000,5000])
        li[3].set_xdata([sample_number_of_echo,sample_number_of_echo])
        li[3].set_label(distance_label)
        
        # Commands and labels for plotting the data continioustly
        ax.legend()
        ax.set_ylim([-2,2]) 
        ax.set_ylabel('Voltage (V)')
        ax.set_xlabel('Sample Number')
        ax.relim()
        ax.autoscale_view(True,True,True)
        plt.gcf().canvas.draw()
        plt.pause(0.01)



## -------------------- Three transdcuer triangulation ------------------- ##
    
elif choose == ("2"):
    print("You have chosen Three transdcuer triangulation mode")
    print("In progress........")




# -------------------------------------------------------------------------- #

else:
    print("Come on, pick a correct mode!")
























































