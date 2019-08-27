#!/usr/bin/python3

board = 1
from Controller import *
import Functions
with Controller() as com:
    command = {"CMD":2}
    reply = com.send_json(command)
    print(reply)

    # Send Power setting command
    command_power = Functions.create_board_command_power(board, 511)
    reply = com.send_json(command_power)
    if reply["Status"] != "Success":
        raise Exception("Failed to start conversion", reply)
            
    for i in range(100):
        # Send offset commands
        command = Functions.create_board_command_offset(board, i, 0.1*i, enable=True)
        reply = com.send_json(command)
        if reply["Status"] != "Success":
            raise Exception("Failed to start conversion", reply)
        
                
    # Send load offset command
    command = Functions.create_board_command_load_offsets(board)
    reply = com.send_json(command)
    if reply["Status"] != "Success":
        raise Exception("Failed to start conversion 1", reply)
