## Main program for the acoustic tracker project
## Controller function that communicates witht the teensy is stored in Controller.py
## To keep this clean functions are kept in Functions.py

## Import libraries for use in this scoepe 
import matplotlib.pyplot as plt
import time
import numpy as np
import math
from Controller import Controller
from Functions import correlation
from Functions import target_wave
from Functions import read_voltages_two_pins_fastest


# Define the target wave, for the correlation funciton, as the saved recieved wave.
target = target_wave()


def average_waves(averages, command): ### Need to find a better way of doing averaging this is not good
    """ Take in how many waves to average and output the average of those waves.
    """
    import numpy as np
    list_voltages_1 = []
    list_voltages_2 = []
    
    for iteration in range(averages):
        voltages = read_voltages_two_pins_fastest(command.copy())
        list_voltages_1.append(voltages[0])
        list_voltages_2.append(voltages[1])
    
    voltages_1 = np.average(list_voltages_1,axis = 0)
    voltages_2 = np.average(list_voltages_2,axis = 0)

    return voltages_1, voltages_2



import matplotlib.pyplot as plt
import time
#plt.ion()
ax = plt.gca()
li = [plt.plot([1,1], 'x-')[0] for i in range(8)]

while True:
    #Trigger a conversion
    command = {"CMD":2, "ADC0Channels":[23,23,23,23], "ADC1Channels":[38,38,38,38], "PWM_pin":23, "PWMwidth":12}
    voltages_adc_0, voltages_adc_1 = average_waves(15, command)
    
    li[0].set_ydata(voltages_adc_0)
    li[0].set_xdata(range(len(voltages_adc_0)))
    
    target_wave = []
    for i in range(int(0.2*len(voltages_adc_0))):
        target_wave.append(voltages_adc_0[i])
    sample_number_of_echo = 0

    li[1].set_ydata(voltages_adc_1)
    li[1].set_xdata(range(len(voltages_adc_1)))
    
    sample_number_of_echo, correlation_signal = correlation(voltages_adc_1, target_wave)
    correlation_signal = np.multiply(correlation_signal, 0.0001)
    li[2].set_ydata(correlation_signal)
    li[2].set_xdata(range(len(correlation_signal)))
    
    time_to_first_echo = (sample_number_of_echo)/(480000)
    distance_between_transducers = (343 * time_to_first_echo * 100) -7.29  # in cm
    print("Sample Number = ", sample_number_of_echo)
    print("Distance = ", "%.2f" % distance_between_transducers, " cm")
    distance_str = str("%.2f" % distance_between_transducers)
    distance_label = distance_str + " cm"

    
    li[3].set_ydata([-5000,5000])
    li[3].set_xdata([sample_number_of_echo,sample_number_of_echo])
    li[3].set_label(distance_label)
    ax.legend()
    

    ax.set_ylim([-2100,2100]) 
    ax.relim()
    ax.autoscale_view(True,True,True)
    plt.gcf().canvas.draw()
    plt.pause(0.01)
    



    





def calculate_distance(voltages, run_number):

    # Aligning the voltages with the background voltage, to centre around zero volts
    if run_number == 1 or run_number == 2:
        voltages_1 = np.subtract(voltages[0], background_voltage_1)
        voltages_2 = np.subtract(voltages[1], background_voltage_2)
    elif run_number == 3 or run_number == 4:
        voltages_1 = np.subtract(voltages[0], background_voltage_3)
        voltages_2 = np.subtract(voltages[1], background_voltage_1)
    elif run_number == 5 or run_number == 6:
        voltages_1 = np.subtract(voltages[0], background_voltage_3)
        voltages_2 = np.subtract(voltages[1], background_voltage_2)
    else:
        raise Exception('Pick a run number between 1 and 6')
    
    
    
    # Target wave is some percentage of the transmitted signal
    target_wave = []
    for i in range(int(0.2*number_of_samples)):
        if run_number == 1 or run_number == 4 or run_number == 6:
            target_wave.append(voltages_1[i])
        elif run_number == 2 or run_number == 3 or run_number == 5:
            target_wave.append(voltages_2[i])
        else:
            raise Exception('Pick a run number between 1 and 6')
        
    sample_number_of_echo = 0
    
    
    #Now correlate the signal and target wave
    from functions import correlation
    if run_number == 1 or run_number == 4 or run_number == 6:
        sample_number_of_echo, correlation_signal = correlation(voltages_2, target_wave)
    elif run_number == 2 or run_number == 3 or run_number == 5:
        sample_number_of_echo, correlation_signal = correlation(voltages_1, target_wave)
    else:
        raise Exception('Pick a run number between 1 and 6')
    
    
    distance = 0      
    if sample_number_of_echo != 0:
        time_to_first_echo = (sample_number_of_echo)/335000
        distance_between_transducers = 343 * time_to_first_echo
        distance = (distance_between_transducers)*100 # in cm
        distance_str = str("%.2f" % distance)
    else:
        distance_str = "Cant hear anything"
        

    return distance



def average_distances(averages):
    distances_1 = []
    distances_2 = []
    distances_3 = []
    
    for i in range(averages):
        distance_1_1 = calculate_distance(read_and_calculate_values(1) , 1)
        distance_1_2 = calculate_distance(read_and_calculate_values(2) , 2)
        distance_1 = np.average([distance_1_1, distance_1_2])
        distances_1.append(distance_1)
        
        distance_2_1 = calculate_distance(read_and_calculate_values(3) , 3)
        distance_2_2 = calculate_distance(read_and_calculate_values(4) , 4)
        distance_2 = np.average([distance_2_1, distance_2_2])
        distances_2.append(distance_2)
        
        distance_3_1 = calculate_distance(read_and_calculate_values(5) , 5)
        distance_3_2 = calculate_distance(read_and_calculate_values(6) , 6)
        distance_3 = np.average([distance_3_1, distance_3_2])
        distances_3.append(distance_3)
        
    
    return np.average(distances_1), np.average(distances_2), np.average(distances_3),
                      


"""
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)


def animate(i):

    distance_1, distance_2, distance_3 = average_distances(4)
          
    print("D1 1-2 = Average = ", "%.2f" % distance_1)
    print("D2 1-3 = Average = ", "%.2f" % distance_2)
    print("D3 2-3 = Average = ", "%.2f" % distance_3)
    
    angle = math.acos((distance_1**2 + distance_2**2 - distance_3**2)/(2*distance_2*distance_1))
    L = math.cos(angle)*distance_2
    H = math.sin(angle)*distance_2
    
    x_values = [0, distance_1 , L]
    y_values = [0, 0          , H]

    
    ax1.clear()
    ax1.plot(x_values, y_values ,'ro', markersize=20)
    ax1.set_ylim(-0.5,10)
    ax1.set_xlim(-0.5,10)
    ax1.set_title('Locations of transducers')
    ax1.set_xlabel('x axis m')
    ax1.set_ylabel('y axis m')
    ax1.legend()
    


ani = animation.FuncAnimation(fig, animate,  interval = 1500)
plt.show



"""


"""
fig = plt.figure()
ax1 = fig.add_subplot(3,1,1)
ax2 = fig.add_subplot(3,1,2)
ax3 = fig.add_subplot(3,1,3)
fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.5)




def animate(i):
    t1 = time.time()
    run_number = 2
    # Take samples either signle or averaged 
    voltages =  read_and_calculate_values(run_number) 
    #values =  average_waves(15)


    # Aligning the voltages with the background voltage, to centre around zero volts
    if run_number == 1 or run_number == 2:
        voltages_1 = np.subtract(voltages[0], background_voltage_1)
        voltages_2 = np.subtract(voltages[1], background_voltage_2)
    elif run_number == 3 or run_number == 4:
        voltages_1 = np.subtract(voltages[0], background_voltage_3)
        voltages_2 = np.subtract(voltages[1], background_voltage_1)
    elif run_number == 5 or run_number == 6:
        voltages_1 = np.subtract(voltages[0], background_voltage_3)
        voltages_2 = np.subtract(voltages[1], background_voltage_2)
    else:
        raise Exception('Pick a run number between 1 and 6')
    # Target wave is some percentage of the transmitted signal
    target_wave = []
    for i in range(int(0.2*number_of_samples)):
        target_wave.append(voltages_2[i])
    sample_number_of_echo = 0
    
    
    #Now correlate the signal and target wave
    from functions import correlation
    sample_number_of_echo, correlation_signal = correlation(voltages_1, target_wave)
    
            
    if sample_number_of_echo != 0:
        time_to_first_echo = (sample_number_of_echo)/335000
        distance_to_transducer_and_back_in_m = 343 * time_to_first_echo
        distance = (distance_to_transducer_and_back_in_m/2)*100 # in cm
        distance_str = str("%.2f" % distance)
    else:
        distance_str = "Cant hear anything"

        
    ax1.clear()
    ax1.plot(voltages_1, linewidth=0.5)
    label = distance_str + " cm"
    ax1.plot([sample_number_of_echo,sample_number_of_echo],[-3.5,3.5], label=(label))
    ax1.set_ylim([-0.2,0.2]) 
    ax1.set_title('Recieved Signal (Right Speaker)')
    ax1.set_xlabel('Sample Number')
    ax1.set_ylabel('Voltage (V)')
    ax1.legend()
    
    ax2.clear()
    ax2.plot(voltages_2, linewidth=0.5)
    ax2.set_ylim([-2,2])
    ax2.set_title('Transmitted Signal (Left Speaker)')
    ax2.set_xlabel('Sample Number')
    ax2.set_ylabel('Voltage (V)')
    
    ax3.clear()
    ax3.plot(correlation_signal, linewidth=0.5)
    ax2.set_ylim([-2,2])
    ax3.set_title('Correlation Signal')
    ax3.set_xlabel('Sample Number')
    ax3.set_ylabel('Voltage (V)')
    t2 = time.time()
    print("Time = ",t2-t1)

ani = animation.FuncAnimation(fig, animate,  interval = 250)
plt.show

"""