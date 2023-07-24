# Python Distributed File System 

## Dependencies
This project is written in **Python 3.6**  
It was written on a Windows Machine.
This project uses sockets to send information between servers and services.

To run this project, do the following:

* Run the client application: **python start_script.py**

```
$ python start_script.py
Starting services...
FILE SERVER is ready to receive...
FILE SERVER is ready to receive...    
FILE SERVER is ready to receive...    
LOCKING SERVICE is ready to receive...
DIRECTORY SERVICE is ready to receive...
```

## file servers:

* primary_server holds the primary copy for replication, can be used for writing : **python primary_server.py**
* replica_server_1 only takes read requests: **python replica_server_1.py**
* replica_server_2 (like replica_server_1) only takes read requests: **python replica_server_2.py**


## Example Usage

* Start up the start_script.py. primary_server, replica_server_1 and replica_server_2 must exist in their own separate folders/ directories.

* Open 2 clients using ***python client.py*** in separate terminals.

* Client 1 write:

```
$<write> somefilename
Write some text...
<end> to finish writing
--------------------------------
$Hello world!
$<end>
--------------------------------
Sending version: 0
File successfully written to
File unlocked...
Exiting <write> mode...

```

* Client 1 read:

```
$<read> somefilename
Checking version...
Versions match, reading from cache...
--------------------------------
Hello world!

--------------------------------
Exiting <read> mode...
```

* Client 2 read: 

```
$<read> somefilename
REQUESTING FILE FROM FILE SERVER - FILE NOT IN CACHE
--------------------------------
Hello world!

--------------------------------
somefilename.txt successfully cached...
Exiting <read> mode...
```

## Project Overview
This project simulates a distributed file system using the NFS protocol.
It can support multiple clients accessing files.
The following are the main components of the file system:

* Distributed transparent file access
* Directory service
* Locking service
* Caching
* Replication

----

**Distributed transparent file access**

Clients can read from and write to files on fileservers. The client side application is a text editor and viewer. The client application's functionality comes from the client library (client_utils.py). The client never downloads or uploads a file from a fileserver, it downloads or uploads the contents of the file. 

The client can use the following commands to access files:

	<write> [filename]  # write to file mode
	<end>           # finish writing

	<read> [filename]   # read from file mode

	<create> [filename]  # create to file mode

	<list>          # lists all existing files

	<instructions>      # lets you see the instructions 

	<quit>          # exits the application

----

**Directory service (similar to a load balancer)**


A directory service facilitates the association between the requested file name and the corresponding file server. This information is stored in a CSV file called "file_mappings.csv," which contains details like the file's actual name, the file server's IP and Port where it's stored, and whether the file server holds the primary copy.

When a client intends to write to a file, the directory service forwards the request to primary_server, which holds the primary copy. On the other hand, if the client wants to read from a file, the directory service routes the request to either replica_server_1 or replica_server_2, as they have replicated versions of the files present on primary_server. This redundancy ensures smoother access and availability of files while avoiding overloading a single server.


----

**Locking service**

In the given file access system, when client 1 wishes to write to a file, it requests a lock for writing. The client can only proceed with writing once it receives the lock. However, it can read from the file without any restrictions. If client 2 wants to write to the same file and finds it locked by client 1, it must wait until client 1 unlocks it. Client 2 will continuously poll the file's status to check if it becomes unlocked, with a timeout of 10 seconds for each polling attempt.

This system ensures fair locking and unlocking behavior, resembling a First-In-First-Out (FIFO) queue. When multiple clients request to write to the file in sequence (client 2, client 3, and client 4), they will obtain the lock in the order of their requests. Hence, client 2 will be the first to acquire the lock on the file. Once client 2 finishes writing and unlocks the file, client 3 will receive the lock, followed by client 4, and so on, maintaining the fairness of access.

This mechanism allows clients to access the file for writing in a controlled and orderly manner, preventing contention and ensuring that all clients eventually get their turn to write to the file.

----

**Caching (Write Through)**

![](https://github.com/Abdus8Samad/dfsPython/blob/main/write_through.png)

the described system ensures cache consistency between clients when accessing a file. Here's a summary of how the process works:

1. Write Request: When a client requests to write to a file, the request is sent to the fileserver that holds the primary copy of the file. The file is updated on the fileserver, and simultaneously, the client's cache is also updated with the new version of the file.

2. Read Request: When a client requests to read a file, the client first checks in the cache if the file is present, if it is it return that otherwise it requests the corresponding replica server assign in the `file_mappings.csv` file and that server sends the content. It is simultaneously updated in the cache. 

3. Cache Freshness: By following this approach, the system ensures that clients always have the most recent version of a file when reading from their cache.

---- 

**Replication**

The primary copy model in this file system is designed to ensure file replication among multiple fileservers, providing data redundancy and consistency. Here's how the process works:

1. Write Request: When a client wishes to write to a file, the directory service directs the write request to primary_server. primary_server is responsible for holding the primary copy of all files, making it the central authority for write operations. This design simplifies the management of write requests, as they are all handled by primary_server.

2. File Replication: After the client finishes writing the file, primary_server ensures consistency across all fileservers by replicating the file. It sends a copy of the newly updated file to both replica_server_1 and replica_server_2.

3. Read Request: When a client requests to read a file, the request is not directed to primary_server (the primary copy holder). Instead, the client is sent to read a replicated copy of the file that resides on either replica_server_1 or replica_server_2. This load balancing approach ensures that read requests are distributed among the replicated servers, reducing potential bottlenecks and improving overall performance.

By implementing this primary copy model with file replication, the file system achieves data redundancy and consistency across multiple fileservers. The primary copy on primary_server allows for centralized write management, while the replicated copies on replica_server_1 and replica_server_2 enable efficient and balanced read operations for clients. This system architecture enhances data availability, fault tolerance, and performance in the file system.
