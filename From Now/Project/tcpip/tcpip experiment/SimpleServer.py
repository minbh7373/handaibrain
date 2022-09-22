import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 8089))
server.listen(1)

while True:
    conn, addr = server.accept()
    cmnd = conn.recv(4)  # The default size of the command packet is 4 bytes
    print(cmnd)

    if 'INIT' in str(cmnd):
        # Do the initialization action
        conn.sendall(b'INIT-DONE')
    elif 'PLAY' in str(cmnd):
        # Do the play action
        conn.sendall(b'PLAY-DONE')
    elif 'QUIT' in str(cmnd):
        # Do the quiting action
        conn.sendall(b'QUIT-DONE')
        break

server.close()