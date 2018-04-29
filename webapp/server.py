import socket              
from threading import Thread
import tkinter
             # Now wait for client connection.
BUFSIZ = 1024             

def accept_incoming_connections(server):
	while True:
	   client, addr = server.accept()     # Establish connection with client.
	   print 'Got connection from', addr
	   Thread(target=receive, args=(client,)).start() 
	   break

def receive(client):
    while True:
        try:
            msg = client.recv(BUFSIZ).decode("utf8")
            msg_list.insert(tkinter.END, msg)
        except OSError:  
            break



if __name__ == '__main__':
	server = socket.socket()         
	host = socket.gethostname() 
	port = 12345   
	server.bind((host, port))        # Bind to the port
	server.listen(5) 
	print "Accepting connections at " + host
	accept_incoming_connections(server)  
	# accepted incoming connedctions
	top = tkinter.Tk()
	top.title("Chatter")

	messages_frame = tkinter.Frame(top)
	my_msg = tkinter.StringVar()  # For the messages to be sent.
	my_msg.set("Type your messages here.")
	scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
	# Following will contain the messages.
	msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
	scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
	msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
	msg_list.pack()
	messages_frame.pack()

	entry_field = tkinter.Entry(top, textvariable=my_msg)
	entry_field.pack()
	send_button = tkinter.Button(top, text="Send", command=send)
	send_button.pack()
	top.protocol("WM_DELETE_WINDOW", on_closing)
	tkinter.mainloop()