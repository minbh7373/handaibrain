import socket
import struct

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 8089)
client.connect(server_address)

for x in range(100):
    size = struct.unpack('i', client.recv(4))[0]  # Extract the msg size from four bytes - mind the encoding
    str_data = client.recv(size)
    print('Data size: %s Data value: %s' % (size, str_data.decode('ascii')))

client.sendall(b'Enough data :) Thanks')  # Sending anything back closes the connection
