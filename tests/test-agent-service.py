# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/4/29
@Software: PyCharm
@disc:
======================================="""
import http.server
import logging
import socketserver
from socket import socket, AF_INET, SOCK_STREAM
from urllib.parse import urlparse
import socks

from PFlowC.utils import logger

# 设置代理
socks.set_default_proxy(socks.SOCKS5, '10.2.1.0', 7890)
socket.socket = socks.socksocket


class SimpleProxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 解析请求的URL以获取目标主机和路径
        url = urlparse(self.path)
        print("GET url:", url)
        proxy_path = url.path
        if url.query:
            proxy_path += '?' + url.query
        try:
            print("proxy_path:", proxy_path)
            # 创建到目标服务器的连接
            conn = http.client.HTTPConnection(url.netloc)
            conn.request('GET', proxy_path)
            res = conn.getresponse()

            # 将响应头和内容转发回客户端
            self.send_response(res.status)
            for header, value in res.getheaders():
                self.send_header(header, value)
            self.end_headers()
            self.wfile.write(res.read())
            print('%s %s %s' % (res.status, proxy_path, res.reason))
        except Exception as e:
            print('%s %s %s' % (e.__class__.__name__, proxy_path, res))
            self.send_error(500, str(e))

    def do_CONNECT(self):
        host, port = self.path.split(':')
        print("CONNECT %s:%s" % (host, port))
        # 建立与目标HTTPS服务器的连接
        try:
            tunnel_socket = socket(AF_INET, SOCK_STREAM)
            tunnel_socket.connect((host, int(port)))
            logging.info("Connected to %s:%s" % (host, port))
            # 发送连接成功的响应给客户端
            self.send_response(200, 'Connection Established')
            self.end_headers()

            # 开始数据转发
            self.connection = tunnel_socket
            self.handle_tunnel()
        except Exception as e:
            self.send_error(502, str(e))  # Bad Gateway

    def handle_tunnel(self):
        # 数据转发循环
        while True:
            client_data = self.rfile.readline()
            if not client_data:
                logging.error("[连接失败] {}".format(self.path))
                break
            self.connection.send(client_data)
            logging.info("[发送数据成功] {} {}".format(self.path, client_data))
            server_data = self.connection.recv(4096)
            if not server_data:
                logging.error("[目标服务器异常响应] {} [{}]".format(self.path, server_data))
                break
            logging.info("[获取数据成功] {} {}".format(self.path, server_data))
            self.wfile.write(server_data)


if __name__ == '__main__':
    logger.init("agent-service", console_level=logging.INFO)
    port = 8380
    # 监听本地的8080端口
    with socketserver.TCPServer(("", port), SimpleProxy) as httpd:
        print("Serving at port", port)
        httpd.serve_forever()
