import socket
import struct 
import time   
import argparse
import statistics
from datetime import datetime
#变量定义
buffer_size=1024 #缓冲区大小
time_out=0.1 #超时时间，100ms
ver=2 #版本
retrans=2 #重传次数
#连接建立与释放的 消息发送与接收
def send_packet(client_socket, server_address, packet_type):
    packet=packet_type.encode()#syn,syn-ack,ack,fin,fin-ack
    client_socket.sendto(packet, server_address)
def wait_server_response(client_socket, expected_type):
    client_socket.settimeout(time_out)
    try:
        data,_=client_socket.recvfrom(buffer_size)
        received_type=data.decode().strip()
        if received_type==expected_type:
            return True
    except socket.timeout:
        print("Timeout waiting for response")
    return False
#构造数据包并发送给服务器
def mysend(seq_no, client_socket ,server_address):
    send_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")#精确到微妙
    other_content = send_time.encode() + b"221002422" + b'\x00' * (197 - len(send_time) - len(b"221002422"))
    #将 seq_no 和 ver 转换为 ASCII 字符串,确保长度
    seq_no_str = "{:02d}".format(seq_no).encode()  # 转换为两位数的字符串
    ver_str = "{:01d}".format(ver).encode()  # 转换为1位数的字符串
    packet = seq_no_str + ver_str + other_content
    client_socket.sendto(packet, server_address)#发送消息
#主函数
def main(serverIP, serverPort,packetsNum):
    client_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #三次握手
    send_packet(client_socket, (serverIP, serverPort), "syn")#发送syn
    print("syn be sent")
    if wait_server_response(client_socket, "syn-ack"): #等待syn-ack
        send_packet(client_socket, (serverIP, serverPort), "ack")  # 发送ack
        print("ack be sent")
    else:
        print("Fail connection")#建立连接失败
        return
    send_times={}#记录每个序列号的发送时间
    server_response_times = []#记录每次服务器的回应时间
    received_packets=0#收到的数据包数量
    rtt_values=[]#记录所有的rtt值
    #发送数据包
    for seq_no in range(1,packetsNum+1):
        my_retrans=0#当前重传次数
        is_received=False #标记是否收到回应
        while not is_received and my_retrans<=retrans:
            send_times[seq_no]=time.perf_counter()#时间更加精确
            mysend(seq_no, client_socket, (serverIP, serverPort))#发送数据包
            client_socket.settimeout(time_out)  #设置响应超时时间
            try:
                data, server_address = client_socket.recvfrom(buffer_size)
                received_packets+=1#收到响应
                received_time=time.perf_counter()
                rtt = (received_time - send_times[seq_no]) * 1000#转换为毫秒
                rtt_values.append(rtt)#加入列表
                print(f"Sequence no: {seq_no}, {server_address[0]}:{server_address[1]}, RTT: {rtt:.2f}ms")
                response_time_str=data[3:24].decode() #从服务器响应数据中提取系统响应时间
                response_time=datetime.strptime(response_time_str, "%Y-%m-%d %H:%M:%S.%f")
                response_time= time.mktime(response_time.timetuple()) + response_time.microsecond / 1e6
                server_response_times.append(response_time)#存储回应时间
                is_received=True
                break
            except socket.timeout:#超时
                my_retrans+=1
                print(f"Sequence {seq_no}, request timeout")
        if my_retrans > retrans:#达到最大重传次数
           print(f"Sequence {seq_no} failed after {my_retrans} retransmissions, moving to next packet.")
           continue
    #发送完毕，打印汇总信息
    print("\n-----【汇总信息】-----")
    print(f"(1) Received UDP packets: {received_packets}")
    print(f"(2) Packet loss rate: {100 * (1 - received_packets / packetsNum):.2f}%")
    if received_packets > 0:
        print(f"(3)  Max RTT: {max(rtt_values):.2f}ms")
        print(f"     Min RTT: {min(rtt_values):.2f}ms")
        print(f"     Avg RTT: {statistics.mean(rtt_values):.2f}ms")
        print(f"     RTT标准差Standard deviation RTT: {statistics.stdev(rtt_values):.2f}ms")
    else:
        print("(3) No RTT data available (no packets received)")
    if server_response_times:
        #计算服务器的整体响应时间
        first_response=server_response_times[0]
        last_response=server_response_times[-1]
        #print(f"第一次{first_response}")
        #print(f"最后一次{last_response}")
        server_response_timedelta=last_response-first_response
        #server_response_time=int(server_response_timedelta.total_seconds()*1000)#转换为毫秒
        server_response_time=server_response_timedelta* 1e6  #微秒
        if server_response_time==0:
            print(f"(4) 整体响应时间: {sum(rtt_values):.2f}ms")
        else:
            print(f"(4) 整体响应时间: {server_response_time}us")
    else:
        print("(4) No response time data available (no packets received)")
    # 四次挥手,关闭连接
    send_packet(client_socket, (serverIP, serverPort), "fin") #发送fin
    if wait_server_response(client_socket, "fin-ack"): #等待fin-ack
        print("Received fin-ack from server.")
        if wait_server_response(client_socket, "fin"): #等待服务器端发送fin
            print("Received fin from server.")
            send_packet(client_socket, server_address, "fin-ack") #发送fin-ack
            print("Connection closed.")
        else:
            print("Error during connection close.")
    else:
        print("Error during connection close.")
    client_socket.close()
#命令行方式下，输入地址与端口
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="udpclient")
    parser.add_argument('--serverIP', type=str, required=True, default='192.168.10.130',help='Server IP address')
    parser.add_argument('--serverPort', type=int, required=True, default=12345,help='Server port number')
    parser.add_argument('--packetsNum', type=int, default=12, help='Number of packets to send (default: 12)')
    args = parser.parse_args()#解析命令行参数  

    main(args.serverIP, args.serverPort,args.packetsNum)