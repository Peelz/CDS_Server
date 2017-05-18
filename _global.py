
# Car Value
SYSTEM_STATUS = 0 	#System status
CURRENT_SPEED = 0	#Car Status
CURRENT_GEAR = "N"
CURRENT_WHEEL_ANGLES = 90
ACCELERATOR = 0
BRAKE = 0

# Static Value
DEFALUT_SPEED = 0
DEFALUT_GEAR = "N"


# Queue of order from data reciever
import Queue
TASK_QUEUE = Queue.Queue() 


# Phone Object socket
PHONE_DRIVER = None
PHONE_CMD = None

# Driving SIMULATOR set Object socket
SIMULATOR_SET_DRIVER = None
SIMULATOR_SET_CMD = None

# Current Driver Object socket 
DRIVER = None

""" Determine 

0 = PH Control
1 = SIM Control
None = No Client 
"""
CONTROL_MODE = None

# Host Ip
HOST = "192.168.137.73"


# Set Logger
import logging
logging.basicConfig(level=logging.DEBUG)


                                                                                                                            
                                                                                                                            
acii_text  = " _____             ______      _       _               _____ _                 _       _              \n"
acii_text += "/  __ \            |  _  \    (_)     (_)             /  ___(_)               | |     | |             \n"
acii_text += "| /  \/ __ _ _ __  | | | |_ __ ___   ___ _ __   __ _  \ `--. _ _ __ ___  _   _| | __ _| |_ ___  _ __  \n"
acii_text += "| |    / _` | '__| | | | | '__| \ \ / / | '_ \ / _` |  `--. \ | '_ ` _ \| | | | |/ _` | __/ _ \| '__| \n"
acii_text += "| \__/\ (_| | |    | |/ /| |  | |\ V /| | | | | (_| | /\__/ / | | | | | | |_| | | (_| | || (_) | |    \n"
acii_text += " \____/\__,_|_|    |___/ |_|  |_| \_/ |_|_| |_|\__, | \____/|_|_| |_| |_|\__,_|_|\__,_|\__\___/|_|    \n"
acii_text += "                                                __/ |                                                 \n"
acii_text += "                                               |___/                                                  \n"