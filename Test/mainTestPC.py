# import server_pc 
import socket 
import Queue
import threading
import time
import sets 
import logging


SYSTEM_STATUS = 0 	#System status


CURRENT_SPEED = 0	#Car Status
CURRENT_GEAR = "n"
CURRENT_WHEEL_ANGLES = 90


"""
"""
ACCELERATOR = 0
BRAKE = 0


"""
Static Value
"""
DEFALUT_SPEED = 0
DEFALUT_GEAR = "n"

"""
Queue of order from data reciever
"""
TASK_QUEUE = Queue.Queue() 

"""
Phone Object socket
"""
PHONE_DRIVER = None
PHONE_CMD = None
"""
Driving SIMULATOR set Object socket
"""
SIMULATOR_SET_DRIVER = None
SIMULATOR_SET_CMD = None

"""
Current Driver Object socket 
"""
DRIVER = None

""" 
Determine 
0 = PH Control
1 = SIM Control
None = No Client 
"""
CONTROL_MODE = None

CLIENT_WHITELIST = sets.Set()
THREAD_POOL = []

HOST = "192.168.100.1"

"""
Command Server
"""

logging.basicConfig(level=logging.DEBUG)

def MainSocket():
	command_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	command_sock.bind((HOST, 7769))
	command_sock.listen(3)

	while True:
		conn, addr = command_sock.accept()
		logging.debug( "Main socket connect from %r", addr)
		socketAuthenticate(conn,addr)

def mainSocketReceiver(conn, addr):
	try:
		while True:
			raw_data = conn.recv(1024)
			command(raw_data)
	except Exception as e:
		logging.debug("Command Socket Disconnected from %r %r", addr, e)
		global CURRENT_SPEED,CURRENT_GEAR,CURRENT_WHEEL_ANGLES,ACCELERATOR,BRAKE
		#set car defult value  
		CURRENT_SPEED = 0
		CURRENT_GEAR = "n"
		CURRENT_WHEEL_ANGLES = 90
		ACCELERATOR = 0
		BRAKE = 0
		

"""
Driver Control Socket
"""
def DriverControlSocket():
	global CONTROL_MODE, PHONE_DRIVER, CONTROL_MODE, SIMULATOR_SET_DRIVER, PHONE_DRIVER


	driver_control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	driver_control_sock.bind((HOST, 7789))
	driver_control_sock.listen(3)

	try :

		while True:
			conn, addr = driver_control_sock.accept()
			logging.debug( "Driver socket connect from %r", addr)
			id_mess = conn.recv(1024)

			if id_mess == "PHONE":
				PHONE_DRIVER = DeviceSocket(conn, "PHONE")
				PHONE_DRIVER.getEvent().set()
				PHONE_DRIVER.start()

				CONTROL_MODE = 0

			elif id_mess == "SIMULATOR_SET":
				SIMULATOR_SET_DRIVER = DeviceSocket(conn, "SIMULATOR_SET")	

				if PHONE_DRIVER == None:
					SIMULATOR_SET_DRIVER.getEvent().set()
					CONTROL_MODE = 1

				else:
					SIMULATOR_SET_DRIVER.getEvent().clear()

				SIMULATOR_SET_DRIVER.start()

			else:
				conn.close()
	except Exception as e :
		raise e

def command(message):
	command = message.split()[0] 

	if command == '-cg':
		changeGear(message.split()[1] )

	if command == '-cm':
		changeControlmode(message.split()[1])

def changeControlmode(cmd):
	global CONTROL_MODE, PHONE_DRIVER, CONTROL_MODE, SIMULATOR_SET_DRIVER

	print cmd 
	if cmd == "phone" and CONTROL_MODE != 0 and PHONE_DRIVER != None:
		CONTROL_MODE = 0
		SIMULATOR_SET_DRIVER.getEvent().clear()
		PHONE_DRIVER.getEvent().set()
		print "Change control mode to", cmd

	elif cmd == "sim" and SIMULATOR_SET_DRIVER != None:
		CONTROL_MODE = 1
		SIMULATOR_SET_DRIVER.getEvent().set()
		PHONE_DRIVER.getEvent().clear()

		print "Change control mode to", cmd

	else :
		print "Control mode not change"

	

def socketAuthenticate(conn, addr):
	conn.send("-sq Who're you")
	auth_data = conn.recv(1024)

	if auth_data == "-a PHONE":
		PHONE_CMD = conn
		threading.Thread(target=mainSocketReceiver, args=(conn, addr)).start()

	elif auth_data == "-a SIMULATOR_SET" :
		SIMULATOR_SET_CMD = conn
		threading.Thread(target=mainSocketReceiver, args=(conn, addr)).start() ########################################add

	else:
		conn.close()
		print addr," connection failed to Authenticate"


"""
Set Current Speed 
"""
def updateCurrentValue (in_head,in_data):
	
	if in_head == 'a': 						#update current accelerator
		accelerator = float(in_data)

		global ACCELERATOR
		ACCELERATOR = accelerator 


	elif in_head == 'b': 					#update current brake
		brake = float(in_data)
		
		global BRAKE
		BRAKE = brake

	elif in_head == 'g': 					#update current gear
		gear = str(in_data)
		
		global CURRENT_GEAR
		CURRENT_GEAR = gear
	
	elif in_head == 't': 					#update current degree
		angles = int(in_data)
		
		global CURRENT_WHEEL_ANGLES
		CURRENT_WHEEL_ANGLES = angles

def CurrentSpeedControl():
	global CURRENT_SPEED,ACCELERATOR,BRAKE,CURRENT_GEAR
	while True:
		
		
		if CURRENT_GEAR == 'd':
			defaultSpeed = 5.0
			forwardMaxSpeed = 120.0
			
			decreaseSpeed = 0.5/100 							#0.5/sec
			accelerator_to_speed = (ACCELERATOR/12.17)/100 	#0-100 12.17sec 
			brake_to_speed = (BRAKE/7)/100 					#100-0 7sec
			
			
			if CURRENT_SPEED == 0 and ACCELERATOR == 0 and BRAKE != 0: 	#unAcc+brake
				
				CURRENT_SPEED = 0
				
			elif CURRENT_SPEED == 0 and ACCELERATOR == 0 and BRAKE == 0:	#unAcc+unBrake
				CURRENT_SPEED = defaultSpeed
			
			
			else:
				
				CURRENT_SPEED = CURRENT_SPEED + accelerator_to_speed - brake_to_speed - decreaseSpeed
				
				if CURRENT_SPEED > forwardMaxSpeed:
					CURRENT_SPEED = forwardMaxSpeed
				elif CURRENT_SPEED <= defaultSpeed and BRAKE == 0:
					CURRENT_SPEED = defaultSpeed
				elif CURRENT_SPEED <= defaultSpeed and BRAKE != 0: #add
					CURRENT_SPEED = 0
				elif CURRENT_SPEED < 0:
					CURRENT_SPEED = 0
			
		elif CURRENT_GEAR == 'r':
			defaultSpeed = 5.0
			reverseMaxSpeed = 40.0

			decreaseSpeed = 0.5/100						#0.5/sec			
			accelerator_to_speed = (ACCELERATOR/12.17)/100  	#0-100 12.17sec 
			brake_to_speed = (BRAKE/7)/100 					#100-0 7sec
			
			
			if CURRENT_SPEED == 0 and ACCELERATOR == 0 and BRAKE != 0: #unAcc+brake
				
				CURRENT_SPEED = 0
				
			elif CURRENT_SPEED == 0 and ACCELERATOR == 0 and BRAKE == 0:#unAcc+unBrake
				CURRENT_SPEED = defaultSpeed
			
			
			else:
				
				CURRENT_SPEED = CURRENT_SPEED + accelerator_to_speed - brake_to_speed - decreaseSpeed
				if CURRENT_SPEED > reverseMaxSpeed:
					CURRENT_SPEED = reverseMaxSpeed
				elif CURRENT_SPEED <= defaultSpeed and BRAKE == 0:
					CURRENT_SPEED = defaultSpeed
				elif CURRENT_SPEED <= defaultSpeed and BRAKE != 0: #add
					CURRENT_SPEED = 0
				elif CURRENT_SPEED < 0:
					CURRENT_SPEED = 0
		
		elif CURRENT_GEAR == 'p':
			
			CURRENT_SPEED = 0
		elif CURRENT_GEAR == 'n':
			
			CURRENT_SPEED = 0

"""
Command Motor By CURRENT_SPEED
"""
def MotorController():
	global CURRENT_GEAR,CURRENT_SPEED

	while True:
		
		if CURRENT_GEAR == 'd':
			if CURRENT_SPEED < 5:
				pwmForword = 0.0
			else:
				pwmForword= 0.2+((0.8/120)*CURRENT_SPEED)
			
			#board.digital[3].write(pwmForword)

		elif CURRENT_GEAR == 'r':
			
			if CURRENT_SPEED < 5:
				pwmReverse = 0.0
			else:
				pwmReverse= 0.2+((0.8/120)*CURRENT_SPEED)

			#board.digital[5].write(pwmReverse)
			

		elif CURRENT_GEAR == 'p':
			pwm = 0.1
			#board.digital[3].write(0.1)
			

		elif CURRENT_GEAR == 'n':
			pwm = 0
			#board.digital[3].write(0)
"""
Command Servo By CURRENT_WHEEL_ANGLES
"""
def ServoController():
	global CURRENT_WHEEL_ANGLES
	while True:
		
		left = 65 											#left max degree
		right = 115 										#right max degree
		carDegree = left+(((right-left)*CURRENT_WHEEL_ANGLES)/180)		#cal degree servo
		#board.digital[12].write(carDegree)	


def DriverController():
	global CONTROL_MODE, DRIVER
	if CONTROL_MODE == 1:
		if DRIVER != None and SIMULATOR_SET.is_connect :
			SIMULATOR_SET.stop()
		PHONE.start()

def SystemCommand(command):
	global SYSTEM_STATUS
	if command == "shutdown":
		SYSTEM_STATUS = 0

	elif command == "start":
		SYSTEM_STATUS =1
	else:
		pass

"""
@param
String head
Integer value
Use tasking low-level devices 
"""
def changeGear(value):
	global CURRENT_GEAR
	if CURRENT_GEAR != value :
		CURRENT_GEAR = value
		print "Change gear to ", value

def assignTask(head, value):
	control_head = ['a','t','b']
	if head in control_head:
		TASK_QUEUE.put(head+value)
	elif head == 'g' :
		changeGear(value)

def decode(income_data):
	__header = ['a','b','t','g']
	block_head = ""
	block_value = ""

	lenght = len(income_data)

	for i in range(lenght):
		if income_data[i] in __header  :
			if block_head != "":
				assignTask(block_head, block_value)
				
				block_head = income_data[i]
				block_value = ""

			else:
				block_head = income_data[i]
				block_value = ""	

		else:
			block_value += income_data[i]

		if i == lenght-1 :
			assignTask(block_head, block_value)
			

def decodeFromTaskQueue(task_data): 
	__header = ['a','b','t','g']
	block_head = ""
	block_value = ""

	lenght = len(task_data)

	for i in range(lenght):
		if task_data[i] in __header  :
			if block_head != "":
				updateCurrentValue(block_head, block_value)
				print block_head, block_value
				block_head = task_data[i]
				block_value = ""

			else:
				block_head = task_data[i]
				block_value = ""	

		else:
			block_value += task_data[i]

		if i == lenght-1 :
			updateCurrentValue(block_head, block_value)
			print block_head,block_value

def getDataFromTask():

	global TASK_QUEUE
	while True:

		while not TASK_QUEUE.empty():
		    decodeFromTaskQueue(TASK_QUEUE.get())

def monitor():
	global ACCELERATOR,BRAKE,CURRENT_SPEED,CURRENT_GEAR,CURRENT_WHEEL_ANGLES
	while True:
		print 'acc', ACCELERATOR, 'brk', BRAKE, 'spd', CURRENT_SPEED, 'gear', CURRENT_GEAR, 'ang', CURRENT_WHEEL_ANGLES
		time.sleep(0.3)
if __name__ == '__main__':
	print "Start Server !! "

	SystemCommand("start")

	# Event 
	# phone_event = threading.Event()
	# SIM_event = threading.Event()

	# Socket Part
	main_socket_thread = threading.Thread(name="Main_Socket_Thread", target=MainSocket)
	main_socket_thread.setDaemon(True)


	driver_control_socket_thread = threading.Thread(name="Driver_Control_Socket_Thread", target=DriverControlSocket)
	driver_control_socket_thread.setDaemon(True)

	main_socket_thread.start()
	driver_control_socket_thread.start()

	# Car System Part
	car_sys_update_data_driven_thread = threading.Thread(name = "Car_System_UpdateData_Driven", target=getDataFromTask)
	car_sys_cal_speed_driven_thread = threading.Thread(name = "Car_System_CalSpeed_Driven", target =CurrentSpeedControl)
	car_sys_motor_driven_thread = threading.Thread(name="Car_System_Motor_Driven", target=MotorController)
	car_sys_servo_driven_thread = threading.Thread(name="Car_System_Servo_Driven", target=ServoController)
	# car_sys_gear_control_thread = threading.Thread("Car_System_Gear_Control", target=GeearController)

	car_sys_update_data_driven_thread.start()
	car_sys_cal_speed_driven_thread.start()
	car_sys_motor_driven_thread.start()
	car_sys_servo_driven_thread.start()
	
	monitor_thread = threading.Thread(target = monitor)
	monitor_thread.start()


	# Append Thread to THREAD_POOL
	# THREAD_POOL.append(car_sys_motor_driven_thread)
	# THREAD_POOL.append(car_sys_servo_driven_thread)
	# THREAD_POOL.append(main_socket_thread)
	# THREAD_POOL.append(driver_control_socket_thread)


class DeviceSocket(threading.Thread):
	

	def __init__(self, conn, name, event=threading.Event()):
		threading.Thread.__init__(self)
		self._name = name
		self.driver_sock = conn
		self.driver_event = threading.Event()

	def handleCommandSocket():
		while True:
			cmd = self.command_sock.recv(1024)
			commandRequest(command_sock, cmd)

	def setDriverEvent(self, event):
		self.driver_event = event

	def getEvent(self):
		return self.driver_event

	def setCommandSocket(conn, id_code):
		self.command_sock = conn, code

	def commandSocket():
		return self.command_sock

	def setDriverSocket(conn):
		self.driver_sock = conn

	def driverSocket(self):
		return self.driver_sock

	def setId(self, Id):
		self._Id = Id

	def getId(self):
		return self._Id

	def getName(self):
		return self._name

	def run(self):
		print "starting with ", self._name
		try:
			while True:
				self.driver_event.wait()
				raw_data = self.driver_sock.recv(1024)
				logging.debug("Receive data from %r", self.getName())

				decode(raw_data)
				print raw_data
		except Exception as e:
			print "Disconenct by", self.getName(), e