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
        import os

        if len(self.ports) == 0:
            if os.name == "nt":
                self.ports = ["COM"+str(i) for i in range(1, 10)]
                
            else:
                self.ports = ["/dev/ttyUSB"+str(i) for i in range(0, 10)]

        self.outputs = 0
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
            
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        #for i in range(self.outputs):
        #    self.disableOutput(i)
        self.com.close()       
        
    def reset_buffer(self):
        self.com.reset_input_buffer()
        self.com.flushInput()
        
    def send_start(self):
        self.com.write(b'd')
        print("Sent start command")
        
    def send_print_1(self):
        self.com.write(b'o')
        print("Sent print command one")
        
    def send_print_2(self):
        self.com.write(b'i')
        print("Sent print command two")
        
    def read_1(self):
        list_of_serial_reads = []
        while len(list_of_serial_reads) < 1025:
            serial_output = str(self.com.readline().decode(encoding='UTF-8'))
            if len(serial_output) > 0:
                list_of_serial_reads.append(serial_output)
        print(self.com.in_waiting)
        return list_of_serial_reads

    def read_2(self):
        list_of_serial_reads_2 = []
        while len(list_of_serial_reads_2) < 1025:
            serial_output = str(self.com.readline().decode(encoding='UTF-8'))
            if len(serial_output) > 0:
                list_of_serial_reads_2.append(serial_output)
        print(self.com.in_waiting)
        return list_of_serial_reads_2



def getWords(text):
    return re.compile('\w+').findall(text)



def read_and_calculate_values():
    with Controller() as ctr:
        ctr.send_start()
        time.sleep(0.1)
        voltages_1 = []
        ctr.reset_buffer()
        for pages in range(number_of_pages):
            ctr.reset_buffer()
            ctr.send_print_1()
            list_of_serial_reads = ctr.read_1()
            time.sleep(0.1)
            for i in range(1,(int(number_of_samples/number_of_pages))+1):
                int_value = int(getWords(list_of_serial_reads[i])[0])
                voltages_1.append((int_value*3.3)/(4096))
        
        voltages_2 = []
        ctr.reset_buffer()
        time.sleep(0.1)
        for pages in range(number_of_pages):
            ctr.reset_buffer()
            ctr.send_print_2()
            list_of_serial_reads_2 = []
            list_of_serial_reads_2 = ctr.read_2()
            time.sleep(0.1)
            for i in range(1,(int(number_of_samples/number_of_pages))+1):
                int_value = int(getWords(list_of_serial_reads_2[i])[0])
                voltages_2.append((int_value*3.3)/(4096))
            
    return voltages_1, voltages_2

fig = plt.figure()
ax1 = fig.add_subplot(2,1,1)
ax2 = fig.add_subplot(2,1,2)
number_of_samples = 1000
number_of_pages = int(number_of_samples/1000)
list_of_serial_reads = []
list_of_serial_reads_2 = []


def animate(i):
    values =  read_and_calculate_values()
    voltages_1 = values[0]
    voltages_2 = values[1]
    sample_number = np.linspace(0,number_of_samples, num=number_of_samples, dtype=int)
    ax1.clear()
    ax2.clear()
    ax1.plot(sample_number, voltages_1, linewidth=0.5)
    ax2.plot(sample_number, voltages_2, linewidth=0.5)
    #ax1.xlabel('Sample Number')
    #ax1.ylabel('Voltage (V)')
    #ax1.ylim([0,3.5])
    
    
ani = animation.FuncAnimation(fig, animate,  interval = 1000)
plt.show




"""
initial_deviation_magnitude = []
for i in range(20):
    deavation = np.abs(1.65 - voltages[i])
    initial_deviation_magnitude.append(deavation)
average_deavation = np.sum(initial_deviation_magnitude)/len(initial_deviation_magnitude)



larger_deavation_than = average_deavation * 3
heard_it_yet = False
sample_number_of_echo = 0

for i in range(15,len(voltages)):
    deaviation_sample = []
    for sample in range(15):
        deaviation_sample.append(np.abs(1.65 - voltages[i-sample]))
    average_deavation_temp = np.sum(deaviation_sample)/len(deaviation_sample)
    if average_deavation_temp > larger_deavation_than and heard_it_yet == False:
        print("I hear it! Sample: ",i)
        sample_number_of_echo = i
        heard_it_yet = True
    

if sample_number_of_echo != 0:
    time_to_first_echo = (sample_number_of_echo - 15 )/335000
    distance = 343 * time_to_first_echo
    print("Distance: ",(distance/2)*100," cm")


"""