## Main program for the acoustic tracker project
## Controller function that communicates witht the teensy is stored in Controller.py
## To keep this clean functions are kept in Functions.py



## Import libraries for use in this scope 
import matplotlib.pyplot as plt
import numpy as np
import time
import math
from mpl_toolkits.mplot3d import Axes3D
from Controller import Controller
from Functions import correlation
from Functions import target_wave
from Functions import read_voltages_two_pins_fastest
from Functions import average_waves
from Functions import find_background_voltages
from Functions import scale_around_zero
from Functions import transducer_info
from unit_tests import run_tests




# Run unit tests to check for errors
print(" ")
if run_tests():
    pass
else:
     raise Exception('Error some or multiple tests failed, aborting')



# Define Constatns
target_saved = target_wave() # Define the target wave, for the correlation funciton, as the saved recieved wave.
adc_resolution = 12
target_wave_adc0_or_adc1 = 0
distance_correction = - 6.51 
repetitions = 2


# Ask User to choose a mode to run
print(" ")
print("Control modes:")
print("(1) = Distance between 2 transducers")
print("(2) = Three transdcuer triangulation")
print("(3) = Ping 4th listen on 1,2 and 3")
print(" ")
choose = input("Please choose a mode from above: ")



## -------------------- Distance between 2 transducers ------------------- ##

if choose == ("1"):

    # Set up plotting axis
    ax = plt.gca()
    li = [plt.plot([1,1], 'x-')[0] for i in range(4)]
    with Controller() as com:
        while True:
            #Trigger the average funvtion to take readings with the following command (Pass com as the controller funciton so that it only connects once at the start)
            command = {"CMD":2, "ADC0Channels":[23,23,23,23], "ADC1Channels":[38,38,38,38], "PWM_pin":20, "PWMwidth":6, "repetitions":repetitions}
            background_voltage_0, background_voltage_1 = find_background_voltages(command, adc_resolution, com, repetitions)
            voltages_adc_0_not_scaled, voltages_adc_1_not_scaled = read_voltages_two_pins_fastest(command, adc_resolution, com, repetitions)
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
                for i in range(int(0.3*len(voltages_adc_1))):
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
            
            # Send the recieved wave and the target wave to the correlation function  (Swithch target_saved to target_wave if you dont want to use the saved wave)
            sample_number_of_echo, correlation_signal = correlation(recieved_signal, target_saved)
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
    
    # Set up plotting axis
    fig = plt.figure()
    ax1 = fig.add_subplot(2,1,1)
    ax2 = fig.add_subplot(2,1,2)
    
    # Create the lines and points that can be updated every loop. This means the figure does not need cleared every time its updated
    li = [ax1.plot([1,1], 'x-')[0] for i in range(4)]
    li_2 = [ax2.plot([1,1], 'x-')[0] for i in range(3)]
    points = [ax2.plot([1,1], 'o', markersize=12)[0] for i in range(3)]
    
    # List of commands that cycle through what transducer is pinging and which is recieving
    command_list = [
    {"CMD":2, "ADC0Channels":[16,16,16,16], "ADC1Channels":[38,38,38,38], "PWM_pin":39, "PWMwidth":6},
    {"CMD":2, "ADC0Channels":[16,16,16,16], "ADC1Channels":[38,38,38,38], "PWM_pin":22, "PWMwidth":6},
    
    {"CMD":2, "ADC0Channels":[23,23,23,23], "ADC1Channels":[16,16,16,16], "PWM_pin":39, "PWMwidth":6},
    {"CMD":2, "ADC0Channels":[23,23,23,23], "ADC1Channels":[16,16,16,16], "PWM_pin":20, "PWMwidth":6},
    
    {"CMD":2, "ADC0Channels":[23,23,23,23], "ADC1Channels":[38,38,38,38], "PWM_pin":22, "PWMwidth":6},
    {"CMD":2, "ADC0Channels":[23,23,23,23], "ADC1Channels":[38,38,38,38], "PWM_pin":20, "PWMwidth":6}]
    
    # List of what ADC the target wave will be on
    target_wave_adc0_or_adc1_list = [0,1,1,0,1,0]
    
    with Controller() as com:
        while True: 
        
            #Keeping track of all 6 distances: 1-2, 2-1, 1-3, 3-1, 2-3, 3-2
            all_distances = []
            
            # Looping through the 6 distances to calculate
            for mesurment in range(6):
                
                # Set up changing variables
                command = command_list[mesurment]
                target_wave_adc0_or_adc1 = target_wave_adc0_or_adc1_list[mesurment]
                
                #Trigger the average funvtion to take readings with the command from the list (Pass com as the controller funciton so that it only connects once at the start)
                background_voltage_0, background_voltage_1 = find_background_voltages(command, adc_resolution, com)
                voltages_adc_0_not_scaled, voltages_adc_1_not_scaled = average_waves(5, adc_resolution, command, com)
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
                
                # Send the recieved wave and the target wave to the correlation function (Swithch target_saved to target_wave if you dont want to use the saved wave)
                sample_number_of_echo, correlation_signal = correlation(recieved_signal, target_saved)
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
            
                all_distances.append(distance_between_transducers)
                
                # Plot vertical line at the distance so it is visiable on the graph
                li[3].set_ydata([-5000,5000])
                li[3].set_xdata([sample_number_of_echo,sample_number_of_echo])
                li[3].set_label(distance_label)
                
    
                # Commands and labels for plotting the data continioustly for axis 1
                ax1.legend()
                ax1.set_ylim([-2,2]) 
                ax1.set_ylabel('Voltage (V)')
                ax1.set_xlabel('Sample Number')
                title_list = ["Currently sampling between transducer 1 and 2", "Currently sampling between transducer 2 and 1", "Currently sampling between transducer 1 and 3", "Currently sampling between transducer 3 and 1", "Currently sampling between transducer 2 and 3", "Currently sampling between transducer 3 and 2"]
                ax1.set_title(title_list[mesurment])
                ax1.relim()
                ax1.autoscale_view(True,True,True)
                plt.pause(0.01)
                    
            # Average the repeated distances and print to output
            distance_1 = np.average([all_distances[0], all_distances[1]])
            distance_2 = np.average([all_distances[2], all_distances[3]])
            distance_3 = np.average([all_distances[4], all_distances[5]])
              
            print("D1 1-2 = Average = ", "%.2f" % distance_1)
            print("D2 1-3 = Average = ", "%.2f" % distance_2)
            print("D3 2-3 = Average = ", "%.2f" % distance_3)
    
            # Performing trig funcitons on the distances to calcuate their relitive positions: H = height of triangle from transducer 3 to the x axis. L = distance between y axis and transducer 3
            # Dealing with math domain errors when the distances are not physically possible due to errors
            if (distance_1**2 + distance_2**2 - distance_3**2)/(2*distance_2*distance_1) >= 1:
                angle = 0
            elif (distance_1**2 + distance_2**2 - distance_3**2)/(2*distance_2*distance_1) <= -1:
                angle = math.pi
            else:
                angle = math.acos((distance_1**2 + distance_2**2 - distance_3**2)/(2*distance_2*distance_1))
            L = math.cos(angle)*distance_2
            H = math.sin(angle)*distance_2
            
            # Creating the dynamic labels that update what the distances are and are displayed in the legend
            distance_str_1 = str("%.2f" % distance_1)
            distance_label_1 = "Distance between 1 and 2: " + distance_str_1 + " cm"
            distance_str_2 = str("%.2f" % distance_2)
            distance_label_2 = "Distance between 1 and 3: " + distance_str_2 + " cm"
            distance_str_3 = str("%.2f" % distance_3)
            distance_label_3 = "Distance between 2 and 3: " + distance_str_3 + " cm"
            
            # Updating the line and point data for all three lines and points
            li_2[0].set_ydata([0, 0])
            li_2[0].set_xdata([0, distance_1])
            li_2[0].set_label(distance_label_1)
            
            li_2[1].set_ydata([0, H])
            li_2[1].set_xdata([0, L])
            li_2[1].set_label(distance_label_2)
            
            li_2[2].set_ydata([0, H])
            li_2[2].set_xdata([distance_1, L])
            li_2[2].set_label(distance_label_3)
            
            points[0].set_ydata([0])
            points[0].set_xdata([0])
            points[0].set_label("Transducer 1")
            
            points[1].set_ydata([0])
            points[1].set_xdata([distance_1])
            points[1].set_label("Transducer 2")
            
            points[2].set_ydata([H])
            points[2].set_xdata([L])
            points[2].set_label("Transducer 3")
            
            # Commands and labels for plotting the data continioustly for axis 2
            ax2.set_aspect('equal', 'datalim')
            ax2.relim()       
            ax2.autoscale_view(True,True,True)
            #ax2.set_ylim([-0.5,10]) 
            #ax2.set_xlim([-0.5,10]) 
            plt.gcf().canvas.draw()
            plt.pause(0.01)
            ax2.set_title('Locations of transducers')
            ax2.set_xlabel('x axis cm')
            ax2.set_ylabel('y axis cm')
            ax2.legend()
        
## ---------------------- Ping 4th listen on 1,2 and 3 --------------------- ##
    
elif choose == ("3"):
    
    # Set up plotting axis
    fig = plt.figure()
    ax1 = fig.add_subplot(2,1,1)
    ax2 = fig.add_subplot(2,1,2)
    
    # Create the lines and points that can be updated every loop. This means the figure does not need cleared every time its updated
    li = [ax1.plot([1,1], 'x-')[0] for i in range(4)]
    li_2 = [ax2.plot([1,1], 'x-')[0] for i in range(3)]
    points = [ax2.plot([1,1], 'o', markersize=12)[0] for i in range(3)]
    
    
    # Command order for listening is transducer 1 then 2 then 3 (Dont care about recording transmitting transducer as we pretend we cant read it)
    # Ping 4 and listen on 1, 2 and 3
    command_list = [
    {"CMD":2, "ADC0Channels":[17,17,17,17], "ADC1Channels":[16,16,16,16], "PWM_pin":19, "PWMwidth":6},
    {"CMD":2, "ADC0Channels":[17,17,17,17], "ADC1Channels":[38,38,38,38], "PWM_pin":19, "PWMwidth":6},
    {"CMD":2, "ADC0Channels":[23,23,23,23], "ADC1Channels":[17,17,17,17], "PWM_pin":19, "PWMwidth":6}]
    
    # List of what ADC the target_wave will be on: Therefore the recieved signal will be on the other ADC
    target_wave_adc0_or_adc1_list = [0, 0, 1]
    
    with Controller() as com:
        while True: 
        
            #Keeping track of all 6 distances: 1-2, 2-1, 1-3, 3-1, 2-3, 3-2
            all_distances = []
            
            # Looping through the 6 distances to calculate
            for mesurment in range(3):
                
                # Set up changing variables
                command = command_list[mesurment]
                target_wave_adc0_or_adc1 = target_wave_adc0_or_adc1_list[mesurment]
                
                #Trigger the average funvtion to take readings with the command from the list (Pass com as the controller funciton so that it only connects once at the start)
                background_voltage_0, background_voltage_1 = find_background_voltages(command, adc_resolution, com)
                voltages_adc_0_not_scaled, voltages_adc_1_not_scaled = average_waves(5, adc_resolution, command, com)
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
                
                # Send the recieved wave and the target wave to the correlation function (Swithch target_saved to target_wave if you dont want to use the saved wave)
                sample_number_of_echo, correlation_signal = correlation(recieved_signal, target_saved)
                correlation_signal = np.multiply(correlation_signal, 0.5) # scale so it is nicer to plot
                li[2].set_ydata(correlation_signal)
                li[2].set_xdata(range(len(correlation_signal)))
                li[2].set_label("Correlation Fuction")
                
                # Calculate the distance to the transducer, knowing that sample rate is 12 per 40kHz wave and assuming speed of sound in air is 343 m/s
                time_to_first_echo = (sample_number_of_echo)/(480000)
                distance_between_transducers = (343 * time_to_first_echo * 100) + distance_correction  # 100 to convert to cm and correction to allow callibration
                #print("Sample Number = ", sample_number_of_echo)
                #print("Distance = ", "%.2f" % distance_between_transducers, " cm")
                distance_str = str("%.2f" % distance_between_transducers)
                distance_label = "Estimated distance: " + distance_str + " cm"
            
                all_distances.append(distance_between_transducers)
                
                # Plot vertical line at the distance so it is visiable on the graph
                li[3].set_ydata([-5000,5000])
                li[3].set_xdata([sample_number_of_echo,sample_number_of_echo])
                li[3].set_label(distance_label)
                
    
                # Commands and labels for plotting the data continioustly for axis 1
                ax1.legend()
                ax1.set_ylim([-2,2]) 
                ax1.set_ylabel('Voltage (V)')
                ax1.set_xlabel('Sample Number')
                title_list = ["Currently sampling transducer 1 ", "Currently sampling transducer 2 ", "Currently sampling  transducer 3"]
                ax1.set_title(title_list[mesurment])
                ax1.relim()
                ax1.autoscale_view(True,True,True)
                plt.pause(0.01)
            
            print("")
            print("Distance from 1 to 4 = ", "%.2f" % all_distances[0])
            print("Distance from 2 to 4 = ", "%.2f" % all_distances[1])
            print("Distance from 3 to 4 = ", "%.2f" % all_distances[2])





else:
    print("Come on, pick a correct mode!")
























































