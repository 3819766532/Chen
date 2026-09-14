# ============================================================
# 免责声明：本代码仅供学习交流使用，请勿用于非法用途。
# 使用本代码所产生的一切后果由使用者自行承担，
# 作者不承担任何法律责任。
# ============================================================

import requests
import time

def check_stock(code):
    # 判断是哪里的股票
    prefix = 'sh' if code.startswith('6') else 'sz'
    url = f"https://hq.sinajs.cn/list={prefix}{code}"
    
    # 调用新浪进行查询，必须带上这个头，否则新浪会拒绝访问
    headers = {
        'Referer': 'https://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        resp = requests.get(url, headers=headers)
        # 新浪接口使用的是 GBK 编码，必须转码，否则中文会乱码
        resp.encoding = 'gbk' 
        
        text = resp.text
        if '=' not in text:
            return "未找到该股票数据"
            
        # 解析返回的字符串数据
        data = text.split('"')[1].split(',')
        
        name = data[0]
        current_price = data[3]
        change_percent = data[32] # 涨跌幅
        high = data[4]
        low = data[5]
        volume = data[8] # 成交量（股）
        amount = data[9] # 成交额（元）
        
        print(f"--- {name} ({prefix}{code}) 实时行情 ---")
        print(f"当前价格: {current_price}")
        print(f"涨跌幅: {change_percent}%")
        print(f"最高: {high} | 最低: {low}")
        print(f"成交量: {volume} 股")
        print(f"成交额: {amount} 元")
        print("--------------------------------")
        
    except Exception as e:
        print(f"查询出错: {e}")

# 查询盈新发展股票代码 (000620)
check_stock('000620')