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


# Define the target wave, for the correlation funciton, as the saved recieved wave.
target = target_wave()

with Controller() as com:
    import matplotlib.pyplot as plt
    import time
    #plt.ion()
    ax = plt.gca()
    li = [plt.plot([1,1], 'x-')[0] for i in range(8)]

    while True:
        #Trigger a conversion
        reply = com.send_json({"CMD":2, "ADC0Channels":[4,4,4,4], "ADC1Channels":[9,9,9,9], "PWM_pin":20, "PWMwidth":8})
        if reply["Status"] != "Success":
            raise Exception("Failed to start conversion", reply)
        
        reply = com.send_json({"CMD":1})
        if reply["Status"] != "Success":
            raise Exception("Failed to download data", reply)

        data=[]
        i = 0
        while i < len(reply["ResultADC0"]):
            data.append(reply["ResultADC0"][i])
            data.append(reply["ResultADC0"][i+1])
            data.append(reply["ResultADC0"][i+2])
            data.append(reply["ResultADC0"][i+3])
            i += 4
        data = np.subtract(data,np.average(data))
        li[0].set_ydata(data)
        li[0].set_xdata(range(len(data)))

        target_wave = []
        for i in range(int(55)):
            target_wave.append(data[i])

        i = 0    
        data=[]
        while i < len(reply["ResultADC1"]):
            data.append(reply["ResultADC1"][i])
            data.append(reply["ResultADC1"][i+1])
            data.append(reply["ResultADC1"][i+2])
            data.append(reply["ResultADC1"][i+3])
            i += 4
        data = np.subtract(data,np.average(data))
        li[1].set_ydata(data)
        li[1].set_xdata(range(len(data)))
        
        sample_number_of_echo, correlation_signal = correlation(data, target)
        correlation_signal = np.multiply(correlation_signal, 0.001)
        li[2].set_ydata(correlation_signal)
        li[2].set_xdata(range(len(correlation_signal)))
        
        time_to_first_echo = (sample_number_of_echo)/(480000)
        distance_between_transducers = (343 * time_to_first_echo * 100) -5.79  # in cm
        print("Sample Number = ", sample_number_of_echo)
        print("Distance = ", "%.2f" % distance_between_transducers, " cm")

        li[3].set_ydata([-5000,5000])
        li[3].set_xdata([sample_number_of_echo,sample_number_of_echo])
        
        ax.set_ylim([-2100,2100]) 
        ax.relim()
        ax.autoscale_view(True,True,True)
        plt.gcf().canvas.draw()
        plt.pause(0.01)
        


def read_and_calculate_values(run_number):
    with Controller() as ctr:
        ctr.send_start(run_number)
        voltages_1 = []
        for pages in range(number_of_pages):
            if run_number == 1 or run_number == 2:
                ctr.send_print_speaker_1()
            elif run_number == 3 or run_number == 4:
                ctr.send_print_speaker_3()
            elif run_number == 5 or run_number == 6:
                ctr.send_print_speaker_3()
            else:
                raise Exception('Pick a run number between 1 and 6')
            
            list_of_serial_reads = ctr.read()
            if len(list_of_serial_reads) == 0:
                print("Error no data read in read_and_calculate_values")
            else:
                for i in range(len(list_of_serial_reads)):
                    int_value = int(list_of_serial_reads[i])
                    voltages_1.append((int_value*3.3)/(2**adc_resolution))
                
        voltages_2 = []
        for pages in range(number_of_pages):
            if run_number == 1 or run_number == 2:
                ctr.send_print_speaker_2()
            elif run_number == 3 or run_number == 4:
                ctr.send_print_speaker_1()
            elif run_number == 5 or run_number == 6:
                ctr.send_print_speaker_2()
            else:
                raise Exception('Pick a run number between 1 and 6')   
                
            list_of_serial_reads = ctr.read()
            if len(list_of_serial_reads) == 0:
                print("Error no data read in read_and_calculate_values")
            else:
                for i in range(len(list_of_serial_reads)):
                    int_value = int(list_of_serial_reads[i])
                    voltages_2.append((int_value*3.3)/(2**adc_resolution))
            
    return voltages_1, voltages_2



def average_waves(averages): ### Need to find a better way of doing averaging this is not good
    """ Take in how many waves to average and output the average of those waves.
    """
    import numpy as np
    
    list_voltages_1 = []
    list_voltages_2 = []
    
    for iteration in range(averages):
        voltages = read_and_calculate_values()
        list_voltages_1.append(voltages[0])
        list_voltages_2.append(voltages[1])
    
    voltages_1 = np.average(list_voltages_1,axis = 0)
    voltages_2 = np.average(list_voltages_2,axis = 0)

    return voltages_1, voltages_2




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