# ============================================================
# 免责声明：本代码仅供学习交流使用，请勿用于非法用途。
# 使用本代码所产生的一切后果由使用者自行承担，
# 作者不承担任何法律责任。
# ============================================================

import tkinter as tk
import random
import math
import sys
LOVE_WORD_COUNT = 180
WINDOW_WIDTH = 170
WINDOW_HEIGHT = 48
LOVE_SCALE = 2.3
LOVE_DISPLAY_TIME = 500
NEW_POPUP_INTERVAL = 90
MAX_TOTAL_WINDOWS = 220
LOVE_CREATE_DELAY = 12
STACK_OFFSET = 2
WORDS = [
    "早点睡，别熬夜", "好好照顾自己", "别太累啦", "按时吃饭",
    "你超棒的", "要多笑笑", "累了就歇一会", "我一直都在",
    "别给自己太大压力", "记得多喝水", "万事慢慢来", "今天也要开心",
    "别胡思乱想", "有我陪着你", "照顾好自己", "你已经很努力了",
    "抱抱你", "你值得所有温柔", "不开心就和我说", "我爱你"
]
windows = []
root = tk.Tk()
root.withdraw()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = screen_width // 2
center_y = screen_height // 2
new_popup_running = False
def get_love_points(n, scale=LOVE_SCALE):
    raw_pts = []
    for i in range(n):
        t = math.pi * 2 * i / n
        x = 160 * math.sin(t) ** 3
        y = 130 * math.cos(t) - 50 * math.cos(2*t) - 20 * math.cos(3*t) - 10 * math.cos(4*t)
        y = -y
        raw_pts.append((x, y))
    scaled_pts = [(x * scale, y * scale) for x, y in raw_pts]
    xs = [p[0] for p in scaled_pts]
    ys = [p[1] for p in scaled_pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    love_center_x = (min_x + max_x) / 2
    love_center_y = (min_y + max_y) / 2
    offset_x = center_x - love_center_x
    offset_y = center_y - love_center_y
    final_pts = []
    for px, py in scaled_pts:
        win_x = int(offset_x + px - WINDOW_WIDTH // 2)
        win_y = int(offset_y + py - WINDOW_HEIGHT // 2)
        final_pts.append((win_x, win_y))
    return final_pts
def make_window(base_x, base_y, is_love_phase=False):
    x = base_x + random.randint(-STACK_OFFSET, STACK_OFFSET)
    y = base_y + random.randint(-STACK_OFFSET, STACK_OFFSET)
    win = tk.Toplevel(root)
    win.title("")
    win.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    win.protocol("WM_DELETE_WINDOW", close_all)
    if is_love_phase:
        bg_color = "#FFC8D8"
        text_color = "#A8071A"
        font_size = 8
    else:
        bg_color = f"#{random.randint(120,255):02x}{random.randint(120,255):02x}{random.randint(120,255):02x}"
        text_color = "#111111"
        font_size = 9
    win.config(bg=bg_color)
    text_content = random.choice(WORDS)
    label = tk.Label(
        win,
        text=text_content,
        bg=bg_color,
        fg=text_color,
        font=("微软雅黑", font_size, "bold"),
        wraplength=WINDOW_WIDTH - 15
    )
    label.pack(expand=True, fill=tk.BOTH, padx=4, pady=4)
    windows.append(win)
    return win
def close_all():
    for w in windows[:]:
        try:
            w.destroy()
        except:
            pass
    windows.clear()
    root.quit()
    sys.exit()
def clear_love_windows():
    for w in windows[:]:
        try:
            w.destroy()
        except:
            pass
    windows.clear()
def start_random_pop():
    global new_popup_running
    if new_popup_running:
        return
    new_popup_running = True
    def add_one():
        global new_popup_running
        if len(windows) >= MAX_TOTAL_WINDOWS:
            new_popup_running = False
            return
        rx = random.randint(30, screen_width - WINDOW_WIDTH - 30)
        ry = random.randint(30, screen_height - WINDOW_HEIGHT - 30)
        make_window(rx, ry, is_love_phase=False)
        root.after(NEW_POPUP_INTERVAL, add_one)
    add_one()
def draw_heart_step_by_step(points, index=0):
    if index >= len(points):
        root.after(LOVE_DISPLAY_TIME, lambda: (clear_love_windows(), start_random_pop()))
        return
    x, y = points[index]
    make_window(x, y, is_love_phase=True)
    root.after(LOVE_CREATE_DELAY, lambda: draw_heart_step_by_step(points, index + 1))
if __name__ == "__main__":
    heart_points = get_love_points(LOVE_WORD_COUNT)
    draw_heart_step_by_step(heart_points)
    root.mainloop()