import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import time
import re
import numpy as np

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
        
    def send_start(self):
        self.com.write(b'd')
        print("Sent start command")
    
    def send_background_check_left(self): ## Print back with p
        self.com.write(b'b')
        print("Sent background check left")
    
    def send_background_check_right(self): ## Print back with p
        self.com.write(b'n')
        print("Sent background check right")
    
    def send_print(self):
        self.com.write(b'p')
        print("Sent print")
        
    def send_print_1(self):
        self.com.write(b'o')
        print("Sent print command one")
        
    def send_print_2(self):
        self.com.write(b'i')
        print("Sent print command two")
        
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


fig = plt.figure()
ax1 = fig.add_subplot(3,1,1)
ax2 = fig.add_subplot(3,1,2)
ax3 = fig.add_subplot(3,1,3)
fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.5)

adc_resolution = 10
number_of_samples = 512
number_of_pages = 1



def background_voltage_func():
    with Controller() as ctr:
        ctr.send_background_check_left()
        background_voltages_left = []
        for pages in range(number_of_pages):
            ctr.send_print()
            list_of_serial_reads = ctr.read()
            if len(list_of_serial_reads) == 0:
                print("Error no data read in background voltage check")
            else:
                for i in range(len(list_of_serial_reads)):
                    int_value = int(list_of_serial_reads[i])
                    background_voltages_left.append((int_value*3.3)/(2**adc_resolution))
                
        ctr.send_background_check_right()
        background_voltages_right = []
        for pages in range(number_of_pages):
            ctr.send_print()
            list_of_serial_reads = ctr.read()
            if len(list_of_serial_reads) == 0:
                print("Error no data read in background voltage check")
            else:
                for i in range(len(list_of_serial_reads)):
                    int_value = int(list_of_serial_reads[i])
                    background_voltages_right.append((int_value*3.3)/(2**adc_resolution))
                
    return background_voltages_left, background_voltages_right

backgrounds = background_voltage_func() 
background_voltage_left   = np.average(backgrounds[0])
background_voltage_right =  np.average(backgrounds[1])

## For plotting the background voltages
"""
ax1.clear(); ax2.clear()
sample_number_background = np.linspace(0,number_of_samples, num=number_of_samples, dtype=int)
ax1.plot(sample_number_background, backgrounds[1], linewidth=0.5)
ax2.plot(sample_number_background, backgrounds[0], linewidth=0.5)
"""

def read_and_calculate_values():
    with Controller() as ctr:
        ctr.send_start()
        voltages_1 = []
        for pages in range(number_of_pages):
            ctr.send_print_1()
            list_of_serial_reads = ctr.read()
            if len(list_of_serial_reads) == 0:
                print("Error no data read in read_and_calculate_values")
            else:
                for i in range(len(list_of_serial_reads)):
                    int_value = int(list_of_serial_reads[i])
                    voltages_1.append((int_value*3.3)/(2**adc_resolution))
                
        voltages_2 = []
        for pages in range(number_of_pages):
            ctr.send_print_2()
            list_of_serial_reads = ctr.read()
            if len(list_of_serial_reads) == 0:
                print("Error no data read in read_and_calculate_values")
            else:
                for i in range(len(list_of_serial_reads)):
                    int_value = int(list_of_serial_reads[i])
                    voltages_2.append((int_value*3.3)/(2**adc_resolution))
            
            
    return voltages_1, voltages_2


def multiple_samples(samples):
    distances = np.zeros(samples)
    for sample_number in range(samples):
        values =  read_and_calculate_values()
        temp_voltages_1 = values[0]

        background_deviation = 0.0055

        larger_deavation_than = background_deviation * 1.5
        heard_it_yet = False
        sample_number_of_echo = 0
        
        for i in range(15,len(temp_voltages_1)):
            deaviation_sample = []
            for sample in range(15):
                deaviation_sample.append(np.abs(1.65 - temp_voltages_1[i-sample]))
            average_deavation_temp = np.sum(deaviation_sample)/len(deaviation_sample)
            if average_deavation_temp > larger_deavation_than and heard_it_yet == False:
                print("I hear it! Sample: ",i)
                sample_number_of_echo = i
                heard_it_yet = True
            
        
        if sample_number_of_echo != 0:
            time_to_first_echo = (sample_number_of_echo - 15 )/335000
            distance_to_transducer_and_back_in_m = 343 * time_to_first_echo
            distances[sample_number] = (distance_to_transducer_and_back_in_m/2)*100 # in cm
            print("Distance: ",distances[sample_number]," cm")
            
    distance = np.average(distances)
    return distance, distances


def animate(i):
    t1 = time.time()
    values =  read_and_calculate_values()

    voltages_1 = np.subtract(values[0], background_voltage_right)
    voltages_2 = np.subtract(values[1], background_voltage_left)
    
    target_wave = []
    for i in range(int(0.1*number_of_samples)):
        target_wave.append(voltages_2[i])
    sample_number_of_echo = 0
    
    
    #Now correlate the signal and target wave
    correlation = []
    for i in range(len(voltages_1) - len(target_wave)):
       csum = 0
       for j in range(len(target_wave)):
           csum += voltages_1[i + j] * target_wave[j]
       correlation.append(csum)

    #Find the highest correlation
    sample_number_of_echo = np.argmax(correlation)
    
            
    if sample_number_of_echo != 0:
        time_to_first_echo = (sample_number_of_echo)/335000
        distance_to_transducer_and_back_in_m = 343 * time_to_first_echo
        distance = (distance_to_transducer_and_back_in_m/2)*100 # in cm
        distance_str = str("%.2f" % distance)
    else:
        distance_str = "Cant hear anything"

    ## Aligning the voltages with the background
        
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
    ax3.plot(correlation, linewidth=0.5)
    ax2.set_ylim([-2,2])
    ax3.set_title('Correlation Signal')
    ax3.set_xlabel('Sample Number')
    ax3.set_ylabel('Voltage (V)')
    t2 = time.time()
    print("Time = ",t2-t1)

ani = animation.FuncAnimation(fig, animate,  interval = 250)
plt.show

