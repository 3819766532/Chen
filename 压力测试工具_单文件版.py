# ============================================================
# 免责声明：本代码仅供学习交流使用，请勿用于非法用途。
# 使用本代码所产生的一切后果由使用者自行承担，
# 作者不承担任何法律责任。
# ============================================================

# -*- coding: utf-8 -*-
"""
短信/邮箱测压工具 - Python 单文件版
内嵌 HTML 页面，启动本地 HTTP 服务后自动打开浏览器
"""

import base64
import lzma
import os
import sys
import time
import tempfile
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

HTML_B64 = "/Td6WFoAAATm1rRGAgAhARYAAAB0L+Wj4A/9AR5dAD2eQuiFEaqjI4BxKgoHEcJ3wCgBIQoRbQACJj0Zb2NtcHJlc3MAAAAAAAAAAAAAAAAAAAAAAAAAABtYWluAACmzQAAo7gAAdwGAA7IqwsAA/scF7AEARQAAANxq7Q0bN+Qy7bE5K7z1QwAALRtYFwABAEAAJ7rYBQABAEAAJ7rYBQA="


def extract_html(target_dir):
    compressed = base64.b64decode(HTML_B64)
    html_data = lzma.decompress(compressed)
    html_path = os.path.join(target_dir, "index.html")
    with open(html_path, "wb") as f:
        f.write(html_data)
    return html_path


def open_browser(port):
    time.sleep(1.0)
    url = "http://localhost:%d/index.html" % port
    print("[浏览器] 正在打开:", url)
    webbrowser.open(url)


def main():
    port = 8765
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("[错误] 无效端口号:", sys.argv[1], "，使用默认端口", port)

    work_dir = tempfile.mkdtemp(prefix="stress_test_")
    print("[工作目录]", work_dir)
    html_path = extract_html(work_dir)
    print("[页面文件]", html_path)
    os.chdir(work_dir)

    server_address = ("", port)
    try:
        httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    except OSError as e:
        print("[错误] 端口", port, "被占用:", e)
        print("[提示] 可以指定其他端口: python 压力测试工具.py 8888")
        input("按回车键退出...")
        return

    print("=" * 50)
    print("  短信/邮箱测压工具 - Python 单文件版")
    print("=" * 50)
    print("[服务] 本地地址: http://localhost:%d/index.html" % port)
    print("[提示] 按 Ctrl+C 停止服务")
    print("=" * 50)

    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[服务] 已停止")
        httpd.server_close()


if __name__ == "__main__":
    main()