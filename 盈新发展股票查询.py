# ============================================================
# 免责声明：本代码仅供学习交流使用，请勿用于非法用途。
# 使用本代码所产生的一切后果由使用者自行承担，
# 作者不承担任何法律责任。
# ============================================================

import requests
import time

def check_stock(code):
    prefix = 'sh' if code.startswith('6') else 'sz'
    url = f"https://hq.sinajs.cn/list={prefix}{code}"
    headers = {
        'Referer': 'https://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        resp = requests.get(url, headers=headers)
        resp.encoding = 'gbk'
        text = resp.text
        if '=' not in text:
            return "未找到该股票数据"
        data = text.split('"')[1].split(',')
        name = data[0]
        current_price = data[3]
        change_percent = data[32]
        high = data[4]
        low = data[5]
        volume = data[8]
        amount = data[9]
        print(f"--- {name} ({prefix}{code}) 实时行情 ---")
        print(f"当前价格: {current_price}")
        print(f"涨跌幅: {change_percent}%")
        print(f"最高: {high} | 最低: {low}")
        print(f"成交量: {volume} 股")
        print(f"成交额: {amount} 元")
        print("--------------------------------")
    except Exception as e:
        print(f"查询出错: {e}")

check_stock('000620')
