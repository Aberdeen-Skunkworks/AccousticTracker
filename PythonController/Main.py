## Main program for the acoustic tracker project
## Controller function that communicates witht the teensy is stored in Controller.py
## To keep this clean functions are kept in Functions.py



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




# Define Constatns
samples_per_wave, time_per_sample = find_samples_per_wave()

teensy_cpu_speed_hz =   168000000 # CPU speed of the teensy board CHECK THIS! very important
delays_to_get_to_end_of_sample = (time_per_sample*512*1000)/((1/teensy_cpu_speed_hz)*4*10**9) # 512 samples 1000 to convert to nanoseconds then the bottom of the fraction is the time for 4 cpu cycles
delays_per_sample = time_per_sample/((1/teensy_cpu_speed_hz)*4*10**6)
adc_resolution = 12             # ADC resolution in bits
distance_correction = - 48      # Distance correction factor im mm
repetitions = 10                # Do not use more than 16 if the teensy is storing the values as 16 bit intagers at 32 bits it can go in the thousands (Will take ages)
PWMdelays = [0, int(delays_per_sample/5), int(2*(delays_per_sample/5)), int(3*(delays_per_sample/5)), int(4*(delays_per_sample/5))]               # Delay of 1 means the delay will take 4 cpu cycles of the teensy (eg at 216MHz 1 would equal a delay of 18.52 nanoseconds)
resolution = 5                  # Number of repetitions to improve spacial resolution = number of points in PWM delays that are below 90
PWMwidth = 6                    # Number of half waves to pulse the transducer with
speed_of_sound, temp = find_speed_of_sound() # Reading the temperature with the use of a Dallas DS18B20 digital temperature sensor: accurate to +-0.5 degrees

first_run = True

print("Speed of sound used is: ","%.2f" % speed_of_sound, "m/s")
print("Calculated for a temp of: ",temp, "Degrees C")

# Ask User to choose a mode to run
print(" ")
print("Control modes:")
print("(1) = Distance between 2 transducers")
print("(2) = Three transdcuer triangulation")
print("(3) = Four transducer optimisation")
print("(negitive numbers) = Debugging and test modes")
print(" ")
choose = input("Please choose a mode from above: ")



## -------------------- Distance between 2 transducers ------------------- ##

if choose == ("1"):

    # Set up plotting axis
    ax = plt.gca()
    li = [plt.plot([1,1], 'x-')[0] for i in range(4)]
    
    ping_trasducer = 6
    recieve_transdcuer = 1
    
    # Create the target wave using the square wave equation taking into account the resolution and number of pulses required Output is scaled to be plotted on microseconds scale
    target_square_wave = square_wave_gen(PWMwidth, resolution, samples_per_wave)[1]
    
    with Controller() as com:
        command, recieved_wave_adc0_or_adc1 = create_read_command(recieve_transdcuer,ping_trasducer,PWMwidth,repetitions) # Read transducer, ping transducer
        while True:
            # Take readings with the following command (Pass com as the controller funciton so that it only connects once at the start)
            output_adc0_sorted, output_adc1_sorted, times_x_axis_sorted = read_with_resolution(command, adc_resolution, com, repetitions, PWMdelays, time_per_sample, teensy_cpu_speed_hz)
            # Allow the choice of what ADC the recieved signal comes from
            if recieved_wave_adc0_or_adc1 == 0:
                target_wave = []
                # Take some percentage of the target wave to use as the target wave
                for i in range(int(0.3*len(output_adc1_sorted))):
                    target_wave.append(output_adc1_sorted[i])
                recieved_signal = output_adc0_sorted
                # Plot the voltage data to the graph as lines
                li[0].set_ydata(output_adc0_sorted)
                li[0].set_xdata(times_x_axis_sorted)
                li[0].set_label("Signal from ADC 0")
                    
            elif recieved_wave_adc0_or_adc1 == 1:
                target_wave = []
                # Take some percentage of the target wave to use as the target wave
                for i in range(int(0.2*len(output_adc0_sorted))):
                    target_wave.append(output_adc0_sorted[i])
                recieved_signal = output_adc1_sorted
                # Plot the voltage data to the graph as lines
                li[1].set_ydata(output_adc1_sorted)
                li[1].set_xdata(times_x_axis_sorted)
                li[1].set_label("Signal from ADC 1")
            else:
                raise Exception('Pick ADC 1 or 0')
                    
            # Send the recieved wave and the target wave to the correlation function  (Swithch target_saved to target_wave if you dont want to use the saved wave)
            sample_number_of_echo, correlation_signal = correlation(recieved_signal, target_square_wave, PWMwidth, resolution)
            correlation_signal = np.multiply(correlation_signal, 0.5) # scale so it is nicer to plot
            correlation_signal_times = []
            for i in range(len(correlation_signal)):
                correlation_signal_times.append(times_x_axis_sorted[i])
            li[2].set_ydata(correlation_signal)
            li[2].set_xdata(correlation_signal_times)
            li[2].set_label("Correlation Fuction")
            
            # Calculate the distance to the transducer, knowing that sample rate is 12 per 40kHz wave and assuming speed of sound in air is 343 m/s
            time_to_first_echo = times_x_axis_sorted[sample_number_of_echo]/1000000
            distance_between_transducers = (speed_of_sound * time_to_first_echo * 1000) + distance_correction  # 100 to convert to cm and correction to allow callibration
            print("Sample Number = ", sample_number_of_echo)
            print("Distance = ", "%.2f" % distance_between_transducers, " mm")
            distance_str = str("%.2f" % distance_between_transducers)
            distance_label = "Estimated distance: " + distance_str + " mm"
        
            # Plot vertical line at the distance so it is visiable on the graph
            li[3].set_ydata([-5000,5000])
            li[3].set_xdata([times_x_axis_sorted[sample_number_of_echo], times_x_axis_sorted[sample_number_of_echo]])
            li[3].set_label(distance_label)
            
            # Commands and labels for plotting the data continioustly
            ax.legend()
            ax.set_ylim([-2,2]) 
            ax.set_ylabel('Voltage (V)')
            ax.set_xlabel('Time (micro seconds)')
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
    pairs = [[1,2],[2,1],[1,3],[3,1],[2,3],[3,2]]
    command_list = []
    recieved_wave_adc0_or_adc1_list = []
    for i in range(6):

        command, recieved_wave_adc0_or_adc1 = create_read_command(pairs[i][0],pairs[i][1],PWMwidth,repetitions)
        command_list.append(command)
        recieved_wave_adc0_or_adc1_list.append(recieved_wave_adc0_or_adc1)
    
    # Create the target wave using the square wave equation taking into account the resolution and number of pulses required Output is scaled to be plotted on microseconds scale
    target_square_wave = square_wave_gen(PWMwidth, resolution, samples_per_wave)[1]
    
    with Controller() as com:
        while True: 
        
            #Keeping track of all 6 distances: 1-2, 2-1, 1-3, 3-1, 2-3, 3-2
            all_distances = []
            
            # Looping through the 6 distances to calculate
            for mesurment in range(6):
                
                # Set up changing variables
                command = command_list[mesurment]
                recieved_wave_adc0_or_adc1 = recieved_wave_adc0_or_adc1_list[mesurment]
                
                # Take readings with the following command (Pass com as the controller funciton so that it only connects once at the start)
                output_adc0_sorted, output_adc1_sorted, times_x_axis_sorted = read_with_resolution(command, adc_resolution, com, repetitions, PWMdelays, time_per_sample, teensy_cpu_speed_hz)
            
                # Allow the choice of what ADC the target signal comes from
                if recieved_wave_adc0_or_adc1 == 0:
                    target_wave = []
                    # Take some percentage of the target wave to use as the target wave
                    for i in range(int(0.2*len(output_adc1_sorted))):
                        target_wave.append(output_adc1_sorted[i])
                    recieved_signal = output_adc0_sorted
                        
                elif recieved_wave_adc0_or_adc1 == 1: 
                    target_wave = []
                    # Take some percentage of the target wave to use as the target wave
                    for i in range(int(0.2*len(output_adc0_sorted))):
                        target_wave.append(output_adc0_sorted[i])
                    recieved_signal = output_adc1_sorted
                else:
                    raise Exception('Pick ADC 1 or 0')
                
                # Plot the voltage data to the graph as lines
                li[0].set_ydata(output_adc0_sorted)
                li[0].set_xdata(times_x_axis_sorted)
                li[0].set_label("Signal from ADC 0")
                
                li[1].set_ydata(output_adc1_sorted)
                li[1].set_xdata(times_x_axis_sorted)
                li[1].set_label("Signal from ADC 1")
                
                # Send the recieved wave and the target wave to the correlation function (Swithch target_saved to target_wave if you dont want to use the saved wave)
                sample_number_of_echo, correlation_signal = correlation(recieved_signal, target_square_wave, PWMwidth, resolution)
                correlation_signal = np.multiply(correlation_signal, 0.5) # scale so it is nicer to plot
                correlation_signal_times = []
                for i in range(len(correlation_signal)):
                    correlation_signal_times.append(times_x_axis_sorted[i])
                li[2].set_ydata(correlation_signal)
                li[2].set_xdata(correlation_signal_times)
                li[2].set_label("Correlation Fuction")
                
                # Calculate the distance to the transducer, knowing that sample rate is 12 per 40kHz wave and assuming speed of sound in air is 343 m/s
                time_to_first_echo = times_x_axis_sorted[sample_number_of_echo]/1000000 # 1,000,000 to convert from microseconds to seconds
                distance_between_transducers = (speed_of_sound * time_to_first_echo * 1000) + distance_correction  # 100 to convert to cm and correction to allow callibration
                #print("Sample Number = ", sample_number_of_echo)
                #print("Distance = ", "%.2f" % distance_between_transducers, " mm")
                distance_str = str("%.2f" % distance_between_transducers)
                distance_label = "Estimated distance: " + distance_str + " mm"
            
                all_distances.append(distance_between_transducers)
                
                # Plot vertical line at the distance so it is visiable on the graph
                li[3].set_ydata([-5000,5000])
                li[3].set_xdata([times_x_axis_sorted[sample_number_of_echo], times_x_axis_sorted[sample_number_of_echo]])
                li[3].set_label(distance_label)
                
    
                # Commands and labels for plotting the data continioustly for axis 1
                ax1.legend()
                ax1.set_ylim([-2,2]) 
                ax1.set_ylabel('Voltage (V)')
                ax1.set_xlabel('Time (micro seconds)')
                title_list = ["Currently sampling between transducer 1 and 2", "Currently sampling between transducer 2 and 1", "Currently sampling between transducer 1 and 3", "Currently sampling between transducer 3 and 1", "Currently sampling between transducer 2 and 3", "Currently sampling between transducer 3 and 2"]
                ax1.set_title(title_list[mesurment])
                ax1.relim()
                ax1.autoscale_view(True,True,True)
                plt.pause(0.01)
                    
            # Average the repeated distances and print to output
            distance_1 = np.average([all_distances[0], all_distances[1]])
            distance_2 = np.average([all_distances[2], all_distances[3]])
            distance_3 = np.average([all_distances[4], all_distances[5]])
            print("")
            print("D1 1-2 = Average = ", "%.2f" % distance_1, " mm")
            print("D2 1-3 = Average = ", "%.2f" % distance_2, " mm")
            print("D3 2-3 = Average = ", "%.2f" % distance_3, " mm")
    
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
            distance_label_1 = "Distance between 1 and 2: " + distance_str_1 + " mm"
            distance_str_2 = str("%.2f" % distance_2)
            distance_label_2 = "Distance between 1 and 3: " + distance_str_2 + " mm"
            distance_str_3 = str("%.2f" % distance_3)
            distance_label_3 = "Distance between 2 and 3: " + distance_str_3 + " mm"
            
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
            ax2.set_xlabel('x axis mm')
            ax2.set_ylabel('y axis mm')
            ax2.legend()
        
## ---------------------- 4 transducer optimisation --------------------- ##
    
elif choose == ("3"):
    
    # Set up plotting axis
    fig = plt.figure()
    ax1 = fig.add_subplot(2,1,1)
    ax2 = fig.add_subplot(2,1,2, projection='3d')
    # Create the lines and points that can be updated every loop. This means the figure does not need cleared every time its updated
    li = [ax1.plot([1,1], 'x-')[0] for i in range(4)]
    
    #lines_3d = [] 
    points = []
    
    points.append( ax2.plot([0.1],[0.1],[0.1], 'ro', markersize=12)) # Need to  be set as floats or they will defalt to ints and not work
    points.append( ax2.plot([0.1],[0.1],[0.1], 'ro', markersize=12))
    points.append( ax2.plot([0.1],[0.1],[0.1], 'ro', markersize=12))
    points.append( ax2.plot([0.1],[0.1],[0.1], 'co', markersize=12))
    points.append( ax2.plot([0.1],[0.1],[0.1], 'co', markersize=12))
    points.append( ax2.plot([0.1],[0.1],[0.1], 'co', markersize=12))
    
    #lines_3d.append( ax2.plot([0.1,0],[0.1,0],[0.1,0]))
    
    ax2.set_xlabel('X axis mm')
    ax2.set_ylabel('Y axis mm')
    ax2.set_zlabel('Z axis mm')
    
    
    # Create the target wave using the square wave equation taking into account the resolution and number of pulses required Output is scaled to be plotted on microseconds scale
    target_square_wave = square_wave_gen(PWMwidth, resolution, samples_per_wave)[1]
    
    #Number of transducers
    Nt=6
    
    #Measured distances numbered from 0 - 5 so transducer 1 is 0 and so on
    dists = [
       #[tid1, tid2, dist],
       [0, 1, None],
       [0, 2, None],
       [0, 3, None],
       [0, 4, None],
       [0, 5, None],
       
       [1, 2, None],
       [1, 3, None],
       [1, 4, None],
       [1, 5, None],
       
       [2, 3, None],
       [2, 4, None],
       [2, 5, None],
       
       [3, 4, None],
       [3, 5, None],
       
       [4, 5, None],
       
       [1, 0, None],
       [2, 0, None],
       [3, 0, None],
       [4, 0, None],
       [5, 0, None],
      
       [2, 1, None],
       [3, 1, None],
       [4, 1, None],
       [5, 1, None],
       
       [3, 2, None],
       [4, 2, None],
       [5, 2, None],
       
       [4, 3, None],
       [5, 3, None],
       
       [5, 4, None],
    ]

    with Controller() as com:
        while True: 

            for pair in range(len(dists)):
                command, recieved_wave_adc0_or_adc1 = create_read_command( dists[pair][0] + 1  , dists[pair][1] + 1 ,PWMwidth,repetitions) ## add one since transducers are numbered from 1 and not zero ...
                # Take readings with the following command (Pass com as the controller funciton so that it only connects once at the start)
                output_adc0_sorted, output_adc1_sorted, times_x_axis_sorted = read_with_resolution(command, adc_resolution, com, repetitions, PWMdelays, time_per_sample, teensy_cpu_speed_hz)
                # Allow the choice of what ADC the recieved signal comes from
                if recieved_wave_adc0_or_adc1 == 0:
                    target_wave = []
                    # Take some percentage of the target wave to use as the target wave
                    for i in range(int(0.3*len(output_adc1_sorted))):
                        target_wave.append(output_adc1_sorted[i])
                    recieved_signal = output_adc0_sorted
                    # Plot the voltage data to the graph as lines
                    li[1].set_ydata(0)
                    li[1].set_xdata(0)
                    li[0].set_ydata(output_adc0_sorted)
                    li[0].set_xdata(times_x_axis_sorted)
                    li[0].set_label("Signal from ADC 0")
                        
                elif recieved_wave_adc0_or_adc1 == 1:
                    target_wave = []
                    # Take some percentage of the target wave to use as the target wave
                    for i in range(int(0.2*len(output_adc0_sorted))):
                        target_wave.append(output_adc0_sorted[i])
                    recieved_signal = output_adc1_sorted
                    li[0].set_ydata(0)
                    li[0].set_xdata(0)
                    li[1].set_ydata(output_adc1_sorted)
                    li[1].set_xdata(times_x_axis_sorted)
                    li[1].set_label("Signal from ADC 1")
                else:
                    raise Exception('Pick ADC 1 or 0')
                
                # Send the recieved wave and the target wave to the correlation function  (Swithch target_saved to target_wave if you dont want to use the saved wave)
                sample_number_of_echo, correlation_signal = correlation(recieved_signal, target_square_wave, PWMwidth, resolution)
                correlation_signal = np.multiply(correlation_signal, 0.6) # scale so it is nicer to plot
                correlation_signal_times = []
                for i in range(len(correlation_signal)):
                    correlation_signal_times.append(times_x_axis_sorted[i])
                li[2].set_ydata(correlation_signal)
                li[2].set_xdata(correlation_signal_times)
                li[2].set_label("Correlation Fuction")
                
                # Calculate the distance to the transducer, knowing that sample rate is 12 per 40kHz wave and assuming speed of sound in air is 343 m/s
                time_to_first_echo = times_x_axis_sorted[sample_number_of_echo]/1000000
                distance_between_transducers = (speed_of_sound * time_to_first_echo * 1000) + distance_correction  # 100 to convert to cm and correction to allow callibration
                distance_str = str("%.2f" % distance_between_transducers)
                distance_label = "Estimated distance: " + distance_str + " mm"
                print()
                print("Distance between transducer ", dists[pair][0] + 1 ," and " ,dists[pair][1] + 1, "is", distance_between_transducers)
                dists[pair][2] = distance_between_transducers
                # Plot vertical line at the distance so it is visiable on the graph
                li[3].set_ydata([-5000,5000])
                li[3].set_xdata([times_x_axis_sorted[sample_number_of_echo], times_x_axis_sorted[sample_number_of_echo]])
                li[3].set_label(distance_label)
                
                # Commands and labels for plotting the data continioustly
                distance_title = "Distance between transducer " + str( dists[pair][0] + 1) + " and "  + str(dists[pair][1] + 1)
                ax1.set_title(distance_title)
                ax1.legend()
                ax1.set_ylim([-2,2]) 
                ax1.set_ylabel('Voltage (V)')
                ax1.set_xlabel('Time (micro seconds)')
                ax1.relim()
                ax1.autoscale_view(True,True,True)
                plt.gcf().canvas.draw()
                plt.pause(0.01)

            #A way of saving the Nt transducer positions to a linear array (which
            #is all that the minimisation can take). We also use this as an
            #opportunity to remove some positions from the minimisation.
            def pos_to_x(tpos):
               x = np.zeros((3*Nt - 3 - 2 * (Nt>1) - 1 * (Nt>2)))
               #First transducer is at 0,0,0 so skip it
               
               #Second transducer is at r1x,0,0, so just save the first coordinate
               if Nt > 1:
                   x[0] = tpos[1][0]
            
               #Third transducer is at r2x,r2y,0
               if Nt > 2:
                   x[1] = tpos[2][0]
                   x[2] = tpos[2][1]
            
               #Do the rest
               for idx in range(3,Nt):
                   x[3+(idx-3)*3+0] = tpos[idx][0]
                   x[3+(idx-3)*3+1] = tpos[idx][1]
                   x[3+(idx-3)*3+2] = tpos[idx][2]
               return x
            
            #The reverse of pos_to_x
            def x_to_pos(x):
               tpos = np.zeros((Nt, 3))
            
               if Nt > 1:
                   tpos[1][0] = x[0]
            
               if Nt > 2:
                   tpos[2][0] = x[1]
                   tpos[2][1] = x[2]
            
               for idx in range(3,Nt):
                   tpos[idx][0] = x[3+(idx-3)*3+0]
                   tpos[idx][1] = x[3+(idx-3)*3+1]
                   tpos[idx][2] = x[3+(idx-3)*3+2]
            
               return tpos
            
            #The function to minmise
            def f(x):
               #Grab the positions out of x
               tpos = x_to_pos(x)
               #Sum up the square distance error
               sumError=0
               for idx1,idx2,d in dists:
                   current_dist = np.linalg.norm(tpos[idx1]-tpos[idx2])
                   error = (current_dist - d)**2
                   sumError += error
               return sumError
            
            #Initial guess for transducer locations
            if first_run:
                inital_guess = [[0,0,0],[90,0,0],[45,45,0],[90,0,200],[45,45,200],[0,0,200]]
            else:
                inital_guess = tpos
                
            x0 = pos_to_x(inital_guess)
            #Call the minimiser
            res = minimize(f, x0, method="nelder-mead", options={'xtol':1e-10})
            #Extract the result
            tpos = x_to_pos(res.x)
            
            #Now check it!
            for idx1,idx2,d in dists:
               current_dist = np.linalg.norm(tpos[idx1]-tpos[idx2])
               print([idx1,idx2]," Mesured distance =", d, "optimised distance =",current_dist)
            
                            

            # Floating point numbers are important for the 3d live plotting to work
            points[0][0]._verts3d[0][0] = tpos[0][0]
            points[0][0]._verts3d[1][0] = tpos[0][1]
            points[0][0]._verts3d[2][0] = tpos[0][2]
            
            """ Plotting lines in 3d only for 1 line needs more work to make it neater
            lines_3d[0][0]._verts3d[0].setflags(write=1)
            lines_3d[0][0]._verts3d[1].setflags(write=1)
            lines_3d[0][0]._verts3d[2].setflags(write=1)
            
            lines_3d[0][0]._verts3d[0][0] = locations[0][0]
            lines_3d[0][0]._verts3d[1][0] = locations[0][1]
            lines_3d[0][0]._verts3d[2][0] = locations[0][2]
            
            lines_3d[0][0]._verts3d[0][1] = location[0]
            lines_3d[0][0]._verts3d[1][1] = location[1]
            lines_3d[0][0]._verts3d[2][1] = location[2]
            """

            points[1][0]._verts3d[0][0] = tpos[1][0]
            points[1][0]._verts3d[1][0] = tpos[1][1]
            points[1][0]._verts3d[2][0] = tpos[1][2]
            
            points[2][0]._verts3d[0][0] = tpos[2][0]
            points[2][0]._verts3d[1][0] = tpos[2][1]
            points[2][0]._verts3d[2][0] = tpos[2][2]
            
            points[3][0]._verts3d[0][0] = tpos[3][0]
            points[3][0]._verts3d[1][0] = tpos[3][1]
            points[3][0]._verts3d[2][0] = tpos[3][2]
            
            points[4][0]._verts3d[0][0] = tpos[4][0]
            points[4][0]._verts3d[1][0] = tpos[4][1]
            points[4][0]._verts3d[2][0] = tpos[4][2]
            
            points[5][0]._verts3d[0][0] = tpos[5][0]
            points[5][0]._verts3d[1][0] = tpos[5][1]
            points[5][0]._verts3d[2][0] = tpos[5][2]
        
            #autoscale_axis_3d(points, ax2)
            ax2.set_xlim([-100, 100])
            ax2.set_ylim([-100, 100])
            ax2.set_zlim([-100, 100])





## ---------------------- New board test --------------------- ##
    
elif choose == ("4"):
    
    with Controller() as com:
        command = {"CMD":2, "ADC0Channels":[14,14,14,14], "ADC1Channels":[39,39,39,39]}
        
        adc_0_output, adc_1_output = read_voltages_two_pins_fastest(command, 1, com, 1)
        
## ----------------------  Debugging and test mode --------------------- ##

elif choose == ("-1"):
    
 # Set up plotting axis
    fig = plt.figure()
    ax1 = fig.add_subplot(2,1,1)
    ax2 = fig.add_subplot(2,1,2)
    
    v_0_five_indivividual = []
    v_1_five_indivividual = []
    
    v_0_five_at_once = []
    v_1_five_at_once = []  
    
    with Controller() as com:
        t1 = time.time()
        repetitions = 1
        command = {"CMD":2, "ADC0Channels":[16,16,16,16], "ADC1Channels":[38,38,38,38], "PWM_pin":-1, "PWMwidth":6, "repetitions":repetitions}
        for i in range(10):
            voltages_adc_0_not_scaled, voltages_adc_1_not_scaled = read_voltages_two_pins_fastest(command.copy(), adc_resolution, com, repetitions)
            v_0_five_indivividual.append(voltages_adc_0_not_scaled)
            v_1_five_indivividual.append(voltages_adc_1_not_scaled)
        
        v_0_five_indivividual = np.average(v_0_five_indivividual, axis = 0)
        v_1_five_indivividual = np.average(v_1_five_indivividual, axis = 0)

        t2 = time.time()
        repetitions = 10
        command = {"CMD":2, "ADC0Channels":[16,16,16,16], "ADC1Channels":[38,38,38,38], "PWM_pin":-1, "PWMwidth":6, "repetitions":repetitions}
        v_0_five_at_once, v_1_five_at_once = read_voltages_two_pins_fastest(command.copy(), adc_resolution, com, repetitions)

        t3 = time.time()
        ax1.plot(v_0_five_indivividual)
        ax1.plot(v_1_five_indivividual)
        ax2.plot(v_0_five_at_once) 
        ax2.plot(v_1_five_at_once)

        print(t2-t1)
        print(t3-t2)


## ----------------------  Debugging and test mode 2 --------------------- ##

elif choose == ("-2"):
    
 # Set up plotting axis
    fig = plt.figure()
    ax1 = fig.add_subplot(2,1,1)
    ax2 = fig.add_subplot(2,1,2)
        
    repetitions = 20
    PWMdelays = [0,10,20,30,40,50,60,70,80]

    
    command = {"CMD":2, "ADC0Channels":[16,16,16,16], "ADC1Channels":[38,38,38,38], "PWM_pin":22, "PWMwidth":10, "repetitions":repetitions, "PWMdelay":0}
            

    with Controller() as com:
        t1 = time.time()
        output_adc0_sorted, output_adc1_sorted, times_x_axis_sorted = read_with_resolution(command, adc_resolution, com, repetitions, PWMdelays)
        t2 = time.time()
        print("Time to run = ", t2-t1)
        
        ax1.plot(times_x_axis_sorted, output_adc0_sorted, 'x-')
        ax2.plot(times_x_axis_sorted, output_adc1_sorted, 'x-')  
        

else:
    print("Come on, pick a correct mode!")
























































