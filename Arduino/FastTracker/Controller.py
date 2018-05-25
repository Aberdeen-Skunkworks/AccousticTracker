#!/usr/bin/python3
import matplotlib.pyplot as plt
import numpy as np
import json
import serial

class Controller():
    def __init__(self):
        pass

    def send_json(self, out_json):
        """Send a JSON command on the serial port, and get the JSON
        reply. This function always returns a dict with a Status key,
        even if there's an error parsing the reply. It guarantees that
        the Status from the reply is set too.
        """
        self.reset_buffer()
        self.com.write(json.dumps(out_json).encode())
        reply = self.com.readline()
        while reply == b"":
            reply = self.com.readline()
            
        try:
            json_reply = json.loads(reply)
            if "Status" not in json_reply:
                return json.loads({"Status":"Fail", "Error":"No status in the returned JSON", "Reply":json_reply})
            return json_reply
        except:
            return {"Status":"Fail", "Error":"Could not parse reply string", "Reply":reply}
        
    def __enter__(self):
        for port in self.serial_ports():
            print("Trying port " + str(port)+" ", end="")
            self.com = serial.Serial(port=port, baudrate=115200, timeout=0.01)
            reply = self.send_json({"CMD":0})
            if reply["Status"] != "Success":
                print("Failed! " + repr(reply))
                continue
            print("Success! Arduino compiled at",reply["CompileTime"])
            break
        if (self.com == None):
            raise Exception("Failed to open communications!")
        return self

    def reset_buffer(self):
        self.com.reset_input_buffer()
        self.com.flushInput()
    
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

    def __exit__(self, exc_type, exc_value, traceback):
        self.com.close()   
        


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
    
    # Show the correlator function and both waves on the same plot
    if plot:
        import matplotlib.pyplot as plt
        plt.plot(correlation_signal, linewidth=0.5)
        plt.plot(signal, linewidth=0.5)
        plt.plot(target_wave, linewidth=0.5)
        plt.show()

    #Find the highest correlation index
    maxindex = np.argmax(correlation_signal)
    
    return maxindex, correlation_signal

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
        data = np.subtract(data,2048)
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
        distance_between_transducers = (343 * time_to_first_echo * 100) -5.86  # in cm
        print("Sample Number = ", sample_number_of_echo)
        print("Distance = ", "%.2f" % distance_between_transducers, " cm")

        
        ax.relim()
        ax.autoscale_view(True,True,True)
        plt.gcf().canvas.draw()
        plt.pause(0.01)
        