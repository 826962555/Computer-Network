import socket
import sys
import os
import random


def createMessage(msg_type, data):
    # 根据给定的消息类型和数据创建协议消息
    if data:
        if isinstance(data, str):
            data = data.encode()  # 如果data是字符串，转换为字节
        length = len(data)  # 数据长度
    else:
        length = 0
        data = b''  # 确保data是字节类型
        # 返回构造的消息
    return f"{msg_type:02d}".encode() + length.to_bytes(4, byteorder='big') + data


def parseMessage(data):
    # 解析协议消息，获取消息类型、长度和内容。
    msg_type = int(data[:2].decode()) # 解析消息类型
    length = int.from_bytes(data[2:6], byteorder='big') # 数据长度
    content = data[6:].decode() # 消息内容
    return msg_type, length, content


def main(server_ip, server_port, file_path, lmin, lmax, output_path):
    # 主函数处理文件传输和接收。
    if lmin > lmax:
        print("错误：最小块大小不能大于最大块大小")
        return

    server_port = int(server_port)  # 服务器端口
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建客户端套接字
    client_socket.connect((server_ip, server_port))  # 连接到服务器

    # 计算文件块大小并确定块数N
    total_size = os.path.getsize(file_path) # 文件总大小
    if total_size < lmin:
        print(f"错误：文件大小 {total_size} 小于最小块大小 {lmin}")
        client_socket.close()
        return

    block_sizes = []  # 有若干片，存储每块的大小
    remaining_size = total_size # 剩余文件大小

    while remaining_size > 0:
        if remaining_size < lmin:
            block_sizes.append(remaining_size)
            break
        size = random.randint(lmin, min(lmax, remaining_size)) # 随机生成块大小，满足任务要求的随机数
        block_sizes.append(size)
        remaining_size -= size

    number_of_blocks = len(block_sizes) # 分块的总数

    # 发送初始化请求，包括块数N
    init_data = number_of_blocks.to_bytes(4, byteorder='big') # 块数转换为字节
    init_request = createMessage(1, init_data) # 创建初始化消息
    client_socket.send(init_request) # 发送TCP连接请求
    response = client_socket.recv(1024) # 接收响应
    msg_type, _, _ = parseMessage(response) # 解析响应消息

    if msg_type != 2:
        print("连接确认失败")
        client_socket.close()
        return

    print(f"连接已确认，准备传输{number_of_blocks}个数据块")

    # 计算并显示文件中的字符总数
    with open(file_path, 'r', encoding='utf-8') as file:
        file_contents = file.read()
        total_characters = len(file_contents)
        print(f"文件中的总字符数: {total_characters}") # 文件字符总数

    reversed_content = [] # 存储反转后的文本块
    block_count = 0 # 记录块数

    with open(file_path, 'rb') as file:
        for size in block_sizes:
            data = file.read(size) # 读取块数据
            original_text = data.decode('utf-8') # 解码块数据
            request = createMessage(3, original_text) # 创建请求消息
            client_socket.send(request) # 发送请求
            response = client_socket.recv(1024)  # 响应请求
            _, _, reversed_data = parseMessage(response) # 解析响应数据
            block_count += 1
            print(f"第{block_count}块原文: {original_text}")
            print(f"第{block_count}块反转的文本: {reversed_data}")
            reversed_content.append(reversed_data) # 添加反转文本到列表

    # 将反转后的内容写入输出文件
    with open(output_path, 'w') as outfile:
        outfile.write(''.join(reversed_content))

    client_socket.close()


if __name__ == '__main__':
    if len(sys.argv) != 7:
        print("Usage: 缺少 python reversetcpclient.py文件 需要的 源IP 源端口号 目标文本路径 最小值 最大值 写入文本路径")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6])
