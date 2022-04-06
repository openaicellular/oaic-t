
import socket
from _thread import *
import threading

print_lock = threading.Lock()

# a thread waiting new actor connection
def wait_actor_connection(host, port):
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        print("socket binded to port", port)
        s.listen(5)
        conn, addr = s.accept()
        # register the new socket connection
        print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])
        start_new_thread(wait_recv_from_actor, (conn,))



# thread function
def wait_recv_from_actor(conn):
    while True:
        # data received from client
        data = conn.recv(1024)
        if not data:
            print('Bye')
            # lock released on exit
            print_lock.release()
            break
        # reverse the given string from client
        data = data[::-1]
        # send back reversed string to client
        conn.send(data)
    # connection closed
    conn.close()
        
def Main():
    host = "127.0.0.1"
    port = 12345
    print('Server started...')
    start_new_thread(wait_actor_connection, (host, port))


if __name__ == '__main__':
    Main()
