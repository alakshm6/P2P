import sys
import socket
import threading
import time
import struct

lastSeqNumSent = 0			#LAST SENT SEQUENCE NUMBER
lastAckNumRecvd = 0				#SEQUENCE NUMBER OF LAST PACKET ACKED
expectedAck = 0			#SEQUENCE NUMBER NEXT EXPECTED ACK
sendLck = threading.Lock()

class gbnsender(threading.Thread):
	def __init__(self, cSock, host, port, msg, s):
		threading.Thread.__init__(self)
		self.timer = time.time()
		self.data = msg				#DATA OF 1 MSS SIZE TO BE SENT
		self.seqNum = s				#SEQUENCE NUMBER OF THE PACKET
		self.sock = cSock
		self.host = host				#SERVER IP ADDRESS
		self.port = port				#SERVER PORT
		self.start()

	def computeChecksum(self, data):
		sum = 0
		for i in range(0, len(data), 2):
			if i+1 < len(data):
				data16 = ord(data[i]) + (ord(data[i+1]) << 8)		#To take 16 bits at a time
				interSum = sum + data16
				sum = (interSum & 0xffff) + (interSum >> 16)		#'&' to ensure 16 bits are returned
		return ~sum & 0xffff										#'&' to ensure 16 bits are returned

	def createPacket(self, data, seq_num):
		#32 bit sequence number
		#16 bit check of the data part
		#16 bit 0101010101010101 -- Indicates data packet(in int 21845)
		seq = struct.pack('=I',seq_num)
		checksum = struct.pack('=H',self.computeChecksum(data))		#Computes the checksum of data
		#print (checksum)
		ack = struct.pack('=H',21845)
		#packet = seqNum+checksum+dataIndicator+bytes(data,'UTF-8')
		packet = seq+checksum+ack+bytes(data)
		return packet

	def run(self):
		global lastAckNumRecvd
		sendLck.acquire()
		packet = self.createPacket(self.data, self.seqNum)				#Packets are created here
		self.sock.sendto(packet,(self.host, self.port))
		sendLck.release()
		try:
			while lastAckNumRecvd < self.seqNum:
				elapsedTime = time.time() - self.timer
				if  elapsedTime < 5:									#RETRANSMISSION time = 5 seconds
					pass
				elif lastAckNumRecvd < self.seqNum:								#Rechecking the ACK
					print('PACKET TIMEOUT, SEQUENCE NUMBER = '+str(self.seqNum))
					self.sock.sendto(packet,(self.host, self.port))	#RETRANSMISSION of time-out packets(No ACK Received)
					self.timer = time.time()
		except:
			print('File server terminated the connection')
			self.sock.close()

#Thread Class to receive the ACK Packets from the Server
class receiver(threading.Thread):

	def __init__(self, cmd, client_socket):		
		threading.Thread.__init__(self)
		self.host = cmd[0]
		self.port = int(cmd[1])
		self.file = cmd[2]
		self.n    = int(cmd[3])
		self.MSS  = int(cmd[4])
		self.sockAddr = client_socket
		self.start()

	def parseMessage(self, msg):
		sequenceNum = struct.unpack('=I', msg[0:4])			#Sequence Number Acked by the server
		checksum = struct.unpack('=H', msg[4:6])				#16 bit field with all 0's
		identifier = struct.unpack('=H', msg[6:])			#16 bit field to identify the ACK packets
		return sequenceNum, checksum, identifier

	def run(self):
		print('Receiver Spawned')
		global lastSeqNumSent
		global lastAckNumRecvd		
		global expectedAck
		try:
			while lastAckNumRecvd < lastSeqNumSent or lastSeqNumSent <= 0 :			
				ackReceived, server_addr = self.sockAddr.recvfrom(2048)			#Receives the ACK packets 
				sequenceNum , zero16, identifier = self.parseMessage(ackReceived)
				print('Received ACK,with Sequence Number : ',sequenceNum[0])
				if int(identifier[0]) == 43690 and expectedAck == int(sequenceNum[0]):
					lastAckNumRecvd = int(sequenceNum[0])
					expectedAck = lastAckNumRecvd+1
		except:
			print('Server closed its connection')
			self.sockAddr.close()
			
#Thread that reads the file continuously
class fileReader(threading.Thread):

	def __init__(self, cmdInput, mySock):
		threading.Thread.__init__(self)
		self.host = cmdInput[0]
		self.port = int(cmdInput[1])
		self.filename = cmdInput[2]
		self.n    = int(cmdInput[3])
		self.MSS  = int(cmdInput[4])
		self.sock = mySock
		self.start()		

	def run(self):
		self.rdt_send()	

	def rdt_send(self):
		f = open(self.filename,'rb')
		currentSeqNum = 0
		global lastSeqNumSent
		global lastAckNumRecvd
		payload = ''
		byte = True
		while byte:
			byte = f.read(1)
			payload += byte
			if len(payload) == self.MSS or (not byte):		
				while currentSeqNum-lastAckNumRecvd >= self.n:
					pass
				gbnsender(self.sock, self.host, self.port, payload, currentSeqNum)
				currentSeqNum += 1
				payload = ''
		sendMsg = '00000end11111'
		gbnsender(self.sock, self.host, self.port, sendMsg,currentSeqNum)
		lastSeqNumSent = currentSeqNum
		f.close()



def main():
	host = sys.argv[1]
	port = 17777
	cliSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	
	cliSocket.bind(('',port)) 
	ackReceiver = receiver(sys.argv[1:], cliSocket)
	fileHandler = fileReader(sys.argv[1:],cliSocket)
	fileHandler.join()
	ackReceiver.join()
	if cliSocket:
		cliSocket.close()
		
if __name__ == '__main__':	
	main()	
