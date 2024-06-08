import socket
import select

def reverseText(text):
    # 反转文本字符串的操作 - 基于python列表
    return text[::-1]

def createMessage(msg_type, data):
    # 根据给定的消息类型和数据创建协议消息
    if data:
        length = len(data) # 数据长度
    else:
        length = 0
    # 如果 msg_type 小于 10，将在前面补零以确保始终有两位数字。之后将字符串编码为字节，这是因为网络通信通常是通过字节流进行的。
    return f"{msg_type:02d}".encode() + length.to_bytes(4, byteorder='big') + data.encode()

def parseMessage(data):
    # 解析协议消息，获取消息类型、长度和内容。
    msg_type = int(data[:2].decode()) # 消息类型
    length = int.from_bytes(data[2:6], byteorder='big') # 数据长度
    content = data[6:].decode() # 消息内容
    return msg_type, length, content
# 服务器ip地址，端口号
# server_ip = '127.0.0.1' # 以本地回环测试
server_ip = '192.168.237.1'
server_port = 9527
buffer_size = 1024

# 创建服务器socket，绑定地址，并开始监听
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(10)
server_socket.setblocking(0)  # 设置socket为非阻塞模式

inputs = [server_socket] # 输入socket列表
outputs = [] # 输出socket列表
message_queues = {}  # 消息队列字典

print("服务器启动在 {}:{}".format(server_ip, server_port))

try:
    while inputs:
        # 使用select方法监听输入、输出和异常状态的socket
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        # 处理可读socket
        for s in readable:
            if s is server_socket:
                # 处理新的连接
                client_socket, client_address = s.accept()
                print("新的连接来自 {}".format(client_address))
                client_socket.setblocking(0)  # 设置为非阻塞模式
                inputs.append(client_socket)   # 加入到监听列表
                message_queues[client_socket] = [] # 为新连接创建消息队列
                # 发送连接确认
                init_message = createMessage(2, "")  # 发送确认协议
                client_socket.send(init_message)
            else:
                # 读取数据
                data = s.recv(buffer_size)
                if data:
                    # 解析消息并处理
                    msg_type, length, content = parseMessage(data)
                    if msg_type == 3:   # 处理反向请求消息
                        print(f"接收到数据: reverseRequest:{length}:{content}")
                        reversed_data = reverseText(content)
                        response = createMessage(4, reversed_data)   # 创建反向答复消息
                        print(f"发送反转文本: {reversed_data.encode()}")
                        message_queues[s].append(response)
                        if s not in outputs:
                            outputs.append(s)
                else:
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    del message_queues[s]
        # 处理可写socket
        for s in writable:
            try:
                next_msg = message_queues[s].pop(0)
            except IndexError:
                # 没有消息可以发送
                outputs.remove(s)
            else:
                s.send(next_msg)

        for s in exceptional:
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()
            del message_queues[s]

finally:
    # 确保服务器socket最终关闭
    server_socket.close()
