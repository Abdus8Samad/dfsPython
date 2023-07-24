# file server
from socket import *
import os, sys

primary_serverddr = "localhost"
server_port = 12001
server_socket = socket(AF_INET,SOCK_STREAM)
server_socket.bind((primary_serverddr, server_port))
server_socket.listen(10)
curr_path = os.path.dirname(os.path.realpath(sys.argv[0]))
print ('PRIMARY SERVER is ready to receive...')

file_version_map = {}

def replicate(filename, action):

	f = open(curr_path + "\\" + filename, 'r')
	text = f.read()
	f.close()

	msg = action + "|" + filename + "|" + text + "|" + str(file_version_map[filename])

	port = 12002
	server_ip = 'localhost'
	print("Replicating to replica_server_1")
	replicate_socket = socket(AF_INET, SOCK_STREAM)
	replicate_socket.connect((server_ip,port))
	replicate_socket.send(msg.encode())
	replicate_socket.close()

	port = 12003
	server_ip = 'localhost'
	print("Replicating to replica_server_2")
	replicate_socket = socket(AF_INET, SOCK_STREAM)
	replicate_socket.connect((server_ip,port))
	replicate_socket.send(msg.encode())
	replicate_socket.close()

def read_write(filename, RW, text, file_version_map):
	if RW == "r":	# if read request
		try:
			file = open(curr_path + "\\" + filename, RW)	
			text_in_file = file.read()		# read the file's text into a string
			if filename not in file_version_map:
				file_version_map[filename] = 0
			return (text_in_file, file_version_map[filename])			
		except IOError:				# IOError occurs when open(curr_path + "\\" + filepath,RW) cannot find the file requested
			print (filename + " does not exist in directory\n")
			return (IOError, -1)

	elif RW == "a+":	# if write request
		if filename not in file_version_map:
			file_version_map[filename] = 0		# if empty (ie. if its a new file), set the version no. to 0
		else:
			file_version_map[filename] = file_version_map[filename] + 1		# increment version no.
			print("Updated " + filename + " to version " + str(file_version_map[filename]))

		file = open(curr_path + "\\" + filename, RW)
		file.write(text)

		print("FILE_VERSION: " + str(file_version_map[filename]))
		return ("Success", file_version_map[filename])


def send_client_reply(response, RW, connection_socket):
	if response == "FILE_CREATED_SUCCESSFULLY\n":
		connection_socket.send(response.encode())
	elif response[0] == "Success":
		reply = "File successfully written to..." + str(response[1])
		print("Sending file version " + str(response[1]))
		connection_socket.send(reply.encode())
	elif response[0] is not IOError and RW == "r":
		connection_socket.send(response.encode())

	elif response[0] is IOError: 
		reply = "FILE_DOES_NOT_EXIST\n"
		connection_socket.send(reply.encode())

def main():
	while 1:
		response = ""
		connection_socket, addr = server_socket.accept()

		recv_msg = connection_socket.recv(1024)
		recv_msg = recv_msg.decode()

		if "CREATE" in recv_msg:
			filename = recv_msg.split("|")[1]
			open(curr_path + "\\" + filename, 'a+')
			file_version_map[filename] = 0
			replicate(filename, "CREATE")
			send_client_reply("FILE_CREATED_SUCCESSFULLY\n", 'a+', connection_socket)
		elif recv_msg != "" and "CHECK_VERSION" not in recv_msg:
			# parse the message

			filename = recv_msg.split("|")[0]	# file path to perform read/write on
			print ("Filename: " + filename)
			RW = recv_msg.split("|")[1]			# whether its a read or write
			print ("RW: " + RW)
			text = recv_msg.split("|")[2]		# the text to be written (this text is "READ" for a read and is ignored)
			print ("TEXT: " + text)

			response = read_write(filename, RW, text, file_version_map)	# perform the read/write and check if successful
			send_client_reply(response, RW, connection_socket)		# send back write successful message or send back text for client to read

			if RW == 'a+':
				replicate(filename, "REPLICATE")


		elif "CHECK_VERSION" in recv_msg:
			client_filename = recv_msg.split("|")[1]			# parse the version number to check
			print("Version check on " + client_filename)
			file_version = str(file_version_map[client_filename])
			connection_socket.send(file_version.encode())


	connection_socket.close()

if __name__ == "__main__":
	main()