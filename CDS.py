# import server_pc 
import socket 
import threading
import time
from time import sleep

# Import global variable
from _global import *
from _embeded import *

# Command Server
class commandSocket(threading.Thread):
	command_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	command_sock.bind((HOST, 7769))
	command_sock.listen(2)

	def __init__(self):
		threading.Thread.__init__(self)
		self.setDaemon(True)


	def run(self):
		while True:
			conn, addr = self.command_sock.accept()
			logging.debug( "Main socket connect from %r", addr)
			self.commandSocketRegistrar(conn,addr)

	def commandSocketRegistrar(self, conn, addr):
		global PHONE_CMD, SIMULATOR_SET_CMD
		auth_data = conn.recv(1024)
		#print 'auth_data' + auth_data # add

		if auth_data == "-a PHONE":
			PHONE_CMD = conn
			new_thread = threading.Thread(target=self.commandSocketReceiver, args=(conn, addr))

			new_thread.start()

		elif auth_data == "-a SIMULATOR_SET" :
			SIMULATOR_SET_CMD = conn

			new_thread = threading.Thread(target=self.commandSocketReceiver, args=(conn, addr))
			new_thread.start()

		else:
			conn.close()
			print addr," connection failed to Authenticate"			

	def commandSocketReceiver(self, conn, addr):
		try:
			while True:
				raw_data = conn.recv(1024)
				#print 'connRecMainSock' + raw_data # add
				command(conn, raw_data)
				
		except Exception as e:
			logging.debug("Command Socket Disconnected from %r %r", addr, e)
			global CURRENT_SPEED,CURRENT_GEAR,CURRENT_WHEEL_ANGLES,ACCELERATOR,BRAKE
			#set car defult value  
			CURRENT_SPEED = 0
			CURRENT_GEAR = "N"
			CURRENT_WHEEL_ANGLES = 90
			ACCELERATOR = 0
			BRAKE = 0

class DeviceSocket(threading.Thread):

	def __init__(self, conn, device_name, event=threading.Event()):
		threading.Thread.__init__(self)
		self._device_name = device_name
		self.driver_sock = conn
		self.setDaemon(True)
		self.driver_event = threading.Event()

	def setDriverEvent(self, event):
		self.driver_event = event

	def getEvent(self):
		return self.driver_event

	def setCommandSocket(conn, id_code):
		self.command_sock = conn, code

	def setDriverSocket(conn):
		self.driver_sock = conn

	def getDriverSocket(self):
		return self.driver_sock

	def getId(self):
		return self._Id

	def getDeviceName(self):
		return self._device_name

	def run(self):
		print self.getDeviceName(), "Start"

		try:
			while True:
				self.driver_event.wait()
				raw_data = self.driver_sock.recv(1024)
				#logging.debug("Receive data from %r", self.getName())
				#print 'self drive' + raw_data # add
				decode(raw_data)
				
		except Exception as e:
			lock = threading.Lock()

			lock.acquire()
			if self.getDeviceName() == "PHONE":
				global PHONE_DRIVER, PHONE_CMD
				PHONE_CMD.close()
				PHONE_DRIVER.getDriverSocket.close()
				PHONE_DRIVER = None ;
				PHONE_CMD = None ; 
			else:
				global SIMULATOR_SET_CMD, SIMULATOR_SET_DRIVER
				SIMULATOR_SET_DRIVER = None ;
				SIMULATOR_SET_CMD = None ;

			print "Disconenct by", self.getDeviceName(), 
			print e
			lock.release()

"""
Return Current Gear
"""			
def getCurrentGear() :
	global CURRENT_GEAR 
	return CURRENT_GEAR

"""
Return has Simset is connected 
"""
def getSimulatorStatus() :
	global SIMULATOR_SET_DRIVER

	if SIMULATOR_SET_DRIVER != None :
		return "1"
	else:	
		return "0"

"""
Driver Control Socket
"""
def DriverControlSocket():
	global CONTROL_MODE, PHONE_DRIVER, CONTROL_MODE, SIMULATOR_SET_DRIVER, PHONE_DRIVER


	driver_control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	driver_control_sock.bind((HOST, 7789))
	driver_control_sock.listen(2)

	try :

		while True:
			conn, addr = driver_control_sock.accept()
			logging.debug( "Driver socket connect from %r", addr)
			id_mess = conn.recv(1024)

			if id_mess == "PHONE":
								
				PHONE_DRIVER = DeviceSocket(conn, "PHONE")
				try:
					PHONE_CMD.send("-s "+getSimulatorStatus() )
					PHONE_CMD.send("-cg "+getCurrentGear() )
				except Exception as e:

					print "Driver control cant send to command socket", e


				#Have SIMSET connect
				if SIMULATOR_SET_DRIVER != None :
					PHONE_CMD.send("-s "+getSimulatorStatus() )
					PHONE_CMD.send("-cg "+getCurrentGear() )
					PHONE_DRIVER.getEvent().clear()
		
				# No SIMSET connect
				else:
					CONTROL_MODE = 0
					PHONE_DRIVER.getEvent().set()

				PHONE_DRIVER.start()


			elif id_mess == "SIMULATOR_SET":
				SIMULATOR_SET_DRIVER = DeviceSocket(conn, "SIMULATOR_SET")	

				# No Phone connect
				if PHONE_DRIVER == None:
					SIMULATOR_SET_DRIVER.getEvent().set()
					CONTROL_MODE = 1

				# Have Phone connnect
				else:
					PHONE_CMD.send("-s "+getSimulatorStatus() )
					PHONE_CMD.send("-cg "+getCurrentGear() )

					SIMULATOR_SET_DRIVER.getEvent().clear()

				SIMULATOR_SET_DRIVER.start()

			else:
				conn.close()

	except Exception as e :
		raise e

def command(conn, message):
	command = message.split()[0] 

	if command == '-cg':
		changeGear(message.split()[1] )

	elif command == '-cm':
		changeControlmode(message.split()[1])


def changeControlmode(cmd):
	global CONTROL_MODE, PHONE_DRIVER, CONTROL_MODE, SIMULATOR_SET_DRIVER

	
	if cmd == "PH" and CONTROL_MODE != 0 and PHONE_DRIVER != None:
		CONTROL_MODE = 0
		PHONE_CMD.send("-cm PH")

		SIMULATOR_SET_DRIVER.getEvent().clear()
		PHONE_DRIVER.getEvent().set()
		print "Change control mode to", cmd

	elif cmd == "SIM" and CONTROL_MODE != 1 and SIMULATOR_SET_DRIVER != None:
		CONTROL_MODE = 1
		PHONE_CMD.send("-cm SIM")

		SIMULATOR_SET_DRIVER.getEvent().set()
		PHONE_DRIVER.getEvent().clear()
		print "Change control mode to", cmd

	else :

		print "Control mode not change"

	
def socketResponse(conn, message):
	try:
		conn.send(message)
	except Exception as e:
		logging.debug("Command response Failed %r",e)


		
def Driving():
	if DRIVER != None :
		new_thread = threading.Thread(name="Driver", target=MotorControl)
		THREAD_POOL.append(new_thread)
	else:
		CURRENT_SPEED = DEFALUT_SPEED 


def checkIntToStr(arg):
	try:
		return int(arg)
	except Exception as e:
		return False
"""
Set Current Speed 
"""
def updateCurrentValue (in_head,in_data):

	try: 
		data = int(in_data)

		if in_head == 'a': 					#update current accelerator
			global ACCELERATOR
			ACCELERATOR = data 		

		elif in_head == 'b': 					#update current brake
			global BRAKE
			BRAKE = data
		
		elif in_head == 't': 					#update current degree
			global CURRENT_WHEEL_ANGLES
			CURRENT_WHEEL_ANGLES = data 

	except :
		pass

	

def CurrentSpeedControl():
	global CURRENT_SPEED,ACCELERATOR,BRAKE,CURRENT_GEAR
	while True:
		
		
		if CURRENT_GEAR == 'D':
			defaultSpeed = 5.0
			forwardMaxSpeed = 160.0
			timeDivide = 200.0
			maxAcc = 8.21 #0-100 12.17sec  +8.21km/s
			maxBrk = 14.28 # 100-0 7sec -14.28km/s
			decreaseSpeed = 3.0/timeDivide		#-3km/s

			maxSpeedCurrentAcc = (ACCELERATOR/100.0)*forwardMaxSpeed

			brake_to_speed = ((BRAKE/100.0)*maxBrk)/timeDivide 
			
			if CURRENT_SPEED <= defaultSpeed and ACCELERATOR == 0 and BRAKE == 0: 
				CURRENT_SPEED = CURRENT_SPEED + decreaseSpeed
					
			else:
				
				if CURRENT_SPEED < maxSpeedCurrentAcc:
					accelerator_to_speed = ((ACCELERATOR/100.0)*maxAcc)/timeDivide
				elif CURRENT_SPEED >= maxSpeedCurrentAcc:
					accelerator_to_speed = 0.0

				if ACCELERATOR != 0 or BRAKE != 0:
					spd = CURRENT_SPEED + accelerator_to_speed - brake_to_speed 
				else:
					spd = CURRENT_SPEED + accelerator_to_speed - brake_to_speed - decreaseSpeed

				if spd >= forwardMaxSpeed:
					CURRENT_SPEED = forwardMaxSpeed
				elif spd < 0:
					CURRENT_SPEED = 0
				elif spd <= defaultSpeed and BRAKE == 0:
					CURRENT_SPEED = defaultSpeed
				else:
					CURRENT_SPEED = spd
			
		elif CURRENT_GEAR == 'R':
			defaultSpeed = 5.0
			reverseMaxSpeed = 20.0					
			timeDivide = 200.0
			maxAcc = 8.21 #0-100 12.17sec  +8.21km/s
			maxBrk = 14.28 # 100-0 7sec -14.28km/s
			decreaseSpeed = 3.0/timeDivide		#-3km/s

			maxSpeedCurrentAcc = (ACCELERATOR/100.0)*reverseMaxSpeed

			brake_to_speed = ((BRAKE/100.0)*maxBrk)/timeDivide 
			
			if CURRENT_SPEED <= defaultSpeed and ACCELERATOR == 0 and BRAKE == 0: 
				CURRENT_SPEED = CURRENT_SPEED + decreaseSpeed
					
			else:
				
				if CURRENT_SPEED < maxSpeedCurrentAcc:
					accelerator_to_speed = ((ACCELERATOR/100.0)*maxAcc)/timeDivide
				elif CURRENT_SPEED >= maxSpeedCurrentAcc:
					accelerator_to_speed = 0.0
				
				if ACCELERATOR != 0 or BRAKE != 0:
					spd = CURRENT_SPEED + accelerator_to_speed - brake_to_speed 
				else:
					spd = CURRENT_SPEED + accelerator_to_speed - brake_to_speed - decreaseSpeed

				if spd >= reverseMaxSpeed:
					CURRENT_SPEED = reverseMaxSpeed
				elif spd < 0:
					CURRENT_SPEED = 0
				elif spd <= defaultSpeed and BRAKE == 0:
					CURRENT_SPEED = defaultSpeed
				else:
					CURRENT_SPEED = spd
		else:
			CURRENT_SPEED = 0

		# # time.sleep(0.1)


"""
Command Motor By CURRENT_SPEED
"""
def MotorController():
	global CURRENT_GEAR,CURRENT_SPEED
	MaxSpeed = 160.0

	pwmStartRun = 0.20 #Motor begin run
	pwmMaxRun = 0.60
	pwmRange = pwmMaxRun - pwmStartRun

	while True:
		t1 = time.time()
		
		if CURRENT_GEAR == 'D':
			if CURRENT_SPEED == 0:
				board.digital[3].write(0)
			else:

				pwmForword = (CURRENT_SPEED/MaxSpeed * pwmRange) + pwmStartRun
				board.digital[3].write(pwmForword)

		elif CURRENT_GEAR == 'R':
			if CURRENT_SPEED == 0:
				board.digital[5].write(0)
			else:
				pwmReverse= (CURRENT_SPEED/MaxSpeed * pwmRange) + pwmStartRun
				board.digital[5].write(pwmReverse)
			

		elif CURRENT_GEAR == 'P':
			
			board.digital[3].write(0.02)
			

		elif CURRENT_GEAR == 'N':

			board.digital[3].write(0)
		#t2 = time.time()

		# print "time used ", t2-t1

"""
Command Servo By CURRENT_WHEEL_ANGLES
"""
def ServoController():
	global CURRENT_WHEEL_ANGLES
	while True:
		
		left = 75 											#left max degree
		right = 125 										#right max degree
		carDegree = left+(((right-left)*CURRENT_WHEEL_ANGLES)/180)		#cal degree servo
		board.digital[12].write(carDegree)	


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
	if CURRENT_GEAR != value and CURRENT_SPEED == 0 :
		CURRENT_GEAR = value
		response_message = "-cg "+value
		if PHONE_CMD != None:
			PHONE_CMD.send(response_message)
		print "Change gear to ", value

def assignTask(head, value):
	control_head = ['a','t','b']
	if head in control_head:
		TASK_QUEUE.put(head+value)
	# elif head == 'g' :
	# 	changeGear(value)

def decode(income_data):
	__header = ['a','b','t','g']
	block_head = ""
	block_value = ""

	lenght = len(income_data)

	for i in range(lenght):
		if income_data[i] in __header  :
			if block_head != "":
				updateCurrentValue(block_head, block_value)
				
				block_head = income_data[i]
				block_value = ""

			else:
				block_head = income_data[i]
				block_value = ""	

		else:
			block_value += income_data[i]

		if i == lenght-1 :
			updateCurrentValue(block_head, block_value)
			

def decodeFromTaskQueue(task_data): 
	lenght = len(task_data)
	block_value = ""
	for i in range(1, lenght):
		block_value += task_data[i]
	updateCurrentValue(task_data[0], block_value)
	# print task_data[0],block_value


def getDataFromTask():

	global TASK_QUEUE
	while True:

		while not TASK_QUEUE.empty():
		    decodeFromTaskQueue(TASK_QUEUE.get())

# Get Current Phone device is connecting 
def getPhoneClient():
	global PHONE_CMD, PHONE_DRIVER

	if (PHONE_DRIVER or PHONE_CMD) == None:
		return False
	else: 
		return True

# TODO: See current Simulator is connecting 
def getSimClient():
	global SIMULATOR_SET_DRIVER, SIMULATOR_SET_CMD

	if (SIMULATOR_SET_DRIVER or SIMULATOR_SET_CMD) == None:
		return False
	else: 
		return True

def monitor():
	global ACCELERATOR,BRAKE,CURRENT_SPEED,CURRENT_GEAR,CURRENT_WHEEL_ANGLES
	while True:
		print 'acc', ACCELERATOR, 'brk', BRAKE, 'spd', CURRENT_SPEED, 'gear', CURRENT_GEAR, 'ang', CURRENT_WHEEL_ANGLES
		print "Control mode: ",CONTROL_MODE
		print 'Client', PHONE_CMD, PHONE_DRIVER, SIMULATOR_SET_CMD, SIMULATOR_SET_DRIVER
		print "\n"
		time.sleep(2)

if __name__ == '__main__':



	# Socket Part
	command_socket_thread = commandSocket()
	command_socket_thread.setDaemon(True)


	driver_control_socket_thread = threading.Thread(name="Driver_Control_Socket_Thread", target=DriverControlSocket)
	driver_control_socket_thread.setDaemon(True)

	# Car System Part
	# car_sys_update_data_driven_thread = threading.Thread(name = "Car_System_UpdateData_Driven", target=getDataFromTask)
	# car_sys_update_data_driven_thread.setDaemon(True)

	car_sys_cal_speed_driven_thread = threading.Thread(name = "Car_System_CalSpeed_Driven", target =CurrentSpeedControl)
	car_sys_motor_driven_thread = threading.Thread(name="Car_System_Motor_Driven", target=MotorController)
	car_sys_servo_driven_thread = threading.Thread(name="Car_System_Servo_Driven", target=ServoController)

	car_sys_cal_speed_driven_thread.setDaemon(True)
	car_sys_motor_driven_thread.setDaemon(True)
	car_sys_servo_driven_thread.setDaemon(True)

	# car_sys_gear_control_thread = threading.Thread("Car_System_Gear_Control", target=GeearController)

	# Monitor thread  
	monitor_thread = threading.Thread(target = monitor)
	monitor_thread.setDaemon(True)


	# Start System 
	try:
		print acii_text
		print "Start "

		command_socket_thread.start()
		driver_control_socket_thread.start()

		# car_sys_update_data_driven_thread.start()
		car_sys_cal_speed_driven_thread.start()
		car_sys_motor_driven_thread.start()
		car_sys_servo_driven_thread.start()

		monitor_thread.start()

		while True:
			inp = raw_input(">_")
			if inp == "exit":
				raise Exception
			pass

	except KeyboardInterrupt as e:
		logging.debug("Close by Keyboard Interrupt")

	except Exception as e:
		logging.debug("Close by Exception",e)



