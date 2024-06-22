import socket
import struct 
import random
from datetime import datetime
#变量定义
HOST = '0.0.0.0'  # 服务器监听的地址，all
PORT = 12345      # 服务器监听的端口
buffer_size=1024 #缓冲区大小
time_out=0.1 #超时时间，100ms
drop_rate=0.05 #丢包率
ver=2 #版本
retrans=2 #重传次数
# 构造数据包
def construct_response(seq_no):#seq_no为客户端发送消息中提取
    send_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    response_content=send_time.encode() + b"221002422" + b'\x00' * (197 - len(send_time) - len(b"221002422"))
    #将 seq_no 和 ver 转换为 ASCII 字符串，确保长度
    seq_no_str = "{:02d}".format(seq_no).encode()  # 转换为两位数的字符串
    ver_str = "{:01d}".format(ver).encode()  # 转换为1位数的字符串
    return seq_no_str + ver_str + response_content
#绑定地址
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))
print("udp server is listening")
try:
    while True:
        data, client_address = server_socket.recvfrom(buffer_size)
        print(f"Received data from {client_address}")
        server_socket.settimeout(time_out)
        packet_type = data.decode().strip() #解码接收到的数据为字符串
        if packet_type=='syn':#连接的建立，三次挥手
            server_socket.sendto(("syn-ack").encode(), client_address)
            print("syn-ack be sent")
        elif packet_type=='ack':
            print("received ack")
        elif packet_type=='fin':#连接的关闭，四次挥手
            server_socket.sendto(("fin-ack").encode(), client_address)
            print("fin-ack be sent")
            server_socket.sendto(("fin").encode(), client_address)
            print("fin be sent")
        elif packet_type=='fin-ack':
            print("received fin-ack")
        else:#数据包
            #seq_no,ver = struct.unpack('!HB', data[:3])
            if len(data) >= 3:
                seq_no=int(data.decode('utf-8')[:2])  # 先解码为utf-8字符串，然后截取前两个字符并转换为整数
                ver=int(data.decode('utf-8')[2:3])
                if random.random() < drop_rate:
                    print(f"Dropping packet {seq_no} from {client_address}")
                    continue
                response=construct_response(seq_no)#构造消息
                server_socket.sendto(response, client_address)
                print(f"Sent response for packet {seq_no} to {client_address}")
except socket.timeout:
    print(f"Timeout with client {client_address}")
except KeyboardInterrupt:
    print("Server is shutting down.")
finally:
    server_socket.close() 