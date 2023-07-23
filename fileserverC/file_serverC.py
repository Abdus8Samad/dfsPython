# file server
from socket import *
import _thread
import sys
import os
from time import sleep

server_addr = "localhost"
server_port = 12003
server_socket = socket(AF_INET,SOCK_STREAM)
server_socket.bind((server_addr, server_port))
server_socket.listen(10)
curr_path = os.path.dirname(os.path.realpath(sys.argv[0]))
print ('FILE SERVER C is ready to receive...')

file_version_map = {}
read_count = 0

def read_write(filename, RW, text, file_version_map):
	global read_count
	if RW == "r":	# if read request
		read_count += 1
		print(" ----------- ", read_count, " users reading on file server C -----------\n")
		if os.stat(curr_path + "\\" + filename).st_size != 0:
			file = open(curr_path + "\\" + filename, RW)
			text_in_file = file.read()		# read the file's text into a string
			if filename not in file_version_map:
				file_version_map[filename] = 0
			# sleep(6.5)
			read_count -= 1
			print(" ----------- ", read_count, " users reading on file server C -----------\n");
			return (text_in_file, file_version_map[filename])
		else:
			empty_msg = "EMPTY_FILE"
			read_count -= 1
			print(" ----------- ", read_count, " users reading on file server C -----------\n")
			return (empty_msg, -1)


	elif RW == "a+":	# if write request

		if filename not in file_version_map:
			file_version_map[filename] = 0		# if empty (ie. if its a new file), set the version no. to 0
		else:
			file_version_map[filename] = file_version_map[filename] + 1		# increment version no.

		file = open(curr_path + "\\" + filename, RW)
		file.write(text)

		#replicate(text)

		print("FILE_VERSION: " + str(file_version_map[filename]))
		return ("Success", file_version_map[filename])


def send_client_reply(response, RW, connection_socket):

	if response[0] == "Success":
		reply = "File successfully written to..." + str(response[1])

		print("Sending file version " + str(response[1]))
		connection_socket.send(reply.encode())
		#print ("Sent: " + reply)

	elif response[1] != -1 and RW == "r":
		connection_socket.send(response[0].encode())
		#print ("Sent: " + reply)

	elif response[1] == -1: 
		reply = response[0]
		connection_socket.send(reply.encode())
		#print ("Sent: " + reply)
	
def handle_client(connection_socket):
	recv_msg = connection_socket.recv(1024)
	recv_msg = recv_msg.decode()
	if (recv_msg != "") and ("CHECK_VERSION" not in recv_msg) and ("REPLICATE" not in recv_msg) and ("CREATE" not in recv_msg):
		# parse the message

		filename = recv_msg.split("|")[0]	# file path to perform read/write on
		print ("Filename: " + filename)
		RW = recv_msg.split("|")[1]			# whether its a read or write
		print ("RW: " + RW)
		text = recv_msg.split("|")[2]		# the text to be written (this text is "READ" for a read and is ignored)
		print ("TEXT: " + text)

		response = read_write(filename, RW, text, file_version_map)	# perform the read/write and check if successful
		send_client_reply(response, RW, connection_socket)		# send back write successful message or send back text for client to read

	elif "CHECK_VERSION" in recv_msg:
		client_filename = recv_msg.split("|")[1]			# parse the version number to check
		print("Version check on " + client_filename + "\n")
		if client_filename not in file_version_map:
			file_version_map[client_filename] = 0
		file_version = str(file_version_map[client_filename])
		connection_socket.send(file_version.encode())

	elif "REPLICATE" in recv_msg:
		rep_filename = recv_msg.split("|")[1]
		rep_text = recv_msg.split("|")[2]
		rep_version = recv_msg.split("|")[3]

		file_version_map[rep_filename] = int(rep_version)

		f = open(curr_path + "\\" + rep_filename, 'w')
		f.write(rep_text)
		f.close()
		print(rep_filename + " successfully replicated on server C...\n")

	elif "CREATE" in recv_msg:
		rep_filename = recv_msg.split("|")[1]
		file_version_map[rep_filename] = 0
		open(curr_path + "\\" + rep_filename, 'a+')
		print(rep_filename + " successfully created on server C...\n")

def main():
	while 1:
		connection_socket, _ = server_socket.accept()
		_thread.start_new_thread(handle_client, (connection_socket, ))

	connection_socket.close()

if __name__ == "__main__":
	main()