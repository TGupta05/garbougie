import socket              
from threading import Thread
import Tkinter as tkinter
import sys



if __name__ == "__main__":
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_address = (sys.argv[1], 12342)
	client.connect(server_address)	
	client.send(bytes("metal"))
	while True:
		received = client.recv(60)#number of bytes recived
		print received
		break

    #welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
   # client.send("welcome")

