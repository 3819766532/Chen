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

HTML_B64 = "/Td6WFoAAATm1rRGAgAhARYAAAB0L+Wj4A/9AR5dAD2eQuiFEaqjI4BxKgoHEcJ3wCgBIQoRbQACJj0Zb2NtcHJlc3MAAAAAAAAAAAAAAAAAAAAAAAAAABtYWluAACmzQAAo7gAAdwGAA7IqwsAA/scF7AEARQAAANxq7Q0bN+Qy7bE5K7z1QwAALRtYFwABAEAAJ7rYBQABAEAAJ7rYBQA=