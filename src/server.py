import socket
import pickle
import threading
import sys
import subprocess

rfc_map = []
rfc_lck = threading.Lock()
peer_map = []					
peer_lck = threading.Lock()

class clientHandler(threading.Thread):
	def __init__(self, client_details):
		threading.Thread.__init__(self)
		self.client = client_details[0]
		self.address = client_details[1]
		self.response_header = ''
	
	
	def parseMessage(self, msg):
		response_lines = msg.split("\n")
		response_line = []
		for line in response_lines:
			response_line.append(str(line).split(' '))
		rfc_title = ''
		for word_in_title in range(1,len(response_line[3])):
			rfc_title += ' ' + response_line[3][word_in_title]
		if(response_line[0][0] in ('LIST')):
			return(response_line[0][0], None, response_line[1][1], response_line[2][1], None, response_line[0][1])
		else:
			return(response_line[0][0], response_line[0][2], response_line[1][1], response_line[2][1], rfc_title, response_line[0][3])
	
	def addToRfcList(self,data, host):
		response_header = '200 OK'
		rfc_lck.acquire()
		rfc_map.append((data[1],data[4],host[0],data[3], host[1]))
		rfc_lck.release()	
		server_response = data[4]+' '+data[2]+' '+data[3]
		self.sendClientResponse(response_header, server_response)

		
	#Look Up Service
	def lookupRFC(self, data):
		rfcNum = data[1]
		peersWithRfc = ''
		
		for rfc in rfc_map:
			if(rfc[0] == rfcNum):
				peersWithRfc = peersWithRfc+rfc[0]+'<c>'+rfc[1]+'<c>'+str(rfc[2])+'<c>'+str(rfc[4])+'<c>'+rfc[3]+'\n'		
				
		if len(peersWithRfc) > 0:
			response_header = '200 OK'
		else:
			response_header = '404 Not Found'
		
		self.sendClientResponse(response_header, peersWithRfc)

	def getRfcList(self):
		index = ''
		response_header = '200 OK'
		for rfc in rfc_map:
			index = index+rfc[0]+'<c>'+rfc[1]+'<c>'+str(rfc[2])+'<c>'+str(rfc[4])+'<c>'+rfc[3]+'\n'
			#index = index+rfc[0]+'<c>'+rfc[1]+'<c>'+str(rfc[2])+'<c>'+str(rfc[3])+'<c>'+str(rfc[4])+'\n'
		self.sendClientResponse(response_header, index)
	
	def sendClientResponse(self, response_header, msgBody):
		server_response = 'P2P-CI/1.0 '+response_header+'\n'+msgBody
		#self.client.send(bytes(preMsg,'UTF-8'))
		self.client.send(bytes(server_response.encode('UTF-8')))
		
	def clientExitHandler(self,host):
		print('Client ('+host[0]+', '+str(host[1])+') has closed the connection')
		rfc_to_be_deleted = list(rfc_map)
		peer_map.remove(host)
		for rfc in rfc_to_be_deleted:
			if rfc[4] == host[1] and rfc[2] == host[0] :
				rfc_map.remove(rfc)
		del rfc_to_be_deleted
	
	
	def run(self):
		peer_lck.acquire()
		peer_map.append(self.address)
		peer_lck.release()
				
		while True:
			try:
				clientMessage = self.client.recv(1024)
			except ConnectionResetError:
				break;			
			message = clientMessage.decode('UTF-8')
			print(message)
			if len(message) != 0:					
				msg = self.parseMessage(message)
				if msg[5] != 'P2P-CI/1.0':
					response_header = '505 P2P-CI Version Not Supported'
					self.sendClientResponse(response_header, '')
				else:
					
					if msg[0] == 'LIST':
						self.getRfcList()
					elif msg[0] == 'LOOKUP':
						self.lookupRFC(msg)
					elif msg[0] == 'ADD':
						self.addToRfcList(msg, self.address)
					else:
						response_header = '400 Bad Request'
						self.sendClientResponse(response_header, '')
			else:
				break								
				
		self.clientExitHandler(self.address)
		self.client.close()
		
		
def main():
	serverPort = 7734	
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
	serverSocket.bind(('',serverPort)) 
	serverSocket.listen(80)

	while True:
		print("Waiting for new peer!")
		clientThread = clientHandler(serverSocket.accept())
		clientThread.start()

if __name__ == '__main__':
	main()