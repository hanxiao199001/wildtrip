#!/usr/bin/env python3
"""简单的 HTTP 服务器，支持中文文件名"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import os

class ChineseHTTPRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        """处理 URL 编码的路径"""
        # 解码 URL 编码
        path = urllib.parse.unquote(path)
        return super().translate_path(path)

if __name__ == '__main__':
    os.chdir('/root/clawd/wildtrip/web')
    server = HTTPServer(('0.0.0.0', 8080), ChineseHTTPRequestHandler)
    print('✅ Web 服务器启动成功！')
    print('📍 http://localhost:8080/')
    print('📂 目录: /root/clawd/wildtrip/web')
    print('按 Ctrl+C 停止服务器')
    server.serve_forever()
