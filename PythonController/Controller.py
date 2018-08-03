#!/usr/bin/python3
import matplotlib.pyplot as plt
import numpy as np
import json
import serial
from Functions import digital_pin_to_sc1a

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
        # Convert the digital pin numbers given from the user to sc1a pin numbers used by the ADC's to send to the teensy board
        if out_json["CMD"] == 2:
            ADC_0_sc1a_pins = []
            ADC_1_sc1a_pins = []
            for i in range(4):
                ADC_0_digital_pins = out_json["ADC0Channels"]
                ADC_1_digital_pins = out_json["ADC1Channels"]
                ADC_0_sc1a_pins.append(digital_pin_to_sc1a( 0, ADC_0_digital_pins[i]) )
                ADC_1_sc1a_pins.append(digital_pin_to_sc1a( 1, ADC_1_digital_pins[i]) )
            out_json["ADC0Channels"] = ADC_0_sc1a_pins
            out_json["ADC1Channels"] = ADC_1_sc1a_pins
        
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


    def getOneWordReply(self, cmd, board):
        self.sendCmd(cmd, board)
        ack = bytearray(self.com.read(1))
        if (len(ack) != 1):
            raise Exception("Failed to read one word")
        return ack[0]

    def getOutputs(self):
        return self.getOneWordReply(bytearray([0b11000000,0,0]))

    def getVersion(self):
        return self.getOneWordReply(bytearray([0b11101000,0,0]))
    
    def sendCmd(self, bytestream, board):
        #Serial communication is carried out using 8 bit/byte
        #chunks. To be able to communicate all the data we need, we
        #use commands composed of 3 bytes. We use the highest bit of
        #each byte to denote if it is the first byte in a command.
        #The remaining bytes must not have the uppermost bit set (to
        #prevent errors in communication causing the controller to
        #assume they are the start of a command), thus only 21bits of
        #information are available for each command.

        # #The structure of a command
        #   23  22  21  20  19  18  17  16  15  14  13  12  11  10  9   8   7   6   5   4   3   2   1   0
        # | 1 | X | X | X | X | X | X | X | 0 | X | X | X | X | X | X | X | 0 | X | X | X | X | X | X | X |
        # 
        
        if board == 1:
            command = {"CMD":7, "Bytestream":bytestream}
            reply = self.send_json(command)
            if reply["Status"] != "Success":
                raise Exception("Failed to send command to board 1", reply)
            if bytestream != reply["Echo"]:
                print ("Sent", repr(bytestream), "but got", reply["Echo"])
            
        elif board == 2:
            command = {"CMD":8, "Bytestream":bytestream}
            reply = self.send_json(command)
            if reply["Status"] != "Success":
                raise Exception("Failed to send command to board 1", reply)
            if bytestream != reply["Echo"]:
                print ("Sent", repr(bytestream), "but got", reply["Echo"])

        else:
            raise Exception("Pick a board that exists 1 or 2")
        
        
    def loadOffsets(self, board):
        self.sendCmd(bytearray([0b11110000, 0, 0]), board)

    def setOffset(self, clock, offset, board, enable=True):
        # #The structure of the command
        #   23  22  21  20  19  18  17  16  15  14  13  12  11  10  9   8   7   6   5   4   3   2   1   0
        # | 1 | 0 | 0 | X | X | X | X | X | 0 | X | X | C | Z | Y | Y | Y | 0 | Y | Y | Y | Y | Y | Y | Y |
        #  X = 7 bit clock select
        #  Y = 10 bit half-phase offset
        #  Z = phase of first oscillation
        #  C = Output enable bit
        if clock > 0b01111111:
            raise Exception("Clock selected is too large!")
        
        if isinstance(offset, float):
            offset = int(1250 * (offset / (2 * math.pi)))

        sign = 0
        offset = offset % 1250
        if offset > 624:
            sign = 1
            offset = offset - 624

        # Place the first 7 bits of the offset into the low_offset byte
        low_offset =  offset & 0b01111111
        # Place the remaining 3 bits of the offset, plus the sign bit, into the high offset
        high_offset = ((offset >> 7) & 0b00000111) + (sign << 3)

        #The command byte has the command bit set, plus 5 bits of the clock select
        b1 = 0b10000000 | (clock >> 2)
        #The next bit has the output enable bit set high, plus the last two bits of the clock select, and the high offset bits
        enable_bit = 0b00010000
        if not enable:
            enable_bit = 0b00000000
        
        b2 = enable_bit | ((clock & 0b00000011)<<5)  | high_offset
        #The last byte contains the low offset bits
        b3 = low_offset
        cmd = bytearray([b1, b2, b3])
        #print(list(map(bin,cmd)))
        self.sendCmd(cmd, board)

    def setOutputDACPower(self, power, board):
        # #The structure of the command
        #   23  22  21  20  19  18  17  16  15  14  13  12  11  10  9   8   7   6   5   4   3   2   1   0
        # | 1 | 1 | 1 | X | X | X | X | X | 0 | X | X | X | X | X | X | Y | 0 | Y | Y | Y | Y | Y | Y | Y |
        #  X = UNUSED
        #  Y = 7 bit DAC value
        if power > 256: #Not a mistake! the DAC goes from 0-256, not 255!
            raise Exception("Power selected is too large!")

        cmd = bytearray([0b11100000, 0b00000011 & (power >> 7), 0b01111111 & power])
        self.sendCmd(cmd, board) 

    def setOutputDACDivisor(self, divisor, board):
        # #The structure of the command
        #   23  22  21  20  19  18  17  16  15  14  13  12  11  10  9   8   7   6   5   4   3   2   1   0
        # | 1 | 0 | 1 | Y | Y | Y | Y | Y | 0 | Y | Y | Y | Y | Y | Y | Y | 0 | Y | Y | Y | Y | Y | Y | Y |
        #  X = UNUSED
        #  Y = 7 bit DAC value
        if divisor > 0b1111111111111111111:
            raise Exception("Divisor selected is too large!")
        if divisor < 50:
            raise Exception("You'll burn out the board if this divisor is too low (<50).")
        cmd = bytearray([0b10100000 | (0b00011111 & (divisor >> 14)), 0b01111111 & (divisor >> 7), 0b01111111 & divisor])
        self.sendCmd(cmd, board) 

    def setOutputDACFreq(self, freq, board):
        self.setOutputDACPower(128) #50% duty cycle, turns the board off and on for equal amounts of time
        divisor=int(5e7/(4*freq)+1)
        return self.setOutputDACDivisor(divisor, board)
        
    def disableOutput(self, clock, board):
        self.setOffset(clock, 0, board, enable=False)
        

        
