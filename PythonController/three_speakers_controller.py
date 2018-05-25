import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import time
import re
import numpy as np
import math

style.use('fivethirtyeight')

class Controller():
    def __init__(self, ports = []):
        self.ports = ports
        pass
    
       
    def __enter__(self):
        import serial
        
        self.ports = self.serial_ports()
        
        for port in self.ports:
            try:
                self.com = serial.Serial(port=port, baudrate=500000, timeout=0.01)
                self.com.reset_input_buffer()

                print("Connected successfully to board on port " + str(port))
                break
            except Exception as e:
                print(e)
                self.com = None
        if (self.com == None):
            raise Exception("Failed to open communications!")
        self.led_toggle()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        #for i in range(self.outputs):
        #    self.disableOutput(i)
        self.led_toggle()
        self.com.close()       
        
    def serial_ports(self):
        import sys
        import glob
        import serial
        """ Lists serial port names
    
            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
    
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def led_toggle(self):
        self.com.write(b'l')

    def reset_buffer(self):
        self.com.reset_input_buffer()
        self.com.flushInput()
        
    def send_start(self, run_number):    
        if run_number == 1:
            self.com.write(b'd')
            print("Sent start command 1")
        elif run_number == 2:
            self.com.write(b'f')
            print("Sent start command 2")
        elif run_number == 3:
            self.com.write(b'g')
            print("Sent start command 3")        
        elif run_number == 4:
            self.com.write(b'h')
            print("Sent start command 4") 
        elif run_number == 5:
            self.com.write(b'j')
            print("Sent start command 5") 
        elif run_number == 6:
            self.com.write(b'k')
            print("Sent start command 6")         



    def send_background_check_1(self): ## Print back with p
        self.com.write(b'b')
        print("Sent background check 1")
    
    def send_background_check_2(self): ## Print back with p
        self.com.write(b'n')
        print("Sent background check 2")

    def send_background_check_3(self): ## Print back with p
        self.com.write(b'm')
        print("Sent background check 3")



    def send_print(self):
        self.com.write(b'p')
        print("Sent print")

    def send_print_speaker_1(self):
        self.com.write(b'o')
        print("Sent print command for speaker_1")
        
    def send_print_speaker_2(self):
        self.com.write(b'i')
        print("Sent print command for speaker_2")
        
    def send_print_speaker_3(self):
        self.com.write(b'u')
        print("Sent print command for speaker_3")
        
        
        
    def read(self):
        list_of_serial_reads = []
        read = True
        store_values = False
        while read == True:
            serial_output = str(self.com.readline().decode(encoding='UTF-8'))
            if len(serial_output) > 0:
                word = getWords(serial_output)[0]
                if word == "finished":
                    read = False
                if store_values == True and read == True:
                    list_of_serial_reads.append(serial_output)
                if word == "printing":
                    store_values = True
                    
        print("Bytes in buffer, for debugging: ",self.com.in_waiting)
        return list_of_serial_reads



def getWords(text):
    return re.compile('\w+').findall(text)


adc_resolution = 10
number_of_samples = 512
number_of_pages = 1


def background_voltage_func():
    with Controller() as ctr:
        ctr.send_background_check_1()
        background_voltages_1 = []
        for pages in range(number_of_pages):
            ctr.send_print()
            list_of_serial_reads = ctr.read()
            if len(list_of_serial_reads) == 0:
                print("Error no data read in background voltage check")
            else:
                for i in range(len(list_of_serial_reads)):
                    int_value = int(list_of_serial_reads[i])
                    background_voltages_1.append((int_value*3.3)/(2**adc_resolution))
                
        ctr.send_background_check_2()
        background_voltages_2 = []
        for pages in range(number_of_pages):
            ctr.send_print()
            list_of_serial_reads = ctr.read()
            if len(list_of_serial_reads) == 0:
                print("Error no data read in background voltage check")
            else:
                for i in range(len(list_of_serial_reads)):
                    int_value = int(list_of_serial_reads[i])
                    background_voltages_2.append((int_value*3.3)/(2**adc_resolution))
                    
        ctr.send_background_check_3()
        background_voltages_3 = []
        for pages in range(number_of_pages):
            ctr.send_print()
            list_of_serial_reads = ctr.read()
            if len(list_of_serial_reads) == 0:
                print("Error no data read in background voltage check")
            else:
                for i in range(len(list_of_serial_reads)):
                    int_value = int(list_of_serial_reads[i])
                    background_voltages_3.append((int_value*3.3)/(2**adc_resolution))
                
    return background_voltages_1, background_voltages_2, background_voltages_3

backgrounds = background_voltage_func() 
background_voltage_1   =  np.average(backgrounds[0])
background_voltage_2   =  np.average(backgrounds[1])
background_voltage_3   =  np.average(backgrounds[2])



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