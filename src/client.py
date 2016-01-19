import socket
import threading
import time
import platform
import sys
import os
import subprocess
port1 = 0
serverHost = '192.168.56.101'
serverPort = 7734
class p2s(threading.Thread):
	def __init__(self, uploadPort, p):
		threading.Thread.__init__(self)
		self.uploadPort = uploadPort
		self.p = p
		self.start()
	
	def mainMenu(self, clientSocket):		
		while True:
			print("1. Add RFC \n")
			print("2. Look Up RFC \n")
			print("3. List RFC index \n")
			print("4. Exit network\n")
			menu_option_selected = str(input("Input = "))
			if menu_option_selected == '1':
				self.addRfcToServer(clientSocket, 1, 0, 0)
			elif menu_option_selected == '2':
				self.lookUpRfc(clientSocket)
			elif menu_option_selected == '3':
				self.listIndexRequest(clientSocket)
			elif menu_option_selected == '4':
				clientSocket.close()
				break
			else:
				print("Invalid Selection. Re-enter the Option!!!")
	def parseMessage(self, message):
		messageLines = message.split("\n")
		return messageLines	
				
	def createPacket(self, request_method, rfcNum, file):
		hostLine = 'Host:' + ' ' + socket.gethostbyname(socket.gethostname())
		portLine = 'Port:' + ' ' + str(self.uploadPort)	
		version = 'P2P-CI/1.0'
		packet = ''
		if request_method == 'ADD':		
			#RFC = file.split(',')[0]
			title = 'Title:' + file.split(',')[1].split(".")[0]
			packet = request_method + ' ' + 'RFC' + ' ' + rfcNum + ' ' + version + '\n' + hostLine + '\n' + portLine + '\n' + title +  '\n\n'
		elif request_method == 'CURR_ADD':
			RFC = 'RFC' + ' ' + rfcNum
			title = file.split(",")[1].split(".")[0]
			title = 'Title:' + title
			packet = 'ADD' + ' ' + RFC + ' ' + version + '\n' + hostLine + '\n' + portLine + '\n' + title + '\n\n'	 
		elif request_method == 'LOOKUP':			
			RFC = 'RFC' + ' ' + str(input("RFC Number = "))
			title = 'Title:' + raw_input("RFC title = ")
			packet = request_method + ' ' + RFC + ' ' + version + '\n' + hostLine + '\n' + portLine + '\n' + title + '\n\n'
		elif request_method == 'GET':
			RFC = 'RFC' + ' ' + rfcNum
			OS = 'OS:' + ' ' + platform.platform()
			packet = request_method + ' ' + RFC + ' ' + version + '\n' + hostLine + '\n' + OS + '\n' + '\n'  # PROPER REQUEST
		else:
			packet = request_method + ' ' + version + '\n' + hostLine + '\n' + portLine + '\n\n'	
		return packet
	
	def advertiseRfc(self, clientSocket):
		rfc_list = []
		for file in os.listdir("."):
			if file.startswith("RFC") and file.lower().endswith(('.pdf')):
				rfc_list.append(file)
		print('Advertising my RFC list...')
		for rfc in rfc_list:
			self.addRfcToServer(clientSocket, 0, 0, rfc)				

	def addRfcToServer(self, client_socket, menu_option_selected, rfc, file):
		if menu_option_selected != 0:
			message = ''
			while True :
				RFC = str(input("RFC Number = "))
				title = raw_input("RFC title = ")
				
				filename = 'RFC' + str(RFC) + ', ' + title + '.pdf'
				#if os.path.isfile(filename) :
				flag = False
				for file in os.listdir("."):
					#print 'file = ' + file
					#print 'filename = '+ filename
					if file == filename:
						flag = True
						break
				if flag == True:
					message = self.createPacket('ADD', str(RFC), filename)
					client_socket.send(bytes(message.encode('UTF-8')))	
					server_response = client_socket.recv(2048) 
					server_message = server_response.decode('UTF-8')
					print('\n' + server_message + '\n')
					break
					
				print(filename + ' does not exist. Try again')
				option = raw_input('I do not want to add! (Y/N)')
				if option == 'Y' :
					break
			
		else:
			#message = self.createPacket('CURR_ADD', rfc[3:len(rfc) - 4], file)
			rfcString = file.split(",")[0]
			rfcNum = rfcString[3:]
			message = self.createPacket('CURR_ADD', rfcNum, file)
			client_socket.send(bytes(message.encode('UTF-8')))	
			server_response = client_socket.recv(2048) 
			server_message = server_response.decode('UTF-8')
			print('\n' + server_message + '\n')

	def lookUpRfc(self, client_socket):
		message = self.createPacket('LOOKUP', 0, 0)
		client_socket.send(bytes(message.encode('UTF-8')))	
		server_response = client_socket.recv(1024) 
		server_message = server_response.decode('UTF-8')
		rfc_peer_list = self.parseMessage(server_message)
		print('\n' + rfc_peer_list[0])
		if '200 OK' not in rfc_peer_list[0]:
			print('Request was not served successfully')
		else:
			print('Select a peer from the below peer list to download RFC.')
			print('Select Quit download option otherwise')			
			for iterator in range(1, len(rfc_peer_list) - 1):
				peerDetails = rfc_peer_list[iterator].split('<c>')  # change <c> 
				print("%d Host:%s\tPort:%s" % (iterator, peerDetails[2], peerDetails[3]))
			print(str(iterator + 1) + ". Quit Download Option")
			peer_selected_for_download = input("option = ")
			while int(peer_selected_for_download) <= 0 or int(peer_selected_for_download) > len(rfc_peer_list) + 1 :
					peer_selected_for_download = input("Enter valid Integer option = ") 

			if int(peer_selected_for_download) == iterator + 1:
					return
			else:
				self.downloadFromPeer(rfc_peer_list[int(peer_selected_for_download)])	    
				return
	def listIndexRequest(self, client_socket):
		sendMessage = self.createPacket('LIST', None, 0)
		client_socket.send(bytes(sendMessage.encode('UTF-8')))	
		server_response = client_socket.recv(1024) 
		server_message = server_response.decode('UTF-8')
		self.printIndex(server_message)
	
	def printIndex(self, rfcIndex):
		rfcList = rfcIndex.split('\n')
		print('\n' + rfcList[0] + '\n')
		if '200 OK' not in rfcList[0]:
			print('Request for RFC index was not completed successfully.')
		else:
			for i in range(1, len(rfcList) - 1):
				rfc = rfcList[i].split('<c>')
				print(str(i) + '.\t' + rfc[0] + '\t' + rfc[1] + '\t' + rfc[2] + '\t' + rfc[3] + '\n')
				#print(str(i) + '.\t' + rfc[0] + '\t' + rfc[1] + '\t' + rfc[2] + '\n')

	
	def downloadFromPeer(self, peerDetails):
		peerDetailsList = peerDetails.split('<c>')
		rfc = peerDetailsList[0]
		title = peerDetailsList[1]
		peer_hostname = peerDetailsList[2]
		peer_upload_port = int(peerDetailsList[4])  # have to change this port number location
		peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)               
		peerSocket.connect((peer_hostname, peer_upload_port))
		filename = 'RFC' + rfc + ', ' + title + '.pdf'
		sendMessage = self.createPacket('GET', rfc, filename)
		peerSocket.send(bytes(sendMessage.encode('UTF-8')))	

		data = peerSocket.recv(2048) 
		decodedData = data.decode('UTF-8')
		print('\n' + decodedData + '\n')
		if '200 OK' in decodedData:
			rfcFile = 'RFC' + rfc + ',' + title + '.pdf'
			executable = 'python gbnClient.py' + ' ' + str(peer_upload_port) + ' ' + str(port1) + ' ' + '"' + rfcFile + '"' + ' ' + str(self.p)
			os.system(executable)			
		else:
			print('Error while connecting to peer. Try again.')
		
		peerSocket.close()
				
	def run(self):
		global serverHost,serverPort
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect((serverHost, serverPort))

		print('Select among the following menu options')
		print('1. Advertise existent RFCs to server')
		print('2. Add RFCs later. Take me to Main Menu')
		initial_menu_option = int(input('Option = '))
		if initial_menu_option == 1:
			self.advertiseRfc(client_socket)
		self.mainMenu(client_socket)

class p2p(threading.Thread):
	def __init__(self, client_details, window_size, mss, upload_port):
		threading.Thread.__init__(self)
		self.client = client_details[0]
		self.address = client_details[1]
		self.n = window_size
		self.mss = mss
		self.upload_port = upload_port
	def parseMessage(self, message):
		messageList = message.split("\n")
		messageDetailsList = []
		for msg in messageList:
			messageDetailsList.append(str(msg).split(" "))		
		return messageDetailsList

	def prepareResponsePacket(self, status, rfcFile):

		OS = 'OS:' + ' ' + platform.platform() + '\n'
		currentTime = 'Date:' + ' ' + time.asctime() + '\n'
		if status == '200 OK':
			seconds = os.path.getmtime(rfcFile)
			lastModifiedTime = 'Last-Modified:' + ' '+ time.strftime('%Y-%m-%d %H:%M', time.localtime(seconds)) + '\n'
			contentLength = 'Content-Length:' + str(os.path.getsize(rfcFile)) + '\n'
		else:
			lastModifiedTime = 'Last-Modified:' + '\n'
			contentLength = 'Content-Length:' + '\n'
		contentType = 'Content-Type: text/plain' + '\n'
		response = 'P2P-CI/1.0' + ' ' + status + '\n' + currentTime + OS + lastModifiedTime + contentLength + contentType
		return response
	def handlePeerRequest(self, peerMessage):
		global port1
		request_method = peerMessage[0][0]
		version = peerMessage[0][3]
		flag = False
		for file in os.listdir("."):
			if file.startswith('RFC' + str(peerMessage[0][2])) :
				rfcFile = file
				flag = True
		#rfcFile = 'RFC' + peerMessage[0][2] + '.pdf'				
		response_status = ''
		if request_method != 'GET':  # Only GET Request is supported
			response_status = '400 Bad Request'	
		elif not os.path.exists(rfcFile) or flag == False:  # The file is checked in the current working directory	
			response_status = '404 Not Found'		
		elif version != 'P2P-CI/1.0':  # Only P2P-CI/1.0 is supported
			response_status = '505 P2P-CI Version Not Supported' 
		else:
			response_status = '200 OK'
		responseMsg = self.prepareResponsePacket(response_status, rfcFile)  # Response to the other peer requesting a file download
		self.client.send(bytes(responseMsg.encode('UTF-8')))
		if response_status == '200 OK':
			peerHostName, peerPort = self.client.getpeername()
			port1 = peerPort
			print(peerHostName + '' + str(peerPort))
			executable = 'python gbnServer.py ' + str(peerHostName) + ' ' + str(7777) + ' ' + '"' + rfcFile + '"' + ' ' + str(self.n) + ' ' + str(self.mss) + ' ' + str(self.upload_port)
			print(str(executable))
			pro = subprocess.Popen(executable, shell=True)
		self.client.close()	
			
	def run(self):
		receivedMessage = self.client.recv(1024)
		decodedMessage = receivedMessage.decode('UTF-8')
		print(decodedMessage)
		data = self.parseMessage(decodedMessage)
		self.handlePeerRequest(data)
		
class uploadHandler(threading.Thread):		
	def __init__(self, uploadPort, window_size, mss):
		threading.Thread.__init__(self)
		self.myUploadSocket = None
		self.port = uploadPort
		self.n = window_size
		self.mss = mss
		self.start()	
	def run(self):
		self.myUploadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.myUploadSocket.bind(('', self.port)) 
		self.myUploadSocket.listen(5)
		while True:
			try:
				u = p2p(self.myUploadSocket.accept(), self.n, self.mss, self.port)
				u.start()
			except OSError:
				print('Peer exited the network')
				break

def main():	
	uploaderPort = int(input("Upload port : "))
	mss = int(input("Maximum Segment Size (Enter value less than 1200) : "))
	n = int(input("Window size for Go Back N transmission : "))
	p = float(input("Probability of packet loss in the file server"))
	peerToServer = p2s(uploaderPort, p)  # Thread to communicate with the server
	peerToPeer = uploadHandler(uploaderPort, n, mss)  # Thread handling upload process
	while peerToServer.isAlive():
		pass
	peerToPeer.myUploadSocket.close()  # Closing the client 

if __name__ == '__main__':	
	main()