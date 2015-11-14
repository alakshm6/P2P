from socket import *
from test.test_email.test_message import first

serverPort = 7734
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(('127.0.0.1',serverPort))
modifiedSentence = clientSocket.recv(1024)
print(modifiedSentence.decode('utf-8'))
message = clientSocket.getsockname()[0] + ' ' + str(clientSocket.getsockname()[1]) + '\r\nRFC 123 first\r\nRFC 345 second\r\n'
clientSocket.send(message.encode('utf-8'))

add_message = 'ADD RFC 456 P2P-CI/1.0\r\n' + 'Host: ' + clientSocket.getsockname()[0] + '\r\n' + 'Port: ' + str(clientSocket.getsockname()[1]) + '\r\n' + 'Title: ' + 'A Proferred Official ICP\r\n'
clientSocket.send(add_message.encode('utf-8'))
serverResponse = clientSocket.recv(2048)
print(serverResponse.decode('utf-8'))

lookup_message = 'LOOKUP RFC 456 P2P-CI/1.0\r\n' + 'Host: ' + clientSocket.getsockname()[0] + '\r\n' + 'Port: ' + str(clientSocket.getsockname()[1]) + '\r\n' + 'Title: ' + 'A Proferred Official ICP\r\n'
clientSocket.send(lookup_message.encode('utf-8'))
serverResponse = clientSocket.recv(2048)
print(serverResponse.decode('utf-8'))

list_message = 'LIST ALL P2P-CI/1.0\r\n' + 'Host: ' + clientSocket.getsockname()[0] + '\r\n' + 'Port: ' + str(clientSocket.getsockname()[1]) + '\r\n'
clientSocket.send(list_message.encode('utf-8'))
serverResponse = clientSocket.recv(2048)
print(serverResponse.decode('utf-8'))


clientSocket.send("EXIT".encode('utf-8'))
clientSocket.close()
