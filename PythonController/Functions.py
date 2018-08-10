## Functions used in the main acoustic tracker program

def square_wave_gen(number_half_waves, resolution, samples_per_wave):
    """
    Takes in number of half waves and resolution in multiples of 12 samples per wave 1 = 12 samples per wave 2 = 24 so on 
    Output square wave oscillating at 40,000 Hz with the x axis in microseconds and centered around zero    
    """
    from scipy import signal
    import matplotlib.pyplot as plt
    import numpy as np
    number_half_waves += 10

    # One wave is 25 microseconds
    t = np.linspace(0, 12.5*number_half_waves, int(samples_per_wave*resolution*(number_half_waves/2)), endpoint=False)
    #wave = -signal.square(2 * np.pi * 0.04 * t)*1.65
    
    
    Fs = 40000 * 12.5 * 2                  ## Sampling Rate
    f  = 40000                       ## Frequency (in Hz)
    ####### sine wave ###########
    wave = -np.sin(2 * np.pi * f * t / Fs)
    triangle = signal.triang(len(t))
    peaked_wave = np.multiply(triangle,wave)

    
    
    
    return t, wave
"""
import matplotlib.pyplot as plt
number_half_waves = 10
resolution = 10
    
t, wave = square_wave_gen(number_half_waves, resolution)
plt.plot(t, wave, 'x-')
plt.ylim(-2, 2)    
 """      



def correlation(signal, target_wave, PWMwidth, resolution, plot = False):
    """ Correlation function that takes in both a signal and a target wave signal and performes a correlation funciton on them. 
    It will output the index of the signal where the waves correlate most. Comment out the plotting lines to see the correlation plotted.
    """
    import numpy as np
   
    #Correlate the signal and target wave
    correlation_signal = []
    for i in range(len(signal) - len(target_wave)):
       csum = 0
       for j in range(len(target_wave)):
           csum += signal[i + j] * target_wave[j]
       if i < (PWMwidth*resolution*14):
           csum = 0
       correlation_signal.append(csum)
    
    # Show the correlator function and both waves on the same plot if the user sets plot to True.
    if plot:
        import matplotlib.pyplot as plt
        plt.plot(correlation_signal, linewidth=0.5)
        plt.plot(signal, linewidth=0.5)
        plt.plot(target_wave, linewidth=0.5)
        plt.show()

    #Find the highest correlation index
    maxindex = np.argmax(correlation_signal)
     
    return maxindex, correlation_signal



def target_wave(): 
    """ Funciton that returns the saved target wave for the correlation funciton to use. This is a 200 sample set of a recieved acoustic signal.
    Code below used to print out the saved wave
    counter = 0
    for i in range(20):
        print(saved_moved[counter], ",", saved_moved[counter+1], ",", saved_moved[counter+2], ",",saved_moved[counter+3], ",",saved_moved[counter+4], ",",saved_moved[counter+5], ",",saved_moved[counter+6], ",",saved_moved[counter+7], ",",saved_moved[counter+8], ",",saved_moved[counter+9], ",",)
        counter = counter + 10
    """
    target_sent = [-0.0056396484374999995 , -1.4912841796874998 , -1.4510009765624998 , -1.445361328125 , -1.464697265625 , -1.461474609375 , -1.4300537109375 , 1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 ,
1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 , -1.4413330078125 , -1.445361328125 , -1.5073974609374998 , -1.5025634765625 , -1.4397216796874999 , -1.4316650390624999 , 1.6250244140624999 ,
1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 , -1.4461669921875 , -1.4316650390624999 , -1.51787109375 , -1.5235107421874998 , -1.4397216796874999 ,
-1.4155517578124999 , 1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 , -1.4413330078125 , -1.409912109375 , -1.5041748046874999 ,
-1.5251220703125 , -1.432470703125 , -1.397021484375 , 1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 , -1.4679199218749999 ,
-1.4219970703125 , -1.5122314453124999 , -1.5364013671874999 , -1.4469726562499998 , -1.4091064453125 , 1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999 , 1.6250244140624999,
1.6250244140624999 , -1.4751708984374998 , -1.4276367187499999]

    return target_sent

                
                                 
def digital_pin_to_sc1a(ADC, pin):
    """
    Function to take in which ADC you want to use on the teensy and a digital output pin number and returns the sc1a number that the ADC uses to label the pins
    It will raise an exeption if an invalid pin is chosen or invalid ADC number.
    """
    if ADC == 0:
    
        # Index is digital pin - value is sc1a number
        sc1a = [None , None , None , None , None , None , None , None , None , None , 
        None , None , None , None , 5 , 14 , 8 , 9 , 13 , 12 , 6 , 7 , 15 , 4 , None , 
        None , None , None , None , None , None , None , None , 17 , 18 , None , None , 
        None , None , None , None , None , None , None , None , None , None , None , None , 
        None , None , None , None , None , None , None , None , None , None , None , None , 
        None , None , None , 3 , None , 23 , None , 1 , None , 26]
        
        if pin > len(sc1a):
            raise Exception("Error: Please choose valid digital pin less than 70")
        elif sc1a[pin] == None:
            raise Exception("Error: ADC:0 is not connected to this pin")
        else:
            return  sc1a[pin]
            

    elif ADC == 1:
        # Index is digital pin - value is sc1a number  (Added 8 and 9 manually)
        sc1a = [None , None , None , None , None , None , None , None , None , None , 
        None , None , None , None , None , None , 8 , 9 , None , None , None , None , 
        None , None , None , None , None , None , None , None , None , 14 , 15 , None , 
        None , 4 , 5 , 6 , 7 , 17 , None , None , None , None , None , None , None , None , 
        None , 10 , 11 , None , None , None , None , None , None , None , None , None , None , 
        None , None , None , None , 19 , None , 23 , None , 1 , None , 18]
        
        if pin > len(sc1a):
            raise Exception("Error: Please choose valid digital pin less than 71")
        elif sc1a[pin] == None:
            raise Exception("Error: ADC:1 is not connected to this pin")
        else:
            return  sc1a[pin]

    else:
        raise Exception("Error: Please choose either ADC:0 or ADC:1")
        


def read_voltages_two_pins_fastest(command, adc_resolution, com, repetitions):
    import numpy as np
    """
    Takes in a command formatted as:
    {"CMD":2, "ADC0Channels":[23,23,23,23], "ADC1Channels":[38,38,38,38], "PWM_pin":23, "PWMwidth":8}
    - Where command 2 tells the teensy board that you want to read pins.
    - The ADC channel numbers correspond to pins on the teensy and must be accesable by that ADC or it wont work as intended.
    - The command takes the digital pin numbers and converts them automatically to sc1a numbers and checks whether or not the corresponding ADC can use that pin
    - This mode is for both ADC's to read only 1 pin each so that the highest reading resolution possible is atchieved.
    - It is possible on a few pins to read with both ADC's therefore to test if they are giving the same outputs can be setupt to read the same signal.
    - The PWM pin takes the digital pin number of the pin you want to output the pulse signal from
    - Pwm Width takes in a number of half waves of the pulse you want. 8 will give you 4 full square wave pulses.
    - This function assumes voltage range of 0-3.3 volts and a ADC resolution of 12 bits. (Otherwise voltages will be scaled wrong)
    """
    
    # Check that all ADC channels are the same for each ADC in the command
    ADC0_channels = command["ADC0Channels"]
    ADC1_channels = command["ADC1Channels"]
    for i in range(len(ADC0_channels)):
        if ADC0_channels[0] != ADC0_channels[i] or ADC1_channels[0] != ADC1_channels[i]:
            raise Exception("This mode requires all channels of each individual ADC to be the same")
            
    # Send commands to the teensy board using json and check if the correct response is recieved
    reply = com.send_json(command)
    if reply["Status"] != "Success":
        raise Exception("Failed to start conversion", reply)
    
    #print(reply)
    
    # Initialise the output arrays and then loop through the result format to save the buffer output values into a single array
    adc_0_output=[]
    i = 0
    
    while i < len(reply["ResultADC0"]):
        adc_0_output.append(reply["ResultADC0"][i])
        adc_0_output.append(reply["ResultADC0"][i+1])
        adc_0_output.append(reply["ResultADC0"][i+2])
        adc_0_output.append(reply["ResultADC0"][i+3])
        i += 4

    adc_1_output=[]
    i = 0
    while i < len(reply["ResultADC1"]):
        adc_1_output.append(reply["ResultADC1"][i])
        adc_1_output.append(reply["ResultADC1"][i+1])
        adc_1_output.append(reply["ResultADC1"][i+2])
        adc_1_output.append(reply["ResultADC1"][i+3])
        i += 4
        
    # Divide out the repitions so that the average output of the teensys multiple samples is outputed by this function        
    return np.divide(adc_0_output, repetitions), np.divide(adc_1_output, repetitions)



def find_background_voltages(command, adc_resolution, com, repetitions):
    """
    Funciton to run first so that the background pin voltage can be found and used to scale the output around zero vols
    """
    import numpy as np
    command_no_pwm = command.copy()
    command_no_pwm["PWM_pin"] = -1
    voltages_0, voltages_1 = read_voltages_two_pins_fastest(command_no_pwm, adc_resolution, com, repetitions)
    

    return np.average(voltages_0), np.average(voltages_1)
    


def scale_around_zero(ADC_0_background, ADC_1_background, adc_0_output, adc_1_output, adc_resolution):
    """
    Funciton to scale the ADC outputs around zero volts
    """
    import numpy as np
    
    # Subtracting the background voltages of the adc outputs from each value so that the range changes from 0,4096 to roughly -2048,2048
    adc_0_output = np.subtract(adc_0_output, ADC_0_background)
    adc_1_output = np.subtract(adc_1_output, ADC_1_background)
    
    # Scale the ADC range to the voltage ragne of 0 - 3.3 volts
    voltages_0 = []
    voltages_1 = []
    for i in range(len(adc_0_output)):
        int_value_adc0 = int(adc_0_output[i])
        int_value_adc1 = int(adc_1_output[i])
        
        voltages_0.append((int_value_adc0*3.3)/(2**adc_resolution))
        voltages_1.append((int_value_adc1*3.3)/(2**adc_resolution))
        
    return voltages_0, voltages_1



def average_waves(averages, adc_resolution, command, com): # Redundant as averaging now done on teensy
    """ Take in how many waves to average, the adc_resoultion and the board command. Output the average of those waves.
    """
    import numpy as np
    list_voltages_1 = []
    list_voltages_2 = []
    
    # Send read command and save to a list for each number of averages asked for
    for iteration in range(averages):
        voltages = read_voltages_two_pins_fastest(command.copy(), adc_resolution, com)
        list_voltages_1.append(voltages[0])
        list_voltages_2.append(voltages[1])
    
    # Use numpy to average the list of lists into the voltages to output
    voltages0 = np.average(list_voltages_1,axis = 0)
    voltages1 = np.average(list_voltages_2,axis = 0)

    return voltages0, voltages1
      

def transducer_info(transducer_number):
    
    read_pin = [16, 38, 23, 17]
    pwm_pin  = [39, 22, 20, 19]
    adc      = [-1,  1,  0, -1] # -1 indicates connected to both ADCs
    
    if transducer_number >= len(read_pin):
        raise Exception('Not that many transducers choose a numver between 0 and ', len(read_pin)-1)
    else:
        return read_pin[transducer_number], pwm_pin[transducer_number], adc[transducer_number]
        



def read_with_resolution(command, adc_resolution, com, repetitions, PWMdelays, time_per_sample, teensy_cpu_speed_hz):
    import numpy as np
    # Function takes in a command with PWM delay set at 0
    # Also takes in the adc resolution the com that the board is connected to and the number of repetitions and also the PWM delays to loop through in an array like [0,30,60]
    
    
    # To be able to delay in the nanoseconds range, a for loop that performs a no operation or nop is used. The for loop takes three cpu instructions and the nop takes one.
    # So in total a PWM delay of 1 will delay the start of the ADC by 4 cpu cycles. At 180MHz thats 22.222222222 repeating nano seconds. 
    # Therefore since one ADC sample takes 2000 nanoseconds for an integer division of this sample the pwm_delay must be a factor of (2000/22.22222) = 90
    # These factors are 1,2,3,5,6,9,10,15,18,30,45 and 90
    # So to delay 1/2 of a sample a pwm_delay of 45 is set
    # ---------------------------------------------------
    #   pwm_delay           Fraction of a sample
    #   90                  1
    #   45                  1/2
    #   30                  1/3
    #   18                  1/5        
    #   15                  1/6            
    #   10                  1/9            
    #   9                   1/10        
    #   6                   1/15            
    #   5                   1/18            
    #   3                   1/30        
    #   2                   1/45        
    #   1                   1/90
    # Thereore resolution increases are only able to be replicated out of 90 so asking for 4 times the resolution is 22.5/90 which is not possible so only fractions of 90 are possible
    
    # Setup output arrays
    output_adc0 = []
    output_adc1 = []
    times_x_axis = []
    
    # Take background readings
    background_voltage_0, background_voltage_1 = find_background_voltages(command, adc_resolution, com, repetitions)
    for resoultion in range(len(PWMdelays)):
        # Set the delay for every loop to get higher resoultions
        command["PWMdelay"] = PWMdelays[resoultion]
        
        # Read the voltages and then scale them around zero using the background voltages
        voltages_adc_0_not_scaled, voltages_adc_1_not_scaled = read_voltages_two_pins_fastest(command.copy(), adc_resolution, com, repetitions)
        voltages_adc_0, voltages_adc_1 = scale_around_zero(background_voltage_0, background_voltage_1, voltages_adc_0_not_scaled, voltages_adc_1_not_scaled, adc_resolution)
        
        # Calculate the times in microseconds that the samples are taken at for each of the resolutions
        times_microseconds = np.linspace(pwm_delay_to_microseconds(PWMdelays[resoultion], teensy_cpu_speed_hz), (len(voltages_adc_0)*time_per_sample+pwm_delay_to_microseconds(PWMdelays[resoultion], teensy_cpu_speed_hz)), num=len(voltages_adc_0), endpoint=True)
        
        # Append the outputs for each resolution to the final output variables
        output_adc0 = np.concatenate([output_adc0, voltages_adc_0])
        output_adc1 = np.concatenate([output_adc1, voltages_adc_1])
        times_x_axis = np.concatenate([times_x_axis,times_microseconds])
        
    # Sort the mesured voltages so that they are in time order and can be easily plotted
    times_x_axis_sorted, output_adc0_sorted, output_adc1_sorted = zip(*sorted(zip(times_x_axis, output_adc0, output_adc1)))
        
    return output_adc0_sorted, output_adc1_sorted, times_x_axis_sorted
        


def pwm_delay_to_microseconds(pwm_delay, teensy_cpu_speed_hz):
    
    miliseconds = pwm_delay * ((1/teensy_cpu_speed_hz)*4*10**6) # 4 for 4 cup cycles
    return miliseconds
    
    
def find_temperature():
    from Controller import Controller
    with Controller() as com:
        command =  {"CMD":5}
        reply = com.send_json(command)
        if reply["Status"] != "Success":
            raise Exception("Failed to start conversion", reply)
            
        else:
            return reply["Temperature"]
            
def find_samples_per_wave():
    from Controller import Controller
    with Controller() as com:
        command =  {"CMD":3}
        reply = com.send_json(command)
        if reply["Status"] != "Success":
            raise Exception("Failed to start conversion", reply)
            
        else:
            time_for_512_samples = reply["SampleDurationuS"] # microseconds
            time_per_sample = time_for_512_samples / 512 # microseconds
            
            samples_per_wave = 25/time_per_sample # 25 microseconds for a 40khz wave
            
            return samples_per_wave, time_per_sample
        
def find_speed_of_sound():
    temp = find_temperature()
    if temp < 10 or temp > 30:
        raise Exception("Temperature reading is either quite high or low are you sure this is correct? if so adjust this checking function", temp, "Degrees C")
    else:
        # Imperical equation for the velocity in m/s of sound in air with temp in degrees C
        velocity = 331.4 + 0.6*temp
        return velocity, temp



def distance_on_sphere(location, point):
    """
    Takes in a location in space [x, y, z] and a point in space [x, y, z] and returns the radius of the circle that is centered on the location and has the point on its surface
    """
    import math
    distance = math.sqrt( (location[0]-point[0])**2 + (location[1]-point[1])**2 + (location[2]-point[2])**2 )
    return distance



def mse(x, locations, distances_mesured): # x = point in 3D space [x, y, z]
    """
    See optimise_location for detailed description of input variables
    This is a Mean Square Error function that outputs a value dependant on the error of the distances mesured to the calcualted distances to the given point x 
    (zero error would mean point x is the valid location that would give the mesured distances)
    """
    import math
    mse = 0.0
    distances = []
    for i in range(len(locations)):
        distances.append(distance_on_sphere(locations[i], x))
        
    for errors in range(len(locations)):
        mse += math.pow(distances_mesured[errors] - distances[errors], 2.0)
    return mse / len(locations)



def optimise_location(guess, locations, distances_mesured):
    import scipy; import time
    """
    Provide an initial location guess as: guess = [0,0,0]
    Provide a list of known locations or beacons as they are commenly refered l1, l2 so on: locations = [[x, y, z], [x, y, z].....
    Provide a list of mesured distances from these beacons to the desired location in space: distances_mesured = [d1, d2, d3  ....these are the distances from desired point to location l1, l2 so on in order
    Uses an optimisation algorithm to find the location in space that minimises the Mean Square Error of the beacon distances to the outputed location
    This location will be the closest point in space to the distances given and is robust to not mathamatically possibe distances between points
    The error is also returned which tells you how much error there is in the given location (If the distances given have a valid mathamatical solution the error will be zero - perfect senario)
    """


    #t1 = time.time()
    result = scipy.optimize.minimize(
    	mse,                                   # The error function
    	guess,                                 # The initial guess
    	args=(locations, distances_mesured),   # Additional parameters for mse
    	method='L-BFGS-B',                     # The optimisation algorithm
    	options={
    		'ftol':1e-5,         # Tolerance
    		'maxiter': 1e+7      # Maximum iterations
    	})
    #t2 = time.time()
        
    location = result.x
    error = result.fun
    #print("")
    #print("Time = ", t2-t1)
    #print("Estimated location: ", location)
    #print("Mean Square Error of location: ", error)
    
    return location, error



def autoscale_axis_3d(points, ax):
    """
    Pass the list of points and the axis to scale and will autpmatically scale the axis so all points are visiable
    """
    
    xmin = 0
    ymin = 0
    zmin = 0
    xmax = 0
    ymax = 0
    zmax = 0
    
    for point in range(len(points)):
        if points[point][0]._verts3d[0][0] < xmin:
            xmin = points[point][0]._verts3d[0][0] - ( points[point][0]._verts3d[0][0] /2 )
        if points[point][0]._verts3d[0][0] > xmax:
            xmax = points[point][0]._verts3d[0][0] + ( points[point][0]._verts3d[0][0] /2 )
            
        if points[point][0]._verts3d[1][0] < ymin:
            ymin = points[point][0]._verts3d[1][0] - ( points[point][0]._verts3d[1][0] /2 )
        if points[point][0]._verts3d[1][0] > ymax:
            ymax = points[point][0]._verts3d[1][0] + ( points[point][0]._verts3d[1][0] /2 )    
    
        if points[point][0]._verts3d[2][0] < zmin:
            zmin = points[point][0]._verts3d[2][0] - ( points[point][0]._verts3d[2][0] /2 )
        if points[point][0]._verts3d[2][0] > zmax:
            zmax = points[point][0]._verts3d[2][0] + ( points[point][0]._verts3d[2][0] /2 )    
        
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_zlim([zmin, zmax])




def transducer_read_pin(transducer_number):
    # Takes in transducer number and outputs what pin that transducer reads on
    read_pins_list = [None, 37, 39, 16, 17, 19, 22]
    
    if transducer_number < 1 or transducer_number > (len(read_pins_list)-1):
        raise Exception("Pick a transdcuer that exists in the list")
    else:
        return read_pins_list[transducer_number]

def transducer_output_pins(transducer_number):
    # Takes in transducer number and outputs both the high and low PWM pins NEVER SET BOTH PINS TO HIGH OR IT WILL FRY THE BOARD

    pull_up_pins   = [None, 25, 12, 9, 6, 1, 3] # Pull up pin is the pin that when pulled high causes the transducer to be pulled high
    pull_down_pins = [None, 24, 11, 8, 5, 0, 2] # Pull down pin is the pin that when pulled high causes the transducer to be pulled low
    
    if transducer_number < 1 or transducer_number > (len(pull_up_pins)):
        raise Exception("Pick a transdcuer that exists in the list")
    else:
        return [pull_up_pins[transducer_number], pull_down_pins[transducer_number]]

def adc_that_read_pin_on(transducer_number):
    # Takes in transducer number and outputs what ADC that transducer should use to read
    adc_list = [None, 1,1,1,1,0,0]
    
    if transducer_number < 1 or transducer_number > (len(adc_list)):
        raise Exception("Pick a transdcuer that exists in the list")
    else:
        return adc_list[transducer_number]

def create_read_command(read_transdcuer, ping_transdcuer, PWMwidth, repetitions):
    
    read_pin = transducer_read_pin(read_transdcuer)    
    read_adc = adc_that_read_pin_on(read_transdcuer)
    
    PWM_pin, PWM_pin_low = transducer_output_pins(ping_transdcuer)
    
    if read_adc == 0:
        command = {"CMD":2, "ADC0Channels":[read_pin,read_pin,read_pin,read_pin], "ADC1Channels":[38,38,38,38], "PWM_pin":PWM_pin, "PWM_pin_low":PWM_pin_low, "PWMwidth":PWMwidth, "repetitions":repetitions, "PWMdelay":0}
    else:
        command = {"CMD":2, "ADC0Channels":[14,14,14,14], "ADC1Channels":[read_pin,read_pin,read_pin,read_pin], "PWM_pin":PWM_pin, "PWM_pin_low":PWM_pin_low, "PWMwidth":PWMwidth, "repetitions":repetitions, "PWMdelay":0}

    return command, read_adc


def create_board_command_offset(board, transducer_number, offset, enable = True):
    # Board = 1 or 2 for which board you want to connect to
    # Transducer number from 0 to 87 for the transducer on that board you want to connect to
    # Offset which is the offset in radiens 0 to 2pi for how phase shifted the sound signal will be can be any number as it just wraps around so pi = 3pi and so on this number is discretised by the teensy
    # Enable is if the transducer is off or not. setting this to falce with a valid transducer and board number will turn that speaker off
    command = {"CMD":7, "board":board, "transducer_number":transducer_number, "offset":offset, "enable":enable}
    return command

def create_board_command_off(board, transducer_number, enable = False):
    command = {"CMD":7, "board":board, "transducer_number":transducer_number, "enable":enable}
    return command

def create_board_command_power(board, power):
    # Power is a number between 1 and 256: #Not a mistake! the DAC goes from 0-256, not 255! which controlls the boards overall modulation 128 would be a 50% duty
    command = {"CMD":7, "board":board, "power":power}
    return command

def create_board_command_divisor(board, divisor):
    # Divisor is a divisior of the power allowing for other frequencys to be modulated on the board no number lower than 50 and none greater than 524,287 is allowed
    command = {"CMD":7, "board":board, "divisor":divisor}
    return command

def create_board_command_freq(board, freq):
    # Frequency uses the divisor to modulate the board at the typed frequency in HZ 
    command = {"CMD":7, "board":board, "freq":freq}
    return command

def create_board_command_load_offsets(board):
    # Frequency uses the divisor to modulate the board at the typed frequency in HZ 
    command = {"CMD":7, "board":board, "load_offsets":True}
    return command

def create_board_command_wav(board, sample_rate, size):
    # Frequency uses the divisor to modulate the board at the typed frequency in HZ 
    command = {"CMD":8, "board":board,"size":size, "sample_rate":sample_rate}
    return command


def can_hear_transducer(listen_transducer, array_board, output_transducer):
    
    """
    Listen_transducer is the transducer number of the locating transducer you want to listen on
    Array board 1 or 2 for now
    Output transducer from 1 to 88 on the array board
    """

    




def turn_on_board_transducer(board, output_transducer):
    from connect import Controller 
    ## Need to edit the controler so it can switch to what board you want to connect to depending on an input, probably needs just hardcoded initially
    ## or manual pulling out the usb of the board you dont want to connect to
    with Controller() as ctl:        
        
        # Turn all transducers off
        for i in range(ctl.outputs):
            ctl.disableOutput(i)
        # Turn the power up
        ctl.setOutputDACPower(256)
        ctl.setOutputDACDivisor(100)
        
        # Turn on the one transducer with no phase offset
        ctl.setOffset(output_transducer, 0)
        ctl.loadOffsets()



def midi_to_hz(midi_number):
    return (27.5 * 2**((midi_number - 21)/12))












































