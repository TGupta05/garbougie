import socket
import Tkinter
from Tkinter import Frame, Tk, BOTH, Text, Menu, END
import threading
import tkFont

top = Tkinter.Tk()
top.config(bg="white")
top.geometry("1500x1000")
top.title("GUI")

s = socket.socket()
rueda = dict()

class Looping(object):
	def __init__(self):
		helv100 = tkFont.Font(family='Helvetica',size=100, weight='bold')
		self.B_start = Tkinter.Button(top, text ="Start",font=helv100, height = 5, bd = 0, command = self.yay)
		self.B_start.pack(fill=BOTH, expand=1)
		# self.B_stop = Tkinter.Button(top, text ="Stop",font=helv100, command = self.button_stop)
		# self.B_stop.pack(fill=BOTH, expand=1)
		self.isRunning = True 

	def back2(self):
		self.w.destroy()
		self.y.destroy()
		self.plastic.destroy()
		self.compost.destroy()
		self.metal.destroy()
		self.trash.destroy()
		self.yay()
	  
	def yay(self):   
		print " in here"     
		global recived
		helv100 = tkFont.Font(family='Helvetica',size=100, weight='bold')  
		self.B_start.destroy() 
		print "here"
		self.show = Tkinter.Label(top, text = "Waiting for Garbougie...", font =helv100)
		self.show.pack()
		top.update()

		self.server = socket.socket()
		host = socket.gethostname() 
		port = 12342
		self.server.bind((host, port))        # Bind to the port
		self.server.listen(5) 
		while True:
			print "waiting"
			client, addr = self.server.accept()     # Establish connection with client
			break
		while self.isRunning == True:
			recived = client.recv(60)#number of bytes recived
			print recived
			break
		else:
			 print "Not connected to the wheel";
		helv100 = tkFont.Font(family='Helvetica',size=100, weight='bold')  
		self.show.destroy()
		self.w = Tkinter.Label(top, text = "Prediction is: " + recived, font =helv100)
		top.update()
		helv10 = tkFont.Font(family='Helvetica',size=20, weight='bold')  
		helv50 = tkFont.Font(family='Helvetica',size=50, weight='bold')  

		self.y = Tkinter.Label(top, text = "What is the real category? ", font =helv50)
		self.w.pack()
		self.y.pack()
		self.plastic = Tkinter.Button(top, text ="plastic",font=helv10 , command = self.back2)
		self.compost = Tkinter.Button(top, text ="compost",font=helv10,   command = self.back2)
		self.metal = Tkinter.Button(top, text ="metal",font=helv10, command = self.back2)
		self.trash = Tkinter.Button(top, text ="trash",font=helv10,  command = self.back2)
		self.plastic.pack()
		self.compost.pack()
		self.metal.pack()
		self.trash.pack()

	def button_stop(self):
		l.isRunning = False       
		self.server.close()
		print "Socket connection breaked"

l=Looping()
top.mainloop()
# import socket              
# from threading import Thread
# import Tkinter as tkinter
#              # Now wait for client connection.
# BUFSIZ = 1024             

# def accept_incoming_connections(server):
# 	while True:
# 	   print 'Got connection from', addr
# 	   Thread(target=receive, args=(client,)).start() 
# 	   break

# def receive(client):
#     while True:
#         try:
#             msg = client.recv(BUFSIZ).decode("utf8")
#             print msg
#             #msg_list.insert(tkinter.END, msg)
#         except OSError:  
#             break



# if __name__ == '__main__':
# 	# accepted incoming connedctions
# 	server = socket.socket()         
# 	host = socket.gethostname() 
# 	port = 12345
# 	server.bind((host, port))        # Bind to the port
# 	server.listen(5) 
# 	print "Accepting connections at " + host
# 	accept_incoming_connections(server)  
# 	top = tkinter.Tk()
# 	top.title("Garbougie")
# 	# top.geometry('300x100')
# 	# top.pack()
# 	messages_frame = tkinter.Frame(top)
# 	#msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)

# 	# my_msg = tkinter.StringVar()  # For the messages to be sent.
# 	# my_msg.set("Type your messages here.")
# 	# scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# 	# Following will contain the messages.
# 	# msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
# 	# scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
# 	# msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
# 	# msg_list.pack()
# 	# messages_frame.pack()

# 	# entry_field = tkinter.Entry(top, textvariable=my_msg)
# 	# entry_field.pack()
# 	send_button = tkinter.Button(top, text="Send")
# 	send_button.pack()
# 	#top.protocol("WM_DELETE_WINDOW", on_closing)
# 	tkinter.mainloop()

