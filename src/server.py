
import socket              
import platform
import time   
import re                 
from _thread import *
from _socket import AF_INET, SOCK_STREAM

server_port = 7734;
server_socket = socket.socket(AF_INET,SOCK_STREAM)
#server_host = socket.gethostname()
server_host = '127.0.0.1'
server_socket.bind((server_host,server_port))
server_socket.listen(80)

peer_map =  list()
rfc_map = list()
peer_rfc_map = list()

def add_to_peer_rfc_map(map,rfc_number,rfc_title, host, port):
    rfc_detail = [str(rfc_number), rfc_title, host, str(port)]
    map.insert(0,rfc_detail)
    return map

def add_to_peer_map(map,host, port):
    host_port_map = [host, str(port)]
    map.insert(0,host_port_map)
    return map

def add_to_rfc_map(map,rfc_number, host, port):
    rfc_detail = [str(rfc_number), host, str(port)]
    map.insert(0,rfc_detail)
    return map

def delete_from(map,host):
    if [host in element for element in map]:
        element = [element for element in map if host in element]
        map = [list for list in map if list not in element]
        
    return map

def handle_add_rfc_request(request_message,peer_rfc_map,rfc_map):  
    #global rfc_map,peer_rfc_map
    rfc_number = re.split(' ',request_message[0])[2]
    host = re.split(': ',request_message[1])[1]
    port = re.split(': ',request_message[2])[1]
    title = re.split(': ',request_message[3])[1]
    print('Handling ADD request')
    print(rfc_number,' ',host,' ',str(port),' ',title)
    peer_rfc_map = add_to_peer_rfc_map(peer_rfc_map, rfc_number,title, host, port)
    rfc_map = add_to_rfc_map(rfc_map,rfc_number, host, port)
    server_response = 'P2P-CI/1.0 200 OK\r\nRFC ' + str(rfc_number) + ' ' + title + ' ' + host + ' ' + str(port) + '\r\n'
    print('Server Response : ',server_response)
    return peer_rfc_map,rfc_map,server_response

def handle_list_request(peer_rfc_map,request_message):
    #global peer_rfc_map  
    server_response = 'P2P-CI/1.0 200 OK\r\n'
    print('Handling LIST request')
    for iterator in peer_rfc_map:
        rfc_detail = 'RFC ' +  ' '.join(iterator) + '\r\n'
        server_response = server_response + rfc_detail
        print('Server Response : ',server_response)
    return peer_rfc_map,server_response

def handle_lookup_request(peer_rfc_map,request_message):
    #global peer_rfc_map
    rfc_number = re.split(' ',request_message[0])[2]
    server_response = 'P2P-CI/1.0 200 OK\r\n'
    print('Handling lookup request')
    if [rfc_number in element for element in peer_rfc_map]:
        print(rfc_number)
        element = [element for element in peer_rfc_map if rfc_number in element]
        print(','.join(str(p) for p in element))
        for iterator in element:
            server_response += 'RFC ' + iterator[0] + ' ' +  iterator[1] + ' ' + iterator[2] + ' ' + str(iterator[3]) + '\r\n'
            print('Server Response : ',server_response)
    return peer_rfc_map,server_response

def client_handler(client_socket,client_addr):
    global peer_map,rfc_map,peer_rfc_map,peer_map_keys,peer_rfc_map_keys,rfc_map_keys
    print(client_addr,"is connected and running")
    client_socket.send(('You are connected to ' + server_host + ' with port ' + str(server_port)).encode('utf-8'))
    # Client has to send the upload port number, list of RFCs and their titles
    client_details = client_socket.recv(2048)
    details_list = re.split('\r\n',client_details.decode('utf-8'))
    print(','.join(str(p) for p in details_list))
    host = None
    port = None
    for iterator in range(0,len(details_list)-1):
        header = re.split(' ',details_list[iterator])
        print(iterator)
        if iterator == 0:
            host = header[0]
            port = header[1]
            peer_map = add_to_peer_map(peer_map, host, port)
        else :
            rfc_number = header[1]
            rfc_title= header[2]
            peer_rfc_map = add_to_peer_rfc_map(peer_rfc_map, rfc_number,rfc_title, host, port)
            rfc_map = add_to_rfc_map(rfc_map,rfc_number, host, port)
   
    print(','.join(str(p) for p in peer_map))
    print(','.join(str(p) for p in peer_rfc_map))
    print(','.join(str(p) for p in rfc_map))
    while True :
        data = client_socket.recv(2048)
        client_message = data.decode('utf-8')
        request_message = re.split('\r\n',client_message)
        request = re.split(' ',request_message[0])[0]
        print(str(client_message))
        if client_message == "EXIT":
            break
        elif request == "LOOKUP":
            peer_rfc_map,server_response = handle_lookup_request(peer_rfc_map, request_message)
            print(server_response)
            client_socket.send(server_response.encode('utf-8'))
        elif request == "LIST":
            peer_rfc_map,server_response = handle_list_request(peer_rfc_map,request_message)
            client_socket.send(server_response.encode('utf-8'))
        elif request == "ADD":
            peer_rfc_map,rfc_map,server_response = handle_add_rfc_request(request_message,peer_rfc_map,rfc_map)
            client_socket.send(server_response.encode('utf-8'))
                
    host,port = client_socket.getpeername()   
    peer_map = delete_from(peer_map,host)
    peer_rfc_map = delete_from(peer_rfc_map,host)
    rfc_map = delete_from(rfc_map,host)
    print("Printing end")
    print(','.join(str(p) for p in peer_map))
    print(','.join(str(p) for p in peer_rfc_map))
    print(','.join(str(p) for p in rfc_map))
    print("Ending client")   
  
while True :
    client_socket,client_addr = server_socket.accept()
    start_new_thread(client_handler,(client_socket,client_addr))

server_socket.close()



