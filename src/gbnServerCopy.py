import sys

import socket

import struct

import random

import threading



def parseMsg(msg):					#Parsing the Message received from client

	#print ('ENtered PArsedmsg')

	header = msg[0:8]

	data = msg[8:]	

	sequenceNum = struct.unpack('=I',header[0:4])

	#print(sequenceNum)		

	checksum = struct.unpack('=H',header[4:6])

	#print(checksum)

	identifier = struct.unpack('=H',header[6:])

	#print (identifier)

	#dataDecoded = data.decode('UTF-8')	

	dataDecoded = data.decode('ISO-8859-1')

	#print(dataDecoded)

	#print (dataDecoded)

	return sequenceNum, checksum, identifier, dataDecoded

	

def formAckPackets(seqAcked):

	seqNum 		 = struct.pack('=I', seqAcked)	#SEQUENCE NUMBER BEING ACKED	

	zero16 	 	 = struct.pack('=H', 0)

	ackIndicator = struct.pack('=H',43690)		#ACK INDICATOR - 1010101010101010[INT 43690]

	ackPacket = seqNum+zero16+ackIndicator

	return ackPacket



def verifyChecksum(data, checksum):

	sum = 0

	

	for i in range(0, len(data), 2):

		if i+1 < len(data):

			data16 = ord(data[i]) + (ord(data[i+1]) << 8)		#To take 16 bits at a time

			interSum = sum + data16

			sum = (interSum & 0xffff) + (interSum >> 16)		#To ensure 16 bits

	currChk = sum & 0xffff 

	result = currChk & checksum

	

	if result == 0:

		return True

	else:

		return False

	

def main():

	#port filename probability

	

	uport = int(sys.argv[1])			#Upload port to send ACKs to
	
	#port_bind = int(sys.argv[2])		#PORT ON WHICH SERVER WILL ACCEPT UDP PACKETS
	port_bind = 7777				#PORT ON WHICH SERVER WILL ACCEPT UDP PACKET

	filename = sys.argv[3]		#NAME OF THE NEW FILE CREATED

	prob = float(sys.argv[4])	#PACKET DROP PROBABILITY

	expSeqNum = 0				

	flag = True

	

	soc  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	

	#host = socket.gethostname()

	soc.bind(('',port_bind)) 

	

	fileHandler = open(filename,'wb')

	

	while flag:	

		print ('Before receiving the data')

		receivedMsg, sender_addr = soc.recvfrom(1024)			#Receive packets sent by client

		print ('After receiving the data')

		sequenceNum, checksum, identifier, data = parseMsg(receivedMsg)

		print ('parsed the received msg')

		#print(prob)

		if random.uniform(0,10) > prob:							#PACKET MAY BE DROPPED BASED ON RANDOM VALUE

			print(expSeqNum,sequenceNum[0])

			if expSeqNum == int(sequenceNum[0]):				#If the expected Packet

				print('received correct seq number')

				chksumVerification = verifyChecksum(data, int(checksum[0]))

				if chksumVerification == True:

					print('Checksum is correct')

					if data != '00000end11111':					#If not the END Packet

						#print('Not end of packet')

						fileHandler.write(data.encode('ISO-8859-1'))					#Write to FILE

						ackPacket = formAckPackets(int(sequenceNum[0]))		#Generating ACK Packet

						#print('sending packet')

						soc.sendto(ackPacket,sender_addr)					#Sending ACK

					else:

						flag = False
						ackPacket = formAckPackets(int(sequenceNum[0]))		#Generating ACK Packet

						#print('sending packet')

						soc.sendto(ackPacket,sender_addr)					#Sending ACK

					expSeqNum += 1

		else:

			print('PACKET LOSS, SEQUENCE NUMBER = '+str(sequenceNum[0]))	#Packet dropped if randomValue <= probability

				

			

	fileHandler.close()

	print('File Received Successfully at the Server')

	soc.close()	

	

if __name__ == '__main__':	

	main()