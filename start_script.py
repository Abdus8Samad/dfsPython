import subprocess
import sys

def main():
    print("Starting services...")
    # print("for stopping the service type <quit>")
    # ------ file servers ------
    fileServerA = subprocess.Popen(["python", "./fileserverA/file_serverA.py"])
    fileServerB = subprocess.Popen(["python", "./fileserverB/file_serverB.py"])
    fileServerC = subprocess.Popen(["python", "./fileserverC/file_serverC.py"])

    # ------ directory service ------
    directoryService = subprocess.Popen(["python", "directory_service.py"])

    # ------ locking service ------
    lockingService = subprocess.Popen(["python", "locking_service.py"])

    fileServerA.wait() # mainly for writing
    fileServerB.wait() # mainly for reading
    fileServerC.wait() # same as B

    directoryService.wait() # for getting info about directories and listing files
    lockingService.wait() # for adding mutex locks for preventing writing conflicts
    # while sys.stdin.readline != "<quit>":
    #     pass
    # sys.exit()

if __name__ == "__main__":
    main()