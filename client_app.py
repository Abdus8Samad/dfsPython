import sys
import client_utils
from time import time
import _thread

def main():

    print ("\n")
    client_utils.instructions()
    client_id = str(round(time() * 1000))
    # for caching
    file_version_map = {}

    while True:
       
        client_input = sys.stdin.readline()

        if "<write>" in client_input:
            while not client_utils.check_valid_input(client_input):       # error check the input
                 client_input = sys.stdin.readline()
            
            filename = client_input.split()[1]      # get the filename from the input

            # response = _thread.start_new_thread(client_utils.handle_write, (filename, client_id, file_version_map))    # handle the write request
            response = client_utils.handle_write(filename, client_id, file_version_map)    # handle the write request
            # print(response)
            # if "success" not in response:
            #     print("Try again")
            print ("Exiting <write> mode...\n")
            

        elif "<read>" in client_input:
            while not client_utils.check_valid_input(client_input):    # error check the input
                 client_input = sys.stdin.readline()
            filename = client_input.split()[1]   # get file name from the input
            client_utils.handle_read(filename, file_version_map, client_id)        # handle the read request 
            print("Exiting <read> mode...\n")

        elif "<create>" in client_input:
            while not client_utils.check_valid_input(client_input):    # error check the input
                 client_input = sys.stdin.readline()
            filename = client_input.split()[1]   # get file name from the input
            filename = filename.split('.')[0] + '.txt' # .txt is default for now
            client_utils.handle_create(filename, file_version_map, client_id)        # handle the read request 
        
        elif "<list>" in client_input:
            client_socket = client_utils.create_socket()
            client_utils.send_directory_service(client_socket, "", "w", True)
            client_socket.close()

        elif "<instructions>" in client_input:
            client_utils.instructions()


        elif "<quit>" in client_input:
            print("Exiting application...")
            sys.exit()

if __name__ == "__main__":
    main()