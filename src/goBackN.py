
import socket # Import socket module
import sys
from collections import namedtuple
import pickle
#from _thread import *
import threading
import inspect
import time
from _socket import SOCK_DGRAM,SOCK_STREAM,AF_INET
from signal import *
from socket import *

DATA_TYPE = 0b101010101010101
DATA_SIZE = 64   #need to be modified
s = socket(AF_INET,SOCK_DGRAM)
s.bind(('',7000))
data_pkt = namedtuple('data_pkt', 'seq_num checksum data_type data')
ack_pkt = namedtuple('ack_pkt', 'seq_num zero_field data_type')
N = 0  # window size
MSS = 0 # maximum segment size
ACK = 0 # ACK received from serverAshwin.
num_pkts_sent = 0
num_pkts_acked = 0
seq_num = 0

mss_chunks=[]
rfc_file = '' 
window_low = 0
window_high = int(N)-1
total_pkts = 0
RTT = 2
pkts = []
done_transmitting = 0
starttime = 0
stoptime= 0

ack_socket = socket(AF_INET,SOCK_DGRAM)  # UDP Foo
host = socket.gethostname()
ack_port_num = 62223
ack_socket.bind(('', ack_port_num))
lock = threading.RLock()

def between(a, b,c):
#Return true if a <= b < c circularly; false otherwise.
    if (((a <= b) and (b < c)) or ((c < a) and (a <= b)) or ((b < c) and (c < a))):
        return True;
    else:
        return False;

def create_packet(chunk,seq_num,ack):
    segment = str(seq_num)+" "+str(ack)+" "+chunk
    return segment
def send_data(sequence_number, expected_sequence_number,mss_chunks):
    global N
    global s
    chunk = mss_chunks[sequence_number]
    seq_num = sequence_number
    ack = (expected_sequence_number + N) % (N + 1)
    segment = create_packet(chunk,seq_num,ack);
    s.sendto(segment.encode('utf-8'),('127.0.0.1', 7000))
    #to physical layer(&s);
    #start timer(frame nr);
    

    
def parse_command_line_arguments():
    host = sys.argv[1]
    port = sys.argv[2]
    rfc_file = sys.argv[3]
    my_window_size = sys.argv[4]
    my_mss = sys.argv[5]
    return host, int(port), rfc_file, int(my_window_size), int(my_mss)

def get_mss_chunks(rfc_file):
    global mss_chunks
    global MSS
    try:
        with open(rfc_file, 'rb') as f:
            while True:
                data = f.read(int(MSS))  # Read the file MSS bytes each time Foo
                if data:
                    mss_chunks.append(data)
                else:
                    break
    except:
        sys.exit("Error while opening file.")
    return mss_chunks
        
def ftp_handler(s,host,port):
    global N,MSS,rfc_file
    global mss_chunks
    mss_chunks = get_mss_chunks(rfc_file)
    
    
    
global N
global MSS
global starttime
starttime = time.time()
host, port, rfc_file, N, MSS = parse_command_line_arguments()
  # Create a socket object

print("Host:", host)
port = 7735 
global window_high
window_high = int(N)-1
threading.Thread(target = ftp_handler,args=(s,host,port)).start()
s.close()  # Close the socket when done
