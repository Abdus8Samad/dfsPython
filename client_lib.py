from socket import *
import sys
import os
from time import sleep
import os.path

curr_path = os.path.dirname(os.path.realpath(sys.argv[0]))      # get path of current program (client.py)
main_server_IP = 'localhost'
main_server_PORT = 12001
lock_server_IP = 'localhost'
lock_server_PORT = 4040

# creating a socket
def create_socket():
    s = socket(AF_INET, SOCK_STREAM)
    return s

# for sending request to server for writing to the file
def send_write(client_socket, fileserverIP_DS, fileserverPORT_DS, filename , RW, file_version_map, msg):
    if filename not in file_version_map:
        file_version_map[filename] = 0

    elif RW != "r":
        file_version_map[filename] = file_version_map[filename] + 1

    send_msg = filename + "|" + RW + "|" + msg 

    print("Sending version: " + str(file_version_map[filename]))

    client_socket.connect((fileserverIP_DS,fileserverPORT_DS))
    client_socket.send(send_msg.encode())

# for sending request to server for reading the file
def send_read(client_socket, fileserverIP_DS, fileserverPORT_DS, filename , RW, file_version_map, msg, filename_DS, client_id):
    if filename not in file_version_map:
        file_version_map[filename] = 0
        print("REQUESTING FILE FROM FILE SERVER - FILE NOT IN CACHE")
        send_msg = filename + "|" + RW + "|" + msg    
        client_socket.connect((fileserverIP_DS,fileserverPORT_DS))
        client_socket.send(send_msg.encode())
        return False

    send_msg = "CHECK_VERSION|" + filename
    client_socket1 = create_socket()
    client_socket1.connect((fileserverIP_DS,fileserverPORT_DS))
    client_socket1.send(send_msg.encode())
    print ("Checking version...")
    version_FS = client_socket1.recv(1024)    # receive file server version number
    version_FS = version_FS.decode()
    client_socket1.close()
    cache_file = curr_path + "\\cache" + "\\client_cache" + client_id + "\\" + filename_DS  
    print(cache_file)
    if os.path.exists(cache_file) == True and version_FS == str(file_version_map[filename]):
        # read from cache
        print("Versions match, reading from cache...")
        cache(filename_DS, "READ", "r", client_id)
    else:
        print("Versions do not match...")
        print("REQUESTING FILE FROM FILE SERVER...")
        file_version_map[filename] = int(version_FS)
        send_msg = filename + "|" + RW + "|" + msg    
        client_socket.connect((fileserverIP_DS,fileserverPORT_DS))
        client_socket.send(send_msg.encode())
        return False    # didn't go to cache - new version

    return True     # went to cache

def handle_write(filename, client_id, file_version_map):
    # ------ INFO FROM DS ------
    client_socket = create_socket()  # create socket to directory service
    reply_DS = send_directory_service(client_socket, filename, 'w', False)  # request the file info from directory service
    client_socket.close()   # close the connection 

    if reply_DS == "FILE_DOES_NOT_EXIST":
        print(filename + " does not exist on a fileserver")
    else:
        filename_DS = reply_DS.split('|')[0]
        fileserverIP_DS = reply_DS.split('|')[1]
        fileserverPORT_DS = reply_DS.split('|')[2]

        # ------ ACQUIRE LOCK FROM SERVER ------
        failure = False # if failed to acquire lock
        while failure == False:
            locking_socket = create_socket()
            locking_socket.connect((lock_server_IP, lock_server_PORT))
            req = client_id + "_1_" + filename
            locking_socket.send(req.encode())
            res = locking_socket.recv(1024).decode()
            if(res == "TIMEOUT"):
                failure = True
                break
            if(res == "file_granted"):
                break
            print(client_id, " Acquiring Lock for file ", filename)
            sleep(0.1)
            locking_socket.close()
        
        if failure:
            print(client_id, " can't Acquire Lock for file ", filename)
            return "INTERNAL_ERROR_OCCURED"
        
        # ------ ClIENT WRITING TEXT ------
        print ("Write some text...")
        print ("<end> to finish writing")
        print_breaker()
        write_client_input = ""
        while True:
            client_input = sys.stdin.readline()
            if "<end>" in client_input:  # check if user wants to finish writing
                break
            else: 
                write_client_input += client_input
        print_breaker()

        

        # ------ WRITING TO FS ------
        client_socket = create_socket()
        send_write(client_socket, fileserverIP_DS, int(fileserverPORT_DS), filename_DS, "a+", file_version_map, write_client_input) # send text and filename to the fileserver
        #print ("SENT FOR WRITE")
        reply_FS = client_socket.recv(1024)
        reply_FS = reply_FS.decode()
        client_socket.close()

        print (reply_FS.split("...")[0])    # split version num from success message and print message
        version_num = int(reply_FS.split("...")[1]) 
        
        if version_num != file_version_map[filename_DS]:
            print("Server version no changed - updating client version no.")
            file_version_map[filename_DS] = version_num

        # sleep(15)

        # ------ RELEASING THE LOCK ------
        locking_socket = create_socket()
        locking_socket.connect((lock_server_IP, lock_server_PORT))
        req = client_id + "_2_" + filename
        locking_socket.send(req.encode())
        res = locking_socket.recv(1024).decode()
        print(res)
        locking_socket.close()


        # ------ CACHING ------
        cache(filename_DS, write_client_input, "a+", client_id)

        return "Written to file " + filename + " successfully"

def cache(filename_DS, write_client_input, RW, client_id):
    cache_file = curr_path + "\\cache" + "\\client_cache" + client_id + "\\" + filename_DS       # append the cache folder and filename to the path
    
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)         # create the directory/file

    if RW == "a+" or RW == "w":
        with open(cache_file, RW) as f:        # write to the cached file
            f.write(write_client_input)
    else:
        with open(cache_file, "r") as f:        # read from the cached file
            print_breaker()
            print(f.read())
            print_breaker()


def handle_read(filename, file_version_map, client_id):
    client_socket = create_socket()  # create socket to directory service
    reply_DS = send_directory_service(client_socket, filename, 'r', False)  # send file name to directory service
    client_socket.close()   # close directory service connection

    if reply_DS == "FILE_DOES_NOT_EXIST":
        print(filename + " does not exist on a fileserver")
    else:
        # parse info received from the directory service
        filename_DS = reply_DS.split('|')[0]
        fileserverIP_DS = reply_DS.split('|')[1]
        fileserverPORT_DS = reply_DS.split('|')[2]

        client_socket = create_socket()  # create socket to file server
        read_cache = send_read(client_socket, fileserverIP_DS, int(fileserverPORT_DS), filename_DS, "r", file_version_map, "READ", filename_DS, client_id) # send filepath and read to file server

        if not read_cache:
            reply_FS = client_socket.recv(1024)    # receive reply from file server, this will be the text from the file
            reply_FS = reply_FS.decode()
            client_socket.close()

            if reply_FS != "EMPTY_FILE":
                print_breaker()
                print (reply_FS)
                print_breaker()

                cache(filename_DS, reply_FS, "w", client_id)  # update the cached file with the new version from the file server
                print (filename_DS + " successfully cached...")
            else:
                print(filename_DS + " is empty...")
                del file_version_map[filename_DS]


def handle_create(filename, file_version_map, client_id):
    client_socket = create_socket()
    res = send_directory_service(client_socket, filename, "CREATE", False)
    print(res)
    file_version_map[filename] = 0
    client_socket.close()


def send_directory_service(client_socket, filename, RW, list_files):
    serverName = 'localhost'
    serverPort = 9090   # port of directory service
    client_socket.connect((serverName,serverPort))

    if not list_files:
        msg = filename + '|' + RW
        # send the string requesting file info to directory send_directory_service
        client_socket.send(msg.encode())
        reply = client_socket.recv(1024)
        reply = reply.decode()
    else:
        msg = "LIST|w"
        # send the string requesting file info to directory service
        client_socket.send(msg.encode())
        reply = client_socket.recv(1024)
        reply = reply.decode()
        client_socket.close()
        print ("Listing files on directory server...")
        print (reply)

    #print (reply)
    return reply

def instructions():
    # instructions to the user
    print ("------------------- INSTRUCTIONS ----------------------")
    print ("<write> [filename] - write to file mode")
    print ("<end> - finish writing")
    print ("<read> [filename] - read from file mode")
    print ("<create> [filename] - create a file")
    print ("<list> - lists all existing files")
    print ("<instructions> - lets you see the instructions again")
    print ("<quit> - exits the application")
    print ("-------------------------------------------------------\n")

def print_breaker():
    print ("--------------------------------")

def check_valid_input(input_string):
    # check for correct format for message split
    if len(input_string.split()) < 2:
        print ("Incorrect format")
        instructions()
        return False
    else:
        return True