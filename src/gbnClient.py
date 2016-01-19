import sys
import threading
import struct
import socket
import random

def validateChecksum(payload, receivedChecksum):
	sum16 = 0
	for i in range(0, len(payload), 2):
		if i+1 < len(payload):
			chunk = ord(payload[i]) + (ord(payload[i+1]) << 8)		#To take 16 bits at a time
			tempSum = sum16 + chunk
			sum16 = (tempSum & 0xffff) + (tempSum >> 16)		#To ensure 16 bits
	computedCheckSum = sum16 & 0xffff 
	validate = computedCheckSum & receivedChecksum
	if validate != 0:
		return False
	else:
		return True

def parseMessage(message):
	received_header = message[0:8]
	seq = struct.unpack('=I',received_header[0:4])
	checksum = struct.unpack('=H',received_header[4:6])
	ack = struct.unpack('=H',received_header[6:])
	payload = message[8:]	
	data = payload.decode('ISO-8859-1')
	return seq, checksum, ack, data

def createAckPacket(acked_seq_num):
	seq 		 = struct.pack('=I', acked_seq_num)	
	checksum 	 	 = struct.pack('=H', 0)
	ack = struct.pack('=H',43690)		#ACK INDICATOR - 1010101010101010[INT 43690]
	ack_packet = seq+checksum+ack
	return ack_packet


def main():
	serverPort = int(sys.argv[1])			
	myPort = 7777				
	rfcFileName = sys.argv[3]	
	p = float(sys.argv[4])					
	udpSocket  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	
	udpSocket.bind(('',myPort))
	seqNumExpected = 0 
	f = open(rfcFileName,'wb')
	flag = True
	while flag:	
		receivedMsg, sender_addr = udpSocket.recvfrom(1024)			
		receivedSeqNum, checksum, ack, data = parseMessage(receivedMsg)
		if random.uniform(0,5) > p:							
			print('[Expected Sequence Number : ',seqNumExpected,' | Received Sequence Number : ',receivedSeqNum[0])
			if seqNumExpected != int(receivedSeqNum[0]):
				print('Packet received out of order. Discarding...')
			else :
				isValidChecksum = validateChecksum(data, int(checksum[0]))
				if isValidChecksum == False:
					print('Received checksum is incorrect. Discarding...')
				else :
					if data == '00000end11111':	
						flag = False
						ackPacket = createAckPacket(int(receivedSeqNum[0]))
						udpSocket.sendto(ackPacket,sender_addr)
					else :					
						f.write(data.encode('ISO-8859-1'))
						ackPacket = createAckPacket(int(receivedSeqNum[0]))
						udpSocket.sendto(ackPacket,sender_addr)
					seqNumExpected += 1
		else:
			print('Discarding Received Sequence Number = '+str(receivedSeqNum[0]) + ' as packet loss...')
	f.close()
	print('RFC downloaded successfully. Switching back to main menu')
	udpSocket.close()	
if __name__ == '__main__':	
	main()