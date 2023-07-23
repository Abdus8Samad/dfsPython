import sys
import client_lib
from time import time
import _thread

def main():

    print ("\n")
    client_lib.instructions()
    client_id = str(round(time() * 1000))
    file_version_map = {}

    while True:
       
        client_input = sys.stdin.readline()

        if "<write>" in client_input:
            while not client_lib.check_valid_input(client_input):       # error check the input
                 client_input = sys.stdin.readline()
            
            filename = client_input.split()[1]      # get the filename from the input

            # response = _thread.start_new_thread(client_lib.handle_write, (filename, client_id, file_version_map))    # handle the write request
            response = client_lib.handle_write(filename, client_id, file_version_map)    # handle the write request
            # print(response)
            # if "success" not in response:
            #     print("Try again")
            print ("Exiting <write> mode...\n")
            

        elif "<read>" in client_input:
            while not client_lib.check_valid_input(client_input):    # error check the input
                 client_input = sys.stdin.readline()
            filename = client_input.split()[1]   # get file name from the input
            client_lib.handle_read(filename, file_version_map, client_id)        # handle the read request 
            print("Exiting <read> mode...\n")

        elif "<create>" in client_input:
            while not client_lib.check_valid_input(client_input):    # error check the input
                 client_input = sys.stdin.readline()
            filename = client_input.split()[1]   # get file name from the input
            filename = filename.split('.')[0] + '.txt' # .txt is default for now
            client_lib.handle_create(filename, file_version_map, client_id)        # handle the read request 
        
        elif "<list>" in client_input:
            client_socket = client_lib.create_socket()
            client_lib.send_directory_service(client_socket, "", "w", True)
            client_socket.close()

        elif "<instructions>" in client_input:
            client_lib.instructions()


        elif "<quit>" in client_input:
            print("Exiting application...")
            sys.exit()

if __name__ == "__main__":
    main()