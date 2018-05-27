## Functions used in the main acoustic tracker program


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



def target_wave(): ## Currently unused
    """ Funciton that returns the saved target wave for the correlation funciton to use. This is a 99 sample set of the recieved acoustic signal.
    """

    target = [-62.43359375, -40.43359375, -7.43359375, 34.56640625, 60.56640625, 80.56640625, 71.56640625, 44.56640625, 4.56640625, -38.43359375,
-70.43359375, -85.43359375, -78.43359375, -52.43359375, -9.43359375, 37.56640625, 77.56640625, 98.56640625, 92.56640625, 63.56640625,
13.56640625, -39.43359375, -80.43359375, -101.4335938, -94.43359375, -64.43359375, -15.43359375, 39.56640625, 80.56640625, 103.5664063,
95.56640625, 65.56640625, 16.56640625, -37.43359375, -81.43359375, -105.4335938, -98.43359375, -70.43359375, -22.43359375, 32.56640625,
79.56640625, 103.5664063, 101.5664063, 72.56640625, 22.56640625, -33.43359375, -77.43359375, -103.4335938, -100.4335938, -71.43359375,
-24.43359375, 29.56640625, 75.56640625, 99.56640625, 97.56640625, 70.56640625, 19.56640625, -29.43359375, -72.43359375, -96.43359375,
-93.43359375, -65.43359375, -20.43359375, 30.56640625,70.56640625, 89.56640625, 86.56640625, 58.56640625, 16.56640625, -28.43359375,
-66.43359375, -88.43359375, -84.43359375, -57.43359375, -16.43359375, 29.56640625, 65.56640625, 81.56640625, 77.56640625, 51.56640625,
12.56640625, -27.43359375, -63.43359375, -79.43359375, -74.43359375, -50.43359375, -14.43359375, 26.56640625, 57.56640625, 72.56640625,
66.56640625, 41.56640625, 2.56640625, -33.43359375, -59.43359375, -72.43359375, -65.43359375, -39.43359375, -4.43359375]
    return target

                
                                 
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
        


def read_voltages_two_pins_fastest(command, adc_resolution, com):
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
    
    reply = com.send_json({"CMD":1}) # command 1 askes the board to dump the buffer out on the serial line
    if reply["Status"] != "Success":
        raise Exception("Failed to download data", reply)

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
        
        
    return adc_0_output, adc_1_output



def find_background_voltages(command, adc_resolution, com):
    """
    Funciton to run first so that the background pin voltage can be found and used to scale the output around zero vols
    """
    import numpy as np
    command_no_pwm = command.copy()
    command_no_pwm["PWM_pin"] = -1
    voltages_0, voltages_1 = read_voltages_two_pins_fastest(command_no_pwm, adc_resolution, com)
    
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



def average_waves(averages, adc_resolution, command, com): 
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
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        