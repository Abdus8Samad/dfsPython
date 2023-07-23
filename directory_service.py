# directory service
import os
import csv      #To work with csv file
import sys
from random import random
from socket import *

serverPort = 9090
server_A_port = 12001
server_B_port = 12002
server_C_port = 12003
server_default_address = "localhost"   # address for every server for development
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(10)
print ('DIRECTORY SERVICE is ready to receive...')
curr_path = os.path.dirname(os.path.realpath(sys.argv[0]))      # get path of current workspace

def check_mappings(client_msg, list_files):

	filename = client_msg.split('|')[0]
	RW = client_msg.split('|')[1]

	with open("file_mappings.csv",'rt') as infile:        # open the .csv file storing the mappings
		d_reader = csv.DictReader(infile, delimiter=',')    # read file as a csv file, taking values after commas
		header = d_reader.fieldnames    	# skip header of csv file
		file_row = ""
		ct = 0
		for row in d_reader:
			user_filename = row['user_filename']
			actual_filename = row['actual_filename'] # get actual filename (eg. file123.txt)
			primary_copy = row['primary']

			if list_files == False:
				# use the dictionary reader to read the values of the cells at the current row
				name_match = (user_filename == filename or actual_filename == filename)
				if name_match and RW == 'w':		# check if file inputted by the user exists	(eg. file123)
					print("WRITING")
					server_addr = row['server_addr']			# get the file's file server IP address
					server_port = row['server_port']			# get the file's file server PORT number

					print("actual_filename: " + actual_filename)
					print("server_addr: " + server_addr)
					print("server_port: " + server_port)

					return actual_filename + "|" + server_addr + "|" + server_port	# return string with the information on the file

				elif name_match and RW == 'r' and primary_copy == 'no':
					print("READING")
					server_addr = row['server_addr']			# get the file's file server IP address
					server_port = row['server_port']			# get the file's file server PORT number

					print("actual_filename: " + actual_filename)
					print("server_addr: " + server_addr)
					print("server_port: " + server_port)

					return actual_filename + "|" + server_addr + "|" + server_port	# return string with the information on the file

			elif ct % 2 == 0:
				file_row = file_row + actual_filename +  "\n"		# append filename to return string
			ct += 1
		if list_files == True:
			return file_row
	# if file does not exist return None
	return None

def create_mapping(filename):
	user_filename, _ = filename.split('.')
	mapping = user_filename + ',' + filename + ',' + server_default_address

	server_for_reading = None
	if(round(random(), 0) == 0):  # for now selecting b or c randomly for reading
		server_for_reading = server_B_port
	else:
		server_for_reading = server_C_port

	for_writing = mapping + ',' + str(server_A_port) + ',' + 'yes\n'
	for_reading = mapping + ',' + str(server_for_reading) + ',' + 'no\n'
	file = open("file_mappings.csv", 'a+')
	file.write(for_writing + for_reading)
	return "MAPPING_CREATED"

def create_file(filename):
	map = create_mapping(filename)
	print(map)
	main_server_socket = socket(AF_INET, SOCK_STREAM)
	main_server_socket.connect((server_default_address, server_A_port))
	msg = "CREATE" + "|" + filename
	main_server_socket.send(msg.encode())
	res = main_server_socket.recv(1024)
	main_server_socket.close()
	return res

def main():
	while 1:
		connectionSocket, addr = serverSocket.accept()

		response = ""
		recv_msg = connectionSocket.recv(1024)
		recv_msg = recv_msg.decode()

		if "LIST" not in recv_msg:
			response = check_mappings(recv_msg, False)		# check the mappings for the file
			if "CREATE" in recv_msg:
				if response is not None:
					response = "FILE_ALREADY_EXISTS"
				else:
					response = create_file(recv_msg.split("|")[0])
		elif "LIST" in recv_msg:
			response = check_mappings(recv_msg, True)
		
		if response is not None:
			response = str(response)
			print("RESPONSE: \n" + response)
			print("\n")
		else:
			response = "FILE_DOES_NOT_EXIST"
			print("RESPONSE: \n" + response)
			print("\n")

		connectionSocket.send(response.encode())	# send the file information or non-existance message to the client
			
		connectionSocket.close()


if __name__ == "__main__":
	main()