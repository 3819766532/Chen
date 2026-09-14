# ============================================================
# 免责声明：本代码仅供学习交流使用，请勿用于非法用途。
# 使用本代码所产生的一切后果由使用者自行承担，
# 作者不承担任何法律责任。
# ============================================================

import requests
from bs4 import BeautifulSoup

# 换用百度作为测试目标，国内访问极快且稳定
url = "https://www.baidu.com"

# 添加 headers 模拟浏览器，防止被简单的反爬机制拦截
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"正在尝试连接: {url} ...")

try:
    response = requests.get(url, headers=headers, timeout=10)
    
    # 检查是否成功 (200 代表成功)
    if response.status_code == 200:
        print("✅ 连接成功！")
        
        # 尝试解析网页标题
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string
        
        print(f"📄 网页标题是: {title}")
        print("🎉 恭喜！你的爬虫环境 (requests + bs4) 已经完全就绪！")
        
    else:
        print(f"⚠️ 连接上了，但服务器返回了错误码: {response.status_code}")

except Exception as e:
    print(f"❌ 发生错误: {e}")