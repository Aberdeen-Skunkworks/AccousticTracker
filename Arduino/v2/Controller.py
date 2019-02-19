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
        command format example: {"CMD":2, "ADC0Channels":[23,23,23,23], "ADC1Channels":[38,38,38,38], "PWM_pin":23, "PWMwidth":8}
        """
        
        self.reset_buffer()
        self.com.write(json.dumps(out_json).encode())
        reply = self.com.readline()
        while reply == b"":
            reply = self.com.readline()
        try:
            json_reply = json.loads(reply.decode("utf-8"))
            if "Status" not in json_reply:
                return json.loads({"Status":"Fail", "Error":"No status in the returned JSON", "Reply":json_reply})
            return json_reply
        except Exception as e:
            return {"Status":"Fail", "Error":"Could not parse reply string", "Reply":reply, "exception":str(e)}
        
    def __enter__(self):
        self.com = None
        for port in self.serial_ports():
            print("Trying port " + str(port)+" ", end="")
            self.com = serial.Serial(port=port, baudrate=500000000, timeout=0.01)
            reply = self.send_json({"CMD":0})
            if reply["Status"] != "Success":
                print("Failed! " + repr(reply))
                self.com = None
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
            ports= glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
            print("darwin", ports)
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
