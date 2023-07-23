import client_lib
import _thread
from time import gmtime, strftime, time, sleep

client_lib.instructions()
file_version_map = {}

def main():
    print ("\n")
    while 1:
        client_id = str(round(time() * 1000))
        _thread.start_new_thread(client_lib.handle_read, ("shard2.txt", file_version_map, client_id))
        sleep(0.5)

if __name__ == "__main__":
    main()