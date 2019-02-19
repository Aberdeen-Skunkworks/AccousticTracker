from Controller import *

with Controller() as com:
    command = {"CMD":2}
    reply = com.send_json(command)
    print(reply)
