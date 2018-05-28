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



def target_wave(): 
    """ Funciton that returns the saved target wave for the correlation funciton to use. This is a 200 sample set of a recieved acoustic signal.
    Code below used to print out the saved wave
    counter = 0
    for i in range(20):
        print(saved_moved[counter], ",", saved_moved[counter+1], ",", saved_moved[counter+2], ",",saved_moved[counter+3], ",",saved_moved[counter+4], ",",saved_moved[counter+5], ",",saved_moved[counter+6], ",",saved_moved[counter+7], ",",saved_moved[counter+8], ",",saved_moved[counter+9], ",",)
        counter = counter + 10
    """
    target_sent = [0.00322265625 , -1.3672119140624999 , -1.3623779296874998 , -1.361572265625 , -1.3623779296874998 , -1.3478759765625 , -1.3390136718749999 , -1.3398193359375 , 1.6524169921874998 , 1.6524169921874998 ,
1.6524169921874998 , 1.6524169921874998 , 1.6524169921874998 , -0.1039306640625 , -1.38896484375 , -1.3664062499999998 , -1.348681640625 , -1.3607666015625 , -1.3664062499999998 , -0.87333984375 ,
1.6524169921874998 , 1.6524169921874998 , 1.6524169921874998 , 1.6524169921874998 , 1.6524169921874998 , -0.6678955078125 , -1.4115234374999999 , -1.3873535156249999 , -1.3502929687499998 , -1.3599609375 ,
-1.3825195312499998 , 1.0497802734375 , 1.6524169921874998 , 1.6524169921874998 , 1.6524169921874998 , 1.6524169921874998 , 1.6524169921874998 , -0.95068359375 , -1.4236083984374999 , -1.409912109375 ,
-1.3623779296874998 , -1.361572265625 , -1.3921875 , 1.4961181640624999 , 1.6524169921874998 , 0.359326171875 , -1.036083984375 , -1.2366943359375 , -0.7033447265624999 , -0.4632568359375]

    target_recieved = [0.000801635742187 , 0.00321862792969 , 0.00482995605469 , 0.00160729980469 , -0.00242102050781 , -0.00403234863281 , -0.00161535644531 , 0.00160729980469 , 0.000801635742187 , -4.0283203125e-06 ,
0.000801635742187 , 0.00241296386719 , 0.00482995605469 , 0.00482995605469 , 0.00160729980469 , -0.00161535644531 , -0.00161535644531 , 0.000801635742187 , -0.000809692382812 , -0.00242102050781 ,
-0.00322668457031 , -0.00161535644531 , 0.00241296386719 , 0.00563562011719 , 0.00724694824219 , 0.00402429199219 , 0.00402429199219 , 0.00321862792969 , 0.00160729980469 , -0.00322668457031 ,
-0.00806066894531 , -0.00806066894531 , -0.00564367675781 , -0.000809692382812 , 0.00402429199219 , 0.00644128417969 , 0.00966394042969 , 0.0112752685547 , 0.0104696044922 , 0.00644128417969 ,
-0.000809692382812 , -0.00886633300781 , -0.0128946533203 , -0.0145059814453 , -0.0128946533203 , -0.00806066894531 , 0.000801635742187 , 0.00966394042969 , 0.0177205810547 , 0.0209432373047 ,
0.0177205810547 , 0.00885827636719 , -0.00242102050781 , -0.0137003173828 , -0.0225626220703 , -0.0257852783203 , -0.0225626220703 , -0.0120889892578 , 0.00241296386719 , 0.0169149169922 ,
0.0281942138672 , 0.0322225341797 , 0.0281942138672 , 0.0161092529297 , -4.0283203125e-06 , -0.0177286376953 , -0.0322305908203 , -0.0370645751953 , -0.0322305908203 , -0.0177286376953 ,
0.00160729980469 , 0.0209432373047 , 0.0346395263672 , 0.0402791748047 , 0.0338338623047 , 0.0193319091797 , -4.0283203125e-06 , -0.0209512939453 , -0.0370645751953 , -0.0435098876953 ,
-0.0402872314453 , -0.0249796142578 , -0.00322668457031 , 0.0201375732422 , 0.0386678466797 , 0.0459188232422 , 0.0378621826172 , 0.0217489013672 , 0.000801635742187 , -0.0217569580078 ,
-0.0394815673828 , -0.0483438720703 , -0.0451212158203 , -0.0290079345703 , -0.00483801269531 , 0.0201375732422 , 0.0386678466797 , 0.0467244873047 , 0.0394735107422 , 0.0241658935547 ,
0.00241296386719 , -0.0201456298828 , -0.0386759033203 , -0.0491495361328 , -0.0467325439453 , -0.0322305908203 , -0.00806066894531 , 0.0177205810547 , 0.0378621826172 , 0.0459188232422 ,
0.0410848388672 , 0.0241658935547 , 0.00160729980469 , -0.0193399658203 , -0.0362589111328 , -0.0451212158203 , -0.0410928955078 , -0.0282022705078 , -0.00725500488281 , 0.0153035888672 ,
0.0338338623047 , 0.0426961669922 , 0.0370565185547 , 0.0225545654297 , 0.00241296386719 , -0.0177286376953 , -0.0338419189453 , -0.0410928955078 , -0.0370645751953 , -0.0233682861328 ,
-0.00403234863281 , 0.0169149169922 , 0.0330281982422 , 0.0386678466797 , 0.0322225341797 , 0.0185262451172 , 0.000801635742187 , -0.0185343017578 , -0.0330362548828 , -0.0378702392578 ,
-0.0322305908203 , -0.0177286376953 , 0.000801635742187 , 0.0193319091797 , 0.0330281982422 , 0.0362508544922 , 0.0314168701172 , 0.0177205810547 , -4.0283203125e-06 , -0.0185343017578 ,
-0.0322305908203 , -0.0354532470703 , -0.0298135986328 , -0.0153116455078 , 0.00241296386719 , 0.0193319091797 , 0.0298055419922 , 0.0338338623047 , 0.0265828857422 , 0.0136922607422 ,
-0.00242102050781 , -0.0185343017578 , -0.0290079345703 , -0.0322305908203 , -0.0241739501953 , -0.0112833251953 , 0.00482995605469 , 0.0209432373047 , 0.0298055419922 , 0.0322225341797 ,
0.0257772216797 , 0.0128865966797 , -0.00242102050781 , -0.0177286376953 , -0.0257852783203 , -0.0265909423828 , -0.0193399658203 , -0.00725500488281 , 0.00805261230469 , 0.0209432373047 ,
0.0289998779297 , 0.0281942138672 , 0.0209432373047 , 0.00885827636719 , -0.00483801269531 , -0.0169229736328 , -0.0241739501953 , -0.0241739501953 , -0.0169229736328 , -0.00564367675781 ,
0.00805261230469 , 0.0193319091797 , 0.0273885498047 , 0.0273885498047 , 0.0193319091797 , 0.00805261230469 , -0.00403234863281 , -0.0153116455078 , -0.0217569580078 , -0.0217569580078]
    
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
        
    
        
    return np.divide(adc_0_output, repetitions), np.divide(adc_1_output, repetitions)



def find_background_voltages(command, adc_resolution, com, repetitions):
    """
    Funciton to run first so that the background pin voltage can be found and used to scale the output around zero vols
    """
    import numpy as np
    command_no_pwm = command.copy()
    command_no_pwm["PWM_pin"] = -1
    voltages_0, voltages_1 = read_voltages_two_pins_fastest(command_no_pwm, adc_resolution, com, repetitions)
    
    # Divide out the repetitions     
    print(voltages_0)
    voltages_0 = np.divide(voltages_0, repetitions)
    print(voltages_1)
    voltages_1 =  np.divide(voltages_1, repetitions)
    
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



def average_waves(averages, adc_resolution, command, com): # Redundant
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
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        