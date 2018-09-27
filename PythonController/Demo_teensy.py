#!/usr/bin/python3
##############################################################################
#-------------------------DEMO with Teensy-----------------------------------#
##############################################################################


## ----------------- Writing transducer locations to rt ------------------ ##
import sys
sys.path.insert(0, '../../Project-X/')
import numpy as np; import transducer_placment; import matplotlib.pyplot as plt;
import phase_algorithms; import math; import algorithms; import time; from PyQt5 import QtWidgets; 
import sys; import Functions


trans_to_delete = []  # List of unwanted transducers leave blank to keep all
rt = transducer_placment.big_daddy()
rt = transducer_placment.delete_transducers(rt,trans_to_delete)
ntrans = len(rt); 
#x = np.zeros(ntrans); y = np.zeros(ntrans)
#for transducer in range (0,ntrans): # Writing the coordinates to output rt
#    x[transducer]= rt[transducer,0]
#    y[transducer]= rt[transducer,1] 
#plt.plot(x, y,'ro'); plt.show() # Show Plot of the positions
# -------------------------------------------------------------------------- #p

board = input("Please choose a Board 1 or 2: ")

print(" ")
print("Control modes:")
print("(o) = OFF")
print("(n) = ON")
print("(h) = Haptic")
print("(p) = Pattern")
print("(power) = Wireless Power")
print("(two) = Two boards, Needs work for both boards at once - not working")
print("(music) = Music mode (Buzzing noise from harmonics)")
print("(t) = Start midi sound mode")
print("(GUI) = Graphical user interface mode - not working")

choose = input("Please choose a mode from above: ")
## --------------------------- Turn off --------------------------- ##

if choose == ("o"):
    
    from Controller import Controller
    with Controller() as com:        
        command_power = Functions.create_board_command_power(board, 0)
        reply_power = com.send_json(command_power)
        if reply_power["Status"] != "Success":
            raise Exception("Failed to start conversion 2", reply_power)
            
## --------------------------- Turn On --------------------------- ##
elif choose == ("n"):
    
    from Controller import Controller
    with Controller() as com:        
        command_power = Functions.create_board_command_power(board, 256)
        reply_power = com.send_json(command_power)
        if reply_power["Status"] != "Success":
            raise Exception("Failed to start conversion 2", reply_power)
            

                   
## --------------------------- Haptic feedback --------------------------- ##
    


elif choose == ("h"):
    print ("Haptic mode selected")
       
    phi_focus = phase_algorithms.phase_find(rt,0,0,0.10)

    from Controller import Controller
    with Controller() as com:        
        for i in range(88):
            # Send offset commands
            command = Functions.create_board_command_offset(board, i, phi_focus[i], True)
            reply = com.send_json(command)
            if reply["Status"] != "Success":
                raise Exception("Failed to start conversion 1", reply)
                
        # Send load offset command
        command = Functions.create_board_command_load_offsets(board)
        reply = com.send_json(command)
        if reply["Status"] != "Success":
            raise Exception("Failed to start conversion 1", reply)
        
        # Send Power setting command
        command_power = Functions.create_board_command_power(board, 256)
        reply_power = com.send_json(command_power)
        if reply_power["Status"] != "Success":
            raise Exception("Failed to start conversion 2", reply_power)
            
        # Send Frequency command 
        #command_freq = Functions.create_board_command_divisor(board, 512)
        command_freq = Functions.create_board_command_freq(board, 200)
        reply_freq = com.send_json(command_freq)
        if reply_freq["Status"] != "Success":
            raise Exception("Failed to start conversion 2", reply_freq)
            

## -------------------------- Focused traps ------------------------------- ##  

elif choose == ("p"):
    print ("Pattern mode selected")
    

    phi_focus = phase_algorithms.phase_find(rt,0,0,0.018)
    phi = phase_algorithms.add_twin_signature(rt, phi_focus, 0)

    from Controller import Controller
    with Controller() as com:  
        
        # Send Power setting command
        command_power = Functions.create_board_command_power(board, 511)
        reply = com.send_json(command_power)
        if reply["Status"] != "Success":
            raise Exception("Failed to start conversion", reply)
            
        for i in range(88):
            # Send offset commands
            command = Functions.create_board_command_offset(board, i, phi[i])
            reply = com.send_json(command)
            if reply["Status"] != "Success":
                raise Exception("Failed to start conversion", reply)
                
        # Send load offset command
        command = Functions.create_board_command_load_offsets(board)
        reply = com.send_json(command)
        if reply["Status"] != "Success":
            raise Exception("Failed to start conversion 1", reply)
        

## --------------------------- Wireless power --------------------------- ##
    

elif choose == ("power"):
    print ("Wireless Power mode selected")
       
    phi_zeros = np.zeros(88)
    phi_focus = phase_algorithms.phase_find(rt,0,0,0.60)

    from Controller import Controller
    with Controller() as com:        
        for i in range(88):
            # Send offset commands
            command = Functions.create_board_command_offset(board, i, phi_zeros[i], True)
            reply = com.send_json(command)
            if reply["Status"] != "Success":
                raise Exception("Failed to start conversion 1", reply)
                
        # Send load offset command
        command = Functions.create_board_command_load_offsets(board)
        reply = com.send_json(command)
        if reply["Status"] != "Success":
            raise Exception("Failed to start conversion 1", reply)
        
        # Send Power setting command
        command_power = Functions.create_board_command_power(board, 511)
        reply_power = com.send_json(command_power)
        if reply_power["Status"] != "Success":
            raise Exception("Failed to start conversion 2", reply_power)

                
## -------------------------- Haptic moving ------------------------------- ##

elif choose == ("hm"):
    print ("Haptic move mode selected")
    
    circle_co_ords = algorithms.circle_co_ords(10, 0.02)
    #line_coordinates = np.linspace(0,2,100)
    
    
    phi_focus = np.zeros([ntrans,len(circle_co_ords[0])])
    phi =  np.zeros([ntrans,len(circle_co_ords[0])])
    phase_index = np.zeros(([ntrans,len(circle_co_ords[0])]),dtype=int)
    

    for point in range (0,len(circle_co_ords[0])):
        
        phi_focus_all = phase_algorithms.phase_find(rt,circle_co_ords[0][point], circle_co_ords[1][point], 0.05) # phi is the initial phase of each transducer to focus on a point
        for transducer in range(0,ntrans):
            phi_focus[transducer][point] = phi_focus_all[transducer]

    from Controller import Controller
    with Controller() as com:    
            # Send Power setting command
            command_power = Functions.create_board_command_power(board, 128)
            reply_power = com.send_json(command_power)
            if reply_power["Status"] != "Success":
                raise Exception("Failed to start conversion 2", reply_power)
                
            # Send Frequency command 
            command_freq = Functions.create_board_command_freq(board, 100)
            reply_freq = com.send_json(command_freq)
            if reply_freq["Status"] != "Success":
                raise Exception("Failed to start conversion 2", reply_freq)
                    
            while True:
                for point in range (0,len(circle_co_ords[0])):
                    for i in range(88):
                        # Send offset commands
                        command = Functions.create_board_command_offset(board, i, phi_focus[i][point], True)
                        reply = com.send_json(command)
                        if reply["Status"] != "Success":
                            raise Exception("Failed to start conversion 1", reply)
                            
                    # Send load offset command
                    command = Functions.create_board_command_load_offsets(board)
                    reply = com.send_json(command)
                    if reply["Status"] != "Success":
                        raise Exception("Failed to start conversion 1", reply)
            

# -------------------------------------------------------------------------- #

elif choose == ("two"):
    print ("Two boards mode selected")
    
    sideways_1 = np.copy(rt)
    sideways_2 = np.copy(rt)
    
    sideways_1[:,0] = np.add(rt[:,2], -0.0925)
    sideways_1[:,2] = np.add(rt[:,0], 0.05)
    
    sideways_2[:,0] = np.add(rt[:,2], 0.0925)
    sideways_2[:,2] = np.add(rt[:,0], 0.05)

    
    phi_focus = phase_algorithms.phase_find(sideways_1,0,0,0.05) # phi is the initial phase of each transducer to focus on a point
    phi = phase_algorithms.add_twin_signature(sideways_1,phi_focus)
    phase_index = np.zeros((ntrans),dtype=int)
    #phi_focus = algorithms.read_from_excel_phases() # Takes phases from an excel spreadsheet of phases from 0 to 2pi, any over 2pi just loops
    for transducer in range(0,ntrans):
        phase_index[transducer] = int(2500-phi[transducer]/((2*math.pi)/1250))

    
    from connect import Controller 
    with Controller() as ctl:
        ctl.setOutputDACPower(256)
        ctl.setOutputDACDivisor(100)
        print("got here")
        for i in range(ctl.outputs):
            ctl.setOffset(i,phase_index[i])
        ctl.loadOffsets()
        print("loaded offsets")

            
# -------------------------------------------------------------------------- #


elif choose == ("music"):
    
    import wave, struct, numpy as np
    from scipy.io import wavfile
    from Controller import Controller
    
    #fs, data = wavfile.read('8bit.wav')
    fs, data = wavfile.read('CantinaSong.wav')
    ##fs, data = wavfile.read('8bit10sec.wav')
    #
    data = data[:min(len(data),100000)]
    #data = [int(110*math.sin(i/8*math.pi)+128) for i in range(100000)]
    size = len(data)
    print("Wave size",size,"bytes")
    data_bytes = bytearray(data)

    
    print("Finished reading wav from file")
    
    with Controller() as com:      
        command = Functions.create_board_command_freq(board, 40000)
        reply = com.send_json(command)
        if reply["Status"] != "Success":
            raise Exception("Failed to send DAC freq", reply)
        
        # Send command
        command = Functions.create_board_command_wav(board, fs, size)
        reply = com.send_json(command)
        if reply["Status"] != "Success":
            raise Exception("Failed to send song start", reply)
        
        print("Starting byte send")
        com.com.write(data_bytes)
        com.com.write(b"\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        print("Byte send complete")
                        
elif choose == ("test"):
    
    import wave, struct, numpy as np
    from scipy.io import wavfile
    from Controller import Controller
    
    data = np.linspace(0,253, 160000, dtype = int)
    data = data.tolist()
    #data = [1,2,3,4,5,6,1,2,3,4,5,6,1,2,3,4,5,6,1,2,3,4,5,6,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,34,125]

    fs = 12000
    size = len(data)
    startMarker = 255
    endMarker = 254
    
    for i in range(size):
        if data[i] == 255 or data[i] == 254:
            data[i] = 253
            
    data_bytes = bytearray(data)
    command = Functions.create_board_command_wav(board, fs, size)
    
    with Controller() as com:  
        # Send command
        reply = com.send_json(command)
        if reply["Status"] != "Success":
            raise Exception("Failed to send song", reply)
                
        com.com.write(bytes([startMarker]))
        com.com.write(data_bytes)
        com.com.write(bytes([endMarker]))

# -------------------------------------------------------------------------- #

elif choose == ("t"):
    
    import mido
    from Controller import Controller
    with Controller() as com:  
        
        phi_focus = phase_algorithms.phase_find(rt,0,0,0.07)
        
        for i in range(88):
            # Send offset commands
            command = Functions.create_board_command_offset(board, i, 0, True)
            reply = com.send_json(command)
            if reply["Status"] != "Success":
                raise Exception("Failed to start conversion 1", reply)
                
        # Send load offset command
        command = Functions.create_board_command_load_offsets(board)
        reply = com.send_json(command)
        if reply["Status"] != "Success":
            raise Exception("Failed to start conversion 1", reply)
        
        # Send power command
        command_power = Functions.create_board_command_power(board, 128)
        reply_power = com.send_json(command_power)
        if reply_power["Status"] != "Success":
            raise Exception("Failed to start conversion 2", reply_power)
            
        #song_file = mido.MidiFile('prelC.mid')
        song_file = mido.MidiFile('for_elise_by_beethoven.mid')
        
        for msg in song_file:
            time.sleep(msg.time)
            if msg.type == 'note_on':
                
                # Send power command
                command_power = Functions.create_board_command_power(board, 128)
                reply_power = com.send_json(command_power)
                if reply_power["Status"] != "Success":
                    raise Exception("Failed to start conversion 2", reply_power)
                    
                # Send Frequency command 
                command_freq = Functions.create_board_command_freq(board, Functions.midi_to_hz(msg.note))
                reply_freq = com.send_json(command_freq)
                if reply_freq["Status"] != "Success":
                    raise Exception("Failed to start conversion 2", reply_freq)
                    
            if msg.type == 'note_off':
                # Send power command
                command_power = Functions.create_board_command_power(board, 0)
                reply_power = com.send_json(command_power)
                if reply_power["Status"] != "Success":
                    raise Exception("Failed to start conversion 2", reply_power)
                
 
# -------------------------------------------------------------------------- #

elif choose == ("GUI"):
    print ("GUI mode selected")
    
    import math; import phase_algorithms; import numpy as np; import transducer_placment
    
    # Initial position in m (x , y , z) (z = up)
    global x,y,z, angle, haptic_toggle
    x = 0    
    y = 0
    z = 0.02
    angle = 0
    haptic_toggle = False
    rt = transducer_placment.big_daddy()
    ntrans = len(rt);
    phi = np.zeros((ntrans),dtype=int)
    
    class Window_update_trap(QtWidgets.QWidget):
    
        def __init__(self):
            
            super().__init__()
            
            from Controller import Controller
            self.com = Controller()
            self.com.__enter__()
            self.init_ui()
            self.turn_on_board_click()
            self.calculate_and_move_trap()

        
        def init_ui(self):
            
            
            self.forward = QtWidgets.QPushButton('Forward')
            self.backward = QtWidgets.QPushButton('Backwards')
            self.right = QtWidgets.QPushButton('Right')
            self.left = QtWidgets.QPushButton('Left')
            self.up = QtWidgets.QPushButton('Up')
            self.down = QtWidgets.QPushButton('Down')
            self.haptic = QtWidgets.QPushButton('Haptic Toggle')
            self.reset = QtWidgets.QPushButton('Reset to [0, 0, 0.02]')
            self.turn_off = QtWidgets.QPushButton('OFF')
            self.turn_on = QtWidgets.QPushButton('ON')   
            self.capture = QtWidgets.QPushButton('Capture')   
        
            
            self.label1 = QtWidgets.QLabel('Movement Controls')
            self.label2 = QtWidgets.QLabel('Extra Controls')
    
    
            h_box_label = QtWidgets.QHBoxLayout()
            h_box_label.addStretch()
            h_box_label.addWidget(self.label1)
            h_box_label.addStretch() 
            
            h_box_labe2 = QtWidgets.QHBoxLayout()
            h_box_labe2.addStretch()
            h_box_labe2.addWidget(self.label2)
            h_box_labe2.addStretch() 
            
            h_box = QtWidgets.QHBoxLayout()
            h_box.addWidget(self.down)
            h_box.addWidget(self.forward)
            h_box.addWidget(self.up) 
        
            h_box2 = QtWidgets.QHBoxLayout()
            h_box2.addWidget(self.left)
            h_box2.addWidget(self.backward)
            h_box2.addWidget(self.right) 
            
            h_box3 = QtWidgets.QHBoxLayout()
            h_box3.addWidget(self.haptic)
            h_box3.addWidget(self.capture)
            h_box3.addWidget(self.reset)
            
            h_box4 = QtWidgets.QHBoxLayout()
            h_box4.addWidget(self.turn_on)
            h_box4.addWidget(self.turn_off)

        
            v_box = QtWidgets.QVBoxLayout()
            v_box.addLayout(h_box_label)
            v_box.addLayout(h_box)
            v_box.addLayout(h_box2)
            v_box.addLayout(h_box_labe2)
            v_box.addLayout(h_box3)
            v_box.addLayout(h_box4)
            
            self.setLayout(v_box)
            self.setWindowTitle('Particle Mover!')
            
            self.forward.clicked.connect(self.forward_click)
            self.backward.clicked.connect(self.backward_click)
            self.left.clicked.connect(self.left_click)
            self.right.clicked.connect(self.right_click)
            self.up.clicked.connect(self.up_click)
            self.down.clicked.connect(self.down_click)
            self.haptic.clicked.connect(self.haptic_click)
            self.reset.clicked.connect(self.reset_click)
            self.turn_off.clicked.connect(self.turn_off_board_click)
            self.turn_on.clicked.connect(self.turn_on_board_click)
            self.capture.clicked.connect(self.capture_click)
            
            self.show()
    
        def calculate_and_move_trap(self):
            global phi, angle, haptic_toggle
            t1 = time.time()
            phi_focus = phase_algorithms.phase_find(rt,x,y,z)
            t2 = time.time()
            # Making it so if haptic is on it will only focus and if its off it will add the pattern
            if haptic_toggle == False:
                phi = phase_algorithms.add_twin_signature(rt,phi_focus, angle)
            else:
                phi = phi_focus
            t3 = time.time()
            #print("T1 = :", t2-t1)
            #print("T2 = :", t3-t2)
            t4 = time.time()
            for i in range(88):
                # Send offset commands
                command = Functions.create_board_command_offset(board, i, phi[i])
                reply = self.com.send_json(command)
                if reply["Status"] != "Success":
                    raise Exception("Failed to start conversion", reply)
            t5 = time.time()  
            #print("T3 = :", t5-t4)
            # Send load offset command
            command = Functions.create_board_command_load_offsets(board)
            reply = self.com.send_json(command)
            if reply["Status"] != "Success":
                raise Exception("Failed to start conversion 1", reply)

        
        def turn_off_board_click(self):
            global haptic_toggle
            print("Board off")
            haptic_toggle = False
            command_power = Functions.create_board_command_power(board, 0)
            reply_power = self.com.send_json(command_power)
            if reply_power["Status"] != "Success":
                raise Exception("Failed to start conversion 2", reply_power)

        def turn_on_board_click(self):
            global haptic_toggle
            print("Board on")
            haptic_toggle = False
            command_power = Functions.create_board_command_power(board, 511)
            reply_power = self.com.send_json(command_power)
            if reply_power["Status"] != "Success":
                raise Exception("Failed to start conversion 2", reply_power)
                
        def capture_click(self):
            
            for up in range(50):
                global z
                print("Rising trap 2 cm")
                z += 0.0004
                self.calculate_and_move_trap()
                time.sleep(0.05)
                print("Raised to final height")
    
        def forward_click(self):
            global x, angle  
            angle = 0
            if haptic_toggle:
                x += 0.01
            else:
                x += 0.001
            self.calculate_and_move_trap()
            print('x changed to = ', "%.3f" % x)
        
        def backward_click(self):
            global x, angle  
            angle = 0
            if haptic_toggle:
                x -= 0.01
            else:
                x -= 0.001
            self.calculate_and_move_trap()
            print('x changed to = ', "%.3f" % x)
            
        def left_click(self):
            global y, angle  
            angle = 90
            if haptic_toggle:
                y += 0.01
            else:
                y += 0.001
            self.calculate_and_move_trap()
            print('y changed to = ', "%.3f" % y)
            
        def right_click(self):
            global y, angle  
            angle = 90
            if haptic_toggle:
                y -= 0.01
            else:
                y -= 0.001
            self.calculate_and_move_trap()
            print('y changed to = ', "%.3f" % y)
            
        def up_click(self):
            global z
            if haptic_toggle:
                z += 0.01
            else:
                z += 0.001
            self.calculate_and_move_trap()
            print('z changed to = ', "%.3f" % z)
            
        def down_click(self):
            global z
            if haptic_toggle:
                 z -= 0.01
            else:
                z -= 0.001
            self.calculate_and_move_trap()
            print('z changed to = ', "%.3f" % z)
            
        def haptic_click(self):
            global haptic_toggle
            if haptic_toggle == False:
                print('Haptic mode activated')
                # Send Power setting command
                command_power = Functions.create_board_command_power(board, 256)
                reply_power = self.com.send_json(command_power)
                if reply_power["Status"] != "Success":
                    raise Exception("Failed to start conversion 2", reply_power)
                    
                # Send Frequency command 
                #command_freq = Functions.create_board_command_divisor(board, 512)
                command_freq = Functions.create_board_command_freq(board, 200)
                reply_freq = self.com.send_json(command_freq)
                if reply_freq["Status"] != "Success":
                    raise Exception("Failed to start conversion 2", reply_freq)
                haptic_toggle = True
            else:
                print('Haptic mode De-activated')
                haptic_toggle = False
                self.turn_on_board_click()
            
        def reset_click(self):
            global x,y,z
            x = 0; y = 0; z = 0.02;
            self.calculate_and_move_trap()
            print(' ')
            print('Reset to [0, 0, 0.02]')
    
    app = QtWidgets.QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    a_window = Window_update_trap()
    sys.exit(app.exec_())
    
# -------------------------------------------------------------------------- #

else:
    print("Come on, pick one of the correct letters!")
