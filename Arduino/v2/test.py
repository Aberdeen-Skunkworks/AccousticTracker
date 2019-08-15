#!/usr/bin/python3

board = 1
from Controller import *
import Functions
with Controller() as com:
    command = {"CMD":2}
    reply = com.send_json(command)
    print(reply)
    command_power = Functions.create_board_command_power(board, 0)
    reply_power = com.send_json(command_power)
    if reply_power["Status"] != "Success":
        raise Exception("Failed! ", reply_power)
