import socket
import time
import statistics
from datetime import datetime

def start_client():
    # 客户端设置
    # server_ip = '127.0.0.1'  # 服务器IP地址 最开始是在本地回环测试
    server_ip = '192.168.237.1'  # 服务器IP地址
    server_port = 12345  # 服务器端口
    num_requests = 12  # 发送请求的总数
    timeout = 0.1  # 超时时间设置为100毫秒
    max_retries = 2  # 最大重试次数 重传2次后还是没有收到则丢弃

    # 创建UDP套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 设置SO_REUSEADDR允许地址重用
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 设置套接字的超时时间
    client_socket.settimeout(timeout)

    # 跟踪往返时间(RTT)和丢包情况
    rtts = [] # 列表存储
    received_packets = 0
    first_response_time = None  # 初始化开始时间变量
    last_response_time = None  # 初始化结束时间变量

    try:
        # 发送12个数据包
        for seq_no in range(1, num_requests + 1):
            attempts = 0
            while attempts <= max_retries:
                ver = 2  # 协议版本
                data = seq_no.to_bytes(2, 'big') + bytes([ver]) + b'X' * 200  # 构造数据包
                client_socket.sendto(data, (server_ip, server_port))
                print(f"尝试 {attempts + 1}: 已发送数据包: 序号 {seq_no}")

                try:
                    # 开始时间
                    start_time = time.time()
                    response, _ = client_socket.recvfrom(1024)
                    rtt = (time.time() - start_time) * 1000
                    rtts.append(rtt)
                    received_packets += 1

                    # 解析服务器时间
                    server_time_str = response[3:].decode()
                    server_time = datetime.strptime(server_time_str, '%Y-%m-%d %H:%M:%S')
                    if first_response_time is None:
                        first_response_time = server_time
                    last_response_time = server_time
                    print(f"序号 {seq_no}, RTT: {rtt:.2f} 毫秒")
                    break  # 接收成功，跳出循环
                except socket.timeout:
                    print(f"序号 {seq_no}, 尝试 {attempts + 1}, 请求超时")
                    attempts += 1
                    if attempts > max_retries:
                        print(f"序号 {seq_no}, 经过 {max_retries} 次重试后放弃")

        # 模拟TCP连接释放
        print("开始连接释放...")
        client_socket.sendto(b'FIN', (server_ip, server_port))
        print("已发送 FIN")
        response, _ = client_socket.recvfrom(1024)
        if response.decode() == 'FIN-ACK':
            print("收到 服务器发来的FIN-ACK, 正在发送 ACK...")
            client_socket.sendto(b'ACK', (server_ip, server_port))
            print("最终 ACK 已发送, 连接现在关闭。")

    finally:
        client_socket.close()
        print("客户端套接字已关闭。")

        # 输出统计信息
        if rtts:
            print(f"\n已接收 UDP 数据包数量: {received_packets}")
            print(f"丢包率: {(1 - received_packets / num_requests) * 100:.2f}%")
            print(f"最大 RTT: {max(rtts):.2f} 毫秒, 最小 RTT: {min(rtts):.2f} 毫秒, 平均 RTT: {sum(rtts) / len(rtts):.2f} 毫秒")
            if len(rtts) > 1:
                print(f"RTT 标准差: {statistics.stdev(rtts):.2f}")
            else:
                print("RTT 标准差: 不适用（需要至少两个数据点）")
            if first_response_time and last_response_time:
                total_response_time = (last_response_time - first_response_time).total_seconds()
                print(f"服务器整体响应时间: {total_response_time} 秒")

if __name__ == "__main__":
    start_client()
