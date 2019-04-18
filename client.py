import socket

input_data = input('Введите запрос в формате HH[:MM[:SS]]-<some_string>:')
sock = socket.socket()
sock.connect(('localhost', 3631))
sock.send(input_data.encode("utf-8"))

data = sock.recv(1024).decode()
sock.close()

print(data)