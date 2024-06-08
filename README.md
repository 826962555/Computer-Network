# TCP socket programming

这个项目包含了一个TCP客户端和服务器的实现，能够进行文本的反转处理，并通过网络传输数据块。

## 功能描述

- **服务器** (reversetcpserver.py): 监听特定的端口，接收客户端的连接和文本数据，将文本反转后返回给客户端。
- **客户端** (reversetcpclient.py): 连接到服务器，发送文件内容进行反转，并接收处理后的数据。

## 运行环境

​	项目运行环境需支持Python 3。

## 安装指南

1. 将项目文件下载到您的本地系统。
2. 确保Python版本为3.x。

## 使用说明

### 服务器端

1. 打开终端或命令提示符。
2. 切换到包含`reversetcpserver.py`的目录。
3. 运行以下命令来启动服务器：

```python
python reversetcpserver.py
```

服务器默认绑定到`192.168.237.1`的`12345`端口。您可以在脚本中修改成你的IP地址和端口号。

### 客户端

1. 打开另一个终端窗口。
2. 切换到包含`reversetcpclient.py`的目录。
3. 使用以下命令格式运行客户端：

```python
python reversetcpclient.py <server_ip> <server_port> <file_path> <min_block_size> <max_block_size> <output_path>
```

参数说明：

- `<server_ip>`: 服务器的IP地址。
- `<server_port>`: 服务器的端口号。
- `<file_path>`: 要发送给服务器的文件路径。
- `<min_block_size>` 和 `<max_block_size>`: 数据块大小的范围，单位为字节。
- `<output_path>`: 反转后文本保存的文件路径。

基于本例：使用以下格式在虚拟机中运行客户端

```python
python3 reversetcpclient.py 192.168.237.1 12345 /home/wjs/桌面/test.txt 1 10 /home/wjs/桌面/new.txt
```

## 注意事项

确保客户端与服务器在相同或互通的网络中。对于防火墙或网络安全设置可能需要相应的调整。

## 作者

计算机22-1王继舜