# ============================================================
# 免责声明：本代码仅供学习交流使用，请勿用于非法用途。
# 使用本代码所产生的一切后果由使用者自行承担，
# 作者不承担任何法律责任。
# ============================================================

import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import re
import json
import time

REQUIRED_LIBS = ['requests']
MISSING_LIBS = []

def check_and_install_dependencies():
    global MISSING_LIBS
    for lib in REQUIRED_LIBS:
        try:
            __import__(lib)
        except ImportError:
            print(f"检测到缺少库: {lib}，正在尝试自动安装...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])
                print(f"成功安装: {lib}")
            except Exception as e:
                print(f"自动安装失败: {lib}。请手动执行: pip install {lib}")
                MISSING_LIBS.append(lib)

check_and_install_dependencies()

try:
    import requests
except ImportError:
    requests = None

class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A股搜索")
        self.font_size_base = 12
        self.row_height = 40
        top_frame = tk.Frame(root, bg="#f0f0f0", pady=5)
        top_frame.pack(fill=tk.X, padx=5)
        tk.Label(top_frame, text="代码/拼音:", bg="#f0f0f0", font=("Arial", self.font_size_base)).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar(value="")
        self.entry = tk.Entry(top_frame, textvariable=self.search_var, font=("Arial", self.font_size_base + 2))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entry.bind("<Return>", lambda e: self.trigger_search())
        list_frame = tk.Frame(root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        columns = ("code", "name")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("code", text="代码")
        self.tree.heading("name", text="名称")
        self.tree.column("code", width=120, anchor=tk.CENTER)
        self.tree.column("name", width=200, anchor=tk.CENTER)
        style = ttk.Style()
        style.configure("Treeview", rowheight=self.row_height, font=("Arial", self.font_size_base))
        style.configure("Treeview.Heading", font=("Arial", self.font_size_base, "bold"), background="yellow")
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<Double-1>", self.on_item_click)
        self.tree.bind("<ButtonRelease-1>", self.on_item_click)
        init_status = "准备就绪 | 请输入代码或拼音后按回车"
        if MISSING_LIBS:
            init_status = f"警告: 缺少库 [{', '.join(MISSING_LIBS)}]"
        elif requests is None:
            init_status = "错误: 网络库加载失败"
        self.status_var = tk.StringVar(value=init_status)
        status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 10))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.after_id = None
        self.root.after(100, self.force_fullscreen_and_resize)

    def force_fullscreen_and_resize(self):
        try:
            try:
                self.root.state('zoomed')
            except:
                pass
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            if sw < 300: sw = 1080
            if sh < 300: sh = 1920
            self.root.geometry(f"{sw}x{sh}+0+0")
            calculated_row_height = int(sh / 25)
            self.row_height = max(35, min(60, calculated_row_height))
            if sw > 600:
                self.font_size_base = 14
                col_code_w = int(sw * 0.25)
                col_name_w = int(sw * 0.70)
            else:
                self.font_size_base = 12
                col_code_w = int(sw * 0.35)
                col_name_w = int(sw * 0.60)
            self.tree.column("code", width=col_code_w)
            self.tree.column("name", width=col_name_w)
            style = ttk.Style()
            style.configure("Treeview", rowheight=self.row_height, font=("Arial", self.font_size_base))
            style.configure("Treeview.Heading", font=("Arial", self.font_size_base, "bold"))
            self.entry.config(font=("Arial", self.font_size_base + 2))
        except Exception as e:
            print(f"布局适配出错: {e}")

    def trigger_search(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.after_id = self.root.after(400, self.start_search_thread)

    def start_search_thread(self):
        if requests is None:
            self.status_var.set("错误: 缺少 requests 库，无法搜索")
            return
        keyword = self.search_var.get().strip()
        if not keyword:
            self.tree.delete(*self.tree.get_children())
            self.status_var.set("准备就绪")
            return
        self.status_var.set(f"正在搜索: {keyword}...")
        t = threading.Thread(target=self.search_stock, args=(keyword,), daemon=True)
        t.start()

    def search_stock(self, keyword):
        results = {}
        try:
            url = f"https://smartbox.gtimg.cn/s3/?t=all&q={keyword}&v=2"
            resp = requests.get(url, timeout=5)
            resp.encoding = 'utf-8'
            text = resp.text
            matches = re.findall(r'\^([a-z]{2}\d{6})\^([^:^]+)\^', text)
            for code, name in matches:
                if name and len(name) < 15:
                    results[code] = name.strip()
        except Exception as e:
            print(f"腾讯接口错误: {e}")
        if len(results) < 5:
            try:
                url_em = f"http://searchapi.eastmoney.com/api/suggest/get?input={keyword}&type=14&token=D43BF722C8E33BDC906FB84D85E326E8&count=10"
                resp_em = requests.get(url_em, timeout=5)
                data_em = resp_em.json()
                if data_em.get('QuotationCodeTable'):
                    for item in data_em['QuotationCodeTable'].get('Data', []):
                        code = item.get('Code', '')
                        name = item.get('Name', '')
                        market = item.get('MktNum', '')
                        if market == '0': full_code = f"sz{code}"
                        elif market == '1': full_code = f"sh{code}"
                        else: full_code = code
                        if full_code and name:
                            results[full_code] = name
            except Exception as e:
                print(f"东财接口错误: {e}")
        self.root.after(0, self.update_list, results)

    def update_list(self, data_dict):
        self.tree.delete(*self.tree.get_children())
        count = 0
        for code, name in data_dict.items():
            self.tree.insert("", tk.END, values=(code, name))
            count += 1
        if count == 0:
            self.status_var.set("未找到相关股票，请检查代码或网络")
        else:
            self.status_var.set(f"搜索完成 | 共 {count} 条结果")

    def on_item_click(self, event):
        selected = self.tree.selection()
        if not selected: return
        if not hasattr(self, '_last_click') or (time.time() - self._last_click > 0.5):
            self._last_click = time.time()
        else:
            return
        item = self.tree.item(selected[0])
        code = item['values'][0]
        name = item['values'][1]
        win = tk.Toplevel(self.root)
        win.title(f"{name} ({code}) K线图")
        win.geometry("400x300")
        tk.Label(win, text=f"正在加载 {name}...", font=("Arial", 12)).pack(pady=20)
        t = threading.Thread(target=self.draw_kline, args=(win, code, name), daemon=True)
        t.start()

    def draw_kline(self, win, code, name):
        if requests is None: return
        prefix = "sh" if code.startswith('6') else "sz"
        stock_code = f"{prefix}{code[2:]}"
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={stock_code},day,,,30,qfq"
        try:
            resp = requests.get(url, timeout=5)
            data_json = resp.json()
            stock_data = data_json.get('data', {}).get(stock_code, {})
            kline_data = stock_data.get('day') or stock_data.get('qfqday')
            if kline_data:
                processed_data = []
                for item in kline_data:
                    if len(item) >= 3:
                        processed_data.append({'close': item[2]})
                win.after(0, self.render_chart, win, processed_data, name)
        except Exception as e:
            print(f"K线接口错误: {e}")

    def render_chart(self, win, data, name):
        for widget in win.winfo_children(): widget.destroy()
        canvas = tk.Canvas(win, bg="white", width=380, height=250)
        canvas.pack()
        if not data:
            canvas.create_text(190, 125, text="无数据", fill="red")
            return
        closes = [float(item['close']) for item in data]
        if not closes: return
        min_p, max_p = min(closes), max(closes)
        range_p = max_p - min_p if max_p != min_p else 1
        points = []
        step = 380 / len(closes)
        for i, price in enumerate(closes):
            x = i * step
            y = 250 - ((price - min_p) / range_p) * 210 - 20
            points.extend([x, y])
        canvas.create_line(points, fill="blue", width=2)
        tk.Label(win, text=f"{name} 近 30 日走势", font=("Arial", 12)).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()