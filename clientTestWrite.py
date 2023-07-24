import client_utils
import _thread
from time import gmtime, strftime, time, sleep

client_utils.instructions()
file_version_map = {}

def main():
    print ("\n")
    while 1:
        client_id = str(round(time() * 1000))
        _thread.start_new_thread(client_utils.handle_write, ("file2.txt", client_id, file_version_map))
        sleep(2)

if __name__ == "__main__":
    main()