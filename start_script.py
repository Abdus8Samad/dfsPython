import subprocess
import sys

def main():
    print("Starting services...")
    # print("for stopping the service type <quit>")

    # ------ file servers ------
    primary_server = subprocess.Popen(["python", "./primary_server/primary_server.py"])
    replica_server_1 = subprocess.Popen(["python", "./replica_server_1/replica_server_1.py"])
    replica_server_2 = subprocess.Popen(["python", "./replica_server_2/replica_server_2.py"])

    # ------ directory service ------
    directoryService = subprocess.Popen(["python", "directory_service.py"])

    # ------ lock service ------
    lockService = subprocess.Popen(["python", "lock_service.py"])

    primary_server.wait() # mainly for writing
    replica_server_1.wait() # mainly for reading
    replica_server_2.wait() # same as 1

    directoryService.wait() # for getting info about directories and listing files
    lockService.wait() # for adding mutex locks for preventing writing conflicts
    # while sys.stdin.readline != "<quit>":
    #     pass
    # sys.exit()

if __name__ == "__main__":
    main()