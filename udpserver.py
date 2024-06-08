import socket
import random
import threading
from datetime import datetime


def handleClient(server_socket, addr, data):
    # 获取当前线程的名称，用于多客户端，在服务器的角度区分进程
    thread_name = threading.current_thread().name
    loss_probability = 0.25  # 丢包概率设为25%
    decoded_data = data.decode()
    # 在连接释放时的服务器交互
    if decoded_data == 'FIN':
        print(f"{thread_name} - 收到 FIN 从 {addr}，发送 FIN-ACK...")
        server_socket.sendto(b'FIN-ACK', addr)  # 收到FIN消息，回复FIN-ACK
        return

    if decoded_data == 'ACK':
        print(f"{thread_name} - 收到最终的 ACK 从 {addr}，连接现在关闭。")
        return  # 收到最终的ACK消息，关闭连接

    # 解析序列号和版本号
    seq_no, ver = int.from_bytes(data[:2], 'big'), data[2]
    print(f"{thread_name} - 收到数据包从 {addr}：序号 {seq_no}，版本 {ver}")

    # 根据设置的丢包概率随机丢弃一些包 - 模拟网络波动
    if random.random() < loss_probability:
        return

    # 将服务器时间附加到响应中
    server_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response = data[:3] + server_time.encode()
    server_socket.sendto(response, addr)
    print(f"{thread_name} - 响应发送给客户端 {addr}，包含服务器时间: {server_time}")


def startServer():
    server_ip = '192.168.237.1'  # 服务器的IP地址 服务器在本机，客户端在虚拟机
    # server_ip = '127.0.0.1'  # 服务器的IP地址 本地测试loopback
    server_port = 12345  # 服务器的端口号 客户端的端口号是随机分配

    # 创建UDP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((server_ip, server_port))

    print(f"服务器正在运行在 {server_ip}:{server_port}")

    try:
        while True:
            # 从客户端接收数据
            data, addr = server_socket.recvfrom(1024)
            thread = threading.Thread(target=handleClient, args=(server_socket, addr, data), name=f"Thread-{addr}")
            thread.start()
    finally:
        server_socket.close()  # 最终关闭服务器套接字
        print("服务器套接字已关闭。")


if __name__ == "__main__":
    startServer()
