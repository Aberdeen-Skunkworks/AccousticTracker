## Functions used in the main acoustic tracker program

def square_wave_gen(number_half_waves, resolution):
    """
    Takes in number of half waves and resolution in multiples of 12 samples per wave 1 = 12 samples per wave 2 = 24 so on 
    Output square wave oscillating at 40,000 Hz with the x axis in microseconds and centered around zero    
    """
    from scipy import signal
    import matplotlib.pyplot as plt
    import numpy as np
    

    # One wave is 25 microseconds
    t = np.linspace(0, 12.5*number_half_waves, 12*resolution*(number_half_waves/2), endpoint=False)
    wave = -signal.square(2 * np.pi * 0.04 * t)*1.65

    
    return t, wave
"""
import matplotlib.pyplot as plt
number_half_waves = 10
resolution = 10
    
t, wave = square_wave_gen(number_half_waves, resolution)
plt.plot(t, wave, 'x-')
plt.ylim(-2, 2)    
 """      



def correlation(signal, target_wave, plot = False):
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
        None , None , None , None , 5 , 14 , 8 , 9 , 13 , 2 , 6 , 7 , 15 , 4 , None , 
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
        



def read_with_resolution(command, adc_resolution, com, repetitions, PWMdelays):
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
        times_microseconds = np.linspace(pwm_delay_to_microseconds(PWMdelays[resoultion]), (len(voltages_adc_0)*2+pwm_delay_to_microseconds(PWMdelays[resoultion])), num=len(voltages_adc_0), endpoint=True)
        
        # Append the outputs for each resolution to the final output variables
        output_adc0 = np.concatenate([output_adc0, voltages_adc_0])
        output_adc1 = np.concatenate([output_adc1, voltages_adc_1])
        times_x_axis = np.concatenate([times_x_axis,times_microseconds])
        
    # Sort the mesured voltages so that they are in time order and can be easily plotted
    times_x_axis_sorted, output_adc0_sorted, output_adc1_sorted = zip(*sorted(zip(times_x_axis, output_adc0, output_adc1)))
        
    return output_adc0_sorted, output_adc1_sorted, times_x_axis_sorted
        


def pwm_delay_to_microseconds(pwm_delay):
    miliseconds = pwm_delay * 0.0222222222222222222222222
    return miliseconds
    
    


        
        
        
        
        
