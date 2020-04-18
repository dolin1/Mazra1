import sys
import os
import socket
import getopt
import threading
import subprocess

#variables
listen = False
command = False
upload = False
pScan=False
nScan=False
cont = True
execute =""
host =""
upload_dest =""
port=0

def usage():
	print "-" * 100
	print "Mazra Net Tools"
	print "*" * 100
	print "-t --target     ============================= Target [host]"
	print "-p --port       ============================= Target [port]"
	print "-l --listen     ============================= Listen On [Host]:[Port] for incoming connections"
	print "-e --execute    ============================= Execute the given file after receiving a connection"
	print "-c --commShell  ============================= Initiate a Command Shell"
	print "-u --upload     ============================= upload/write a file to the destination you have connected to"
	print "*" * 100
	print "-" * 100


def run_command(runComm):
	runComm=runComm.rstrip()
	try:
		output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
	except:
		output = "Failed to execute command. \r\n"

	return output


def client_sender(buffer):
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		client.connect((host,port))

		if len(buffer):
			client.send(buffer)
		while True:
			recv_len = 1
			response = ""
			while recv_len:
				data = client.recv(4096)
				recv_len = len(data)
				response+= data

				if recv_len < 4096:
					break
		print response

		buffer = raw_input("")
		buffer += "\n"

		client.send(buffer)
	except:
		print "[*] Exception! Exiting"

		client.close()


def server_loop():
	#specify global variable
	global host
	socky = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	if not len(host):
		host ="0.0.0.0"
	server =socket.socket(socket.AF_INET , socket.SOCK_STREAM)
	server.bind((host,port))
	server.listen(8)

	print "Listening to Socket " + host + ":" + str(port)
	while True:
		client_socket, addr = server.accept()
		#client handler thread
		client_thread =threading.Thread(target=client_handler, args=(client_socket,))
		client_thread.start()

def client_handler(client_socket):
	#specify instances of these variables are global
	global upload_dest
	global execute
	global command
	
	if len(upload_dest):
		file_buffer = ""
		while True:
			data =client_socket.recv(1024)

			if not data:
				break
			else:
				file_buffer += data
		try:
			file_descriptor = open(upload_dest, "wb")
			file_descriptor.write(file_buffer)
			file_descriptor.close()
			client_socket.send("Successfully saved file to %s\r\n" % upload_dest)
		except:
			client_socket.send("Failed to save file to %s\r\n" % upload_dest)
	if len(execute):
		#run command
		output = run_command(execute)
		client_socket.send(output)
	if command:
		while True:
			# show command prompt
			client_socket.send("<Mazra:#> ")
			#now we receive until we see a line feed (enter key)
			cmd_buffer=""
			while "\n" not in cmd_buffer:
				cmd_buffer += client_socket.recv(1024)
			response = run_command(cmd_buffer)
			client_socket.send(response)
if not len(sys.argv[1:]):
	usage()

try:
	opts, args= getopt.getopt(sys.argv[1:],"hle:t:p:cux:n:",["help","listen","execute","target","port", "command","upload","portscan","netscan"])
	for o,a in opts:
		if o in ("-h","--help"):
			usage()
		elif o in ("-t", "--target"):
			host=a
			print " Target Host " + host + " set "
		elif o in ("-p","--port"):
			port=int(a)
			print " Target Port " + str(port) + " set"
		elif o in ("-u","--upload"):
			upload_dest = a
			print "Upload File " + a
		elif o in ("-e","--execute"):
			execute=a
		elif o in ("-c","--command"):
			commShell=True
			print "Command Shell Mode Enabled"
		elif o in ("-l","--listen"):
			listen=True
			print "Starting Listener"
		elif o in ("-x","--portscan"):
			pScan=True
			result=a
			if(result=='*'):
				scanRange=6000
			else:
				scanRange= int(a)
			print "Starting Port Scan"
		elif o in ("-n","--netscan"):
			nScan=True
			subset="1-254"
			a.strip()
			if(a=='*'):
				scanRange=254
			else:
				scanRange=int(a)
			print "Initiating Enumeration"
		else:
			assert False, "Unhandled Option"
	if not listen and not pScan and not nScan  and len(host) and port > 0:
		buffer = sys.stdin.read()
		client_sender(buffer)
	if listen:
		server_loop()

	if pScan:
		print "-" * 60
		print "Please Wait..."
		print "-" * 60
		remoteServerIP=socket.gethostbyname(host)
		print "Open Ports: "
		for nPort in range(1,scanRange):
                	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
               		result = sock.connect_ex((remoteServerIP,nPort))
                	
			if result==0:
				print "Port {}:   ".format(nPort)
			sock.close()

               	print  'Scanning Completed '
	if nScan:
		print "-" * 60
	        print "Please Wait, Enumerating...."
        	print "-" * 60
		
		if len(host):
			subnets=host.split(".")
            		for octet in range(1,scanRange):
                		pingIP = subnets[0]+"."+subnets[1]+"."+subnets[2] + "."+str(octet)
                		pingCmmd='ping -c 5 '+ pingIP
                		result = os.system(pingCmmd)
        		banner ="Enumeration Complete "

except getopt.GetoptError as err:
	print str(err)
	usage()
except KeyboardInterrupt:
        print "You pressed CTRL+C"
        sys.exit()

except socket.gaierror:
        print "Hostname could not be resolved. Abort"
        sys.exit()

except socket.error:
       	print "Couldn't connect to server"
        sys.exit()



