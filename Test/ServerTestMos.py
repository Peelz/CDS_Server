import socket
import threading

IP = "192.168.137.1"
PORT1 = 7769
PORT2 = 7789


def readPort1():
	while 1:

		data1 = clientsocket1.recv(1024)
		print data1
def readPort2():
	while 1:
		
		data2 = clientsocket2.recv(1024)
		print data2

    # r='REceieve'
    # clientsocket.send(r.encode())


if __name__ == '__main__':
	print "Start Server !! "
	# global IP, PORT1, PORT2, auth_message

	COMMAND_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	COMMAND_SERVER.bind((IP, PORT1))
	COMMAND_SERVER.listen(3)
	(clientsocket1, address1) = COMMAND_SERVER.accept()

	DRIVER_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	DRIVER_SERVER.bind((IP, PORT2))
	DRIVER_SERVER.listen(3)
	(clientsocket2, address2) = DRIVER_SERVER.accept()

	#read and sent
	readPort1 = threading.Thread(name = "Read_Port1", target = readPort1)
	readPort2 = threading.Thread(name = "Read_Port2", target = readPort2)

	readPort1.start()
	readPort2.start()