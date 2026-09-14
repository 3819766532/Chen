# ============================================================
# 免责声明：本代码仅供学习交流使用，请勿用于非法用途。
# 使用本代码所产生的一切后果由使用者自行承担，
# 作者不承担任何法律责任。
# ============================================================

import pickle
import hashlib
import struct
import time
import sys
import os
import random
from functools import lru_cache

try:
    import zstandard as zstd
except ImportError:
    zstd = None

if os.name == 'nt':
    import msvcrt
else:
    import termios
    import tty
    import select


# ---------- 渲染工具 ----------
_char = "▄"
pixel_cache_size = 8192
frame_cache_size = 2048


def myprint(text: str):
    sys.stdout.write(text)
    sys.stdout.flush()


@lru_cache(maxsize=pixel_cache_size)
def transform(ur: int, ug: int, ub: int,
              lr: int, lg: int, lb: int,
              char: str = _char) -> str:
    return "\033[38;2;{0};{1};{2};48;2;{3};{4};{5}m{6}".format(
        lr, lg, lb, ur, ug, ub, char
    )


@lru_cache(maxsize=frame_cache_size)
def parse(lst: tuple, char: str = _char) -> str:
    code = ''
    for row in lst:
        for pixel in row:
            code += transform(*pixel, char)
        code += "\033[0m\n"
    return code.removesuffix("\n")


# ---------- 游戏常量 ----------
BG = (80, 80, 80)  # 深灰色背景

COLORS = {
    'I': (0, 200, 240),
    'O': (240, 200, 0),
    'T': (170, 0, 220),
    'S': (0, 220, 0),
    'Z': (220, 0, 0),
    'J': (0, 0, 220),
    'L': (240, 140, 0),
}

SHAPES = {
    'I': [
        ((0, 1), (1, 1), (2, 1), (3, 1)),
        ((2, 0), (2, 1), (2, 2), (2, 3)),
        ((0, 2), (1, 2), (2, 2), (3, 2)),
        ((1, 0), (1, 1), (1, 2), (1, 3)),
    ],
    'O': [
        ((0, 0), (1, 0), (0, 1), (1, 1)),
        ((0, 0), (1, 0), (0, 1), (1, 1)),
        ((0, 0), (1, 0), (0, 1), (1, 1)),
        ((0, 0), (1, 0), (0, 1), (1, 1)),
    ],
    'T': [
        ((1, 0), (0, 1), (1, 1), (2, 1)),
        ((1, 0), (1, 1), (2, 1), (1, 2)),
        ((0, 1), (1, 1), (2, 1), (1, 2)),
        ((1, 0), (0, 1), (1, 1), (1, 2)),
    ],
    'S': [
        ((1, 0), (2, 0), (0, 1), (1, 1)),
        ((1, 0), (1, 1), (2, 1), (2, 2)),
        ((1, 1), (2, 1), (0, 2), (1, 2)),
        ((0, 0), (0, 1), (1, 1), (1, 2)),
    ],
    'Z': [
        ((0, 0), (1, 0), (1, 1), (2, 1)),
        ((2, 0), (1, 1), (2, 1), (1, 2)),
        ((0, 1), (1, 1), (1, 2), (2, 2)),
        ((1, 0), (0, 1), (1, 1), (0, 2)),
    ],
    'J': [
        ((0, 0), (0, 1), (1, 1), (2, 1)),
        ((1, 0), (2, 0), (1, 1), (1, 2)),
        ((0, 1), (1, 1), (2, 1), (2, 2)),
        ((1, 0), (1, 1), (0, 2), (1, 2)),
    ],
    'L': [
        ((2, 0), (0, 1), (1, 1), (2, 1)),
        ((1, 0), (1, 1), (1, 2), (2, 2)),
        ((0, 1), (1, 1), (2, 1), (0, 2)),
        ((0, 0), (1, 0), (1, 1), (1, 2)),
    ],
}


class Piece:
    def __init__(self, shape_type, x=0, y=0, rotation=0):
        self.type = shape_type
        self.x = x
        self.y = y
        self.rot = rotation
        self.color = COLORS[shape_type]


def new_piece(board_w):
    piece = Piece(random.choice(list(SHAPES.keys())))
    piece.x = (board_w - 4) // 2
    return piece


def collides(board, piece, dx=0, dy=0, rot_offset=0):
    board_h = len(board)
    board_w = len(board[0])
    coords = SHAPES[piece.type][(piece.rot + rot_offset) % len(SHAPES[piece.type])]
    for ox, oy in coords:
        x = piece.x + ox + dx
        y = piece.y + oy + dy

        if x < 0 or x >= board_w or y >= board_h:
            return True

        if y >= 0 and board[y][x] is not None:
            return True

    return False


def try_move(board, piece, dx, dy):
    if collides(board, piece, dx, dy):
        return False
    piece.x += dx
    piece.y += dy
    return True


def try_rotate(board, piece, direction=1):
    if collides(board, piece, rot_offset=direction):
        for kick in (-1, 1, -2, 2):
            if not collides(board, piece, dx=kick, rot_offset=direction):
                piece.x += kick
                piece.rot = (piece.rot + direction) % len(SHAPES[piece.type])
                return True
        return False

    piece.rot = (piece.rot + direction) % len(SHAPES[piece.type])
    return True


def lock_piece(board, piece):
    board_h = len(board)
    board_w = len(board[0])
    for ox, oy in SHAPES[piece.type][piece.rot]:
        x = piece.x + ox
        y = piece.y + oy

        if y < 0:
            return False

        if 0 <= y < board_h and 0 <= x < board_w:
            board[y][x] = piece.color

    return True


def clear_lines(board):
    cleared = 0
    new_board = []

    for row in board:
        if all(cell is not None for cell in row):
            cleared += 1
        else:
            new_board.append(row)

    while len(new_board) < len(board):
        new_board.insert(0, [None] * len(board[0]))

    return new_board, cleared


def board_to_frame(board):
    board_h = len(board)
    board_w = len(board[0])
    term_h = board_h // 2
    rows = []
    
    if board_h % 2 != 0:
        for ty in range(term_h):
            row = []
            for x in range(board_w):
                top = board[ty * 2][x]
                bottom = board[ty * 2 + 1][x]

                ur, ug, ub = top if top is not None else BG
                lr, lg, lb = bottom if bottom is not None else BG

                row.append((ur, ug, ub, lr, lg, lb))
            rows.append(tuple(row))
        row = []
        for x in range(board_w):
            cell = board[board_h - 1][x]
            ur, ug, ub = BG
            lr, lg, lb = cell if cell is not None else BG
            row.append((ur, ug, ub, lr, lg, lb))
        rows.append(tuple(row))
    else:
        for ty in range(term_h):
            row = []
            for x in range(board_w):
                top = board[ty * 2][x]
                bottom = board[ty * 2 + 1][x]

                ur, ug, ub = top if top is not None else BG
                lr, lg, lb = bottom if bottom is not None else BG

                row.append((ur, ug, ub, lr, lg, lb))
            rows.append(tuple(row))
    
    return tuple(rows)


# ---------- 游戏中的实时按键捕获 ----------
if os.name == 'nt':
    def read_keys():
        """Windows 下游戏内实时读取按键"""
        keys = []
        while msvcrt.kbhit():
            ch = msvcrt.getwch()
            
            if ch in ('\x00', '\xe0'):
                ch2 = msvcrt.getwch()
                mapping = {
                    'H': 'up',
                    'P': 'down',
                    'K': 'left',
                    'M': 'right',
                }
                keys.append(mapping.get(ch2, ''))
            else:
                if ch.lower() == 'w':
                    keys.append('up')
                elif ch.lower() == 's':
                    keys.append('down')
                elif ch.lower() == 'a':
                    keys.append('left')
                elif ch.lower() == 'd':
                    keys.append('right')
                elif ch.lower() == 'q':
                    keys.append('quit')
                elif ch == ' ':
                    keys.append('space')
                elif ch.lower() == 'x':
                    keys.append('rotate')
                elif ch.lower() == 'p':
                    keys.append('pause')
                elif ch.lower() == 'r':
                    keys.append('restart')
                elif ch.lower() == 'm':
                    keys.append('menu')
        
        return keys
else:
    def read_keys():
        """Unix/Linux/macOS 下游戏内实时读取按键"""
        keys = []
        while select.select([sys.stdin], [], [], 0)[0]:
            ch = sys.stdin.read(1)

            if ch == '\x1b':
                if select.select([sys.stdin], [], [], 0.01)[0]:
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        if select.select([sys.stdin], [], [], 0.01)[0]:
                            ch3 = sys.stdin.read(1)
                            mapping = {'A': 'up', 'B': 'down',
                                       'C': 'right', 'D': 'left'}
                            keys.append(mapping.get(ch3, 'quit'))
                        else:
                            keys.append('quit')
                    else:
                        keys.append('quit')
                else:
                    keys.append('quit')
            else:
                if ch.lower() == 'w':
                    keys.append('up')
                elif ch.lower() == 's':
                    keys.append('down')
                elif ch.lower() == 'a':
                    keys.append('left')
                elif ch.lower() == 'd':
                    keys.append('right')
                elif ch.lower() == 'q':
                    keys.append('quit')
                elif ch == ' ':
                    keys.append('space')
                elif ch.lower() == 'x':
                    keys.append('rotate')
                elif ch.lower() == 'p':
                    keys.append('pause')
                elif ch.lower() == 'r':
                    keys.append('restart')
                elif ch.lower() == 'm':
                    keys.append('menu')

        return keys


# ---------- 终端模式切换 ----------
def enable_raw_mode():
    """进入游戏前的终端设置"""
    myprint('\033[?1049h\033[?25l')  # 备用屏幕 + 隐藏光标
    
    if os.name != 'nt':
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        return old_settings
    return None


def disable_raw_mode(old_settings=None):
    """退出游戏后恢复终端"""
    if old_settings is not None:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
    
    myprint('\033[?1049l\033[?25h')  # 恢复主屏幕 + 显示光标


def clear_screen():
    myprint('\033[2J\033[H')


# ---------- 菜单系统（使用 input，无边框） ----------
def show_menu():
    """显示主菜单，返回用户选择"""
    clear_screen()
    
    print("""
        俄罗斯方块 - 但是终端

    1. 开始新游戏
    2. 退出游戏
""")
    
    while True:
        choice = input("请选择 (1-2): ").strip()
        if choice == '1':
            return 'new_game'
        elif choice == '2':
            return 'quit'
        else:
            print("无效选择，请输入 1 或 2")


def show_size_input():
    """使用 input 让用户输入自定义棋盘大小"""
    clear_screen()
    
    print("""
        设置棋盘大小

    宽度范围: 5-30
    高度范围: 10-40

    (输入 q 返回主菜单)
""")
    
    # 输入宽度
    while True:
        w_input = input("请输入棋盘宽度 (5-30): ").strip()
        if w_input.lower() == 'q':
            return None
        if w_input.isdigit():
            w = int(w_input)
            if 5 <= w <= 30:
                break
            else:
                print("宽度必须在 5-30 之间")
        else:
            print("请输入有效数字")
    
    # 输入高度
    while True:
        h_input = input("请输入棋盘高度 (10-40): ").strip()
        if h_input.lower() == 'q':
            return None
        if h_input.isdigit():
            h = int(h_input)
            if 10 <= h <= 40:
                break
            else:
                print("高度必须在 10-40 之间")
        else:
            print("请输入有效数字")
    
    return (w, h)


def show_game_over(score, lines, board_w, board_h):
    """游戏结束画面，使用 input"""
    clear_screen()
    
    print(f"""
        游戏结束！

    得分: {score}
    消除行数: {lines}
    棋盘大小: {board_w}x{board_h}

    R. 再来一局
    M. 返回主菜单
    Q. 退出游戏
""")
    
    while True:
        choice = input("请选择 (R/M/Q): ").strip().lower()
        if choice == 'r':
            return 'restart'
        elif choice == 'm':
            return 'menu'
        elif choice == 'q':
            return 'quit'
        else:
            print("无效选择")


def show_pause():
    """暂停画面，使用 input"""
    clear_screen()
    
    print("""
        已暂停

    P. 继续游戏
    M. 返回主菜单
""")
    
    while True:
        choice = input("请选择 (P/M): ").strip().lower()
        if choice == 'p':
            return 'resume'
        elif choice == 'm':
            return 'menu'
        else:
            print("无效选择")


# ---------- 游戏主循环 ----------
def game_loop(board_w, board_h):
    """运行一局游戏，返回 'restart'、'menu' 或 'quit'"""
    board = [[None] * board_w for _ in range(board_h)]
    piece = new_piece(board_w)

    score = 0
    lines = 0
    fall_interval = 0.5
    last_drop = time.time()

    running = True
    game_over = False

    # 进入游戏模式
    old_settings = enable_raw_mode()
    clear_screen()

    try:
        while running:
            now = time.time()

            # 处理按键
            for key in read_keys():
                if key == 'quit':
                    return 'quit'
                elif key == 'pause':
                    # 退出原始模式，使用 input
                    disable_raw_mode(old_settings)
                    pause_result = show_pause()
                    if pause_result == 'menu':
                        return 'menu'
                    elif pause_result == 'resume':
                        old_settings = enable_raw_mode()
                        clear_screen()
                        last_drop = time.time()
                elif not game_over:
                    if key == 'left':
                        try_move(board, piece, -1, 0)
                    elif key == 'right':
                        try_move(board, piece, 1, 0)
                    elif key == 'down':
                        if not try_move(board, piece, 0, 1):
                            if not lock_piece(board, piece):
                                game_over = True
                            else:
                                board, cleared = clear_lines(board)
                                score += cleared * 100
                                lines += cleared
                                piece = new_piece(board_w)
                                if collides(board, piece):
                                    game_over = True
                        last_drop = now
                    elif key in ('up', 'rotate'):
                        try_rotate(board, piece, 1)
                    elif key == 'space':
                        while try_move(board, piece, 0, 1):
                            pass
                        if not lock_piece(board, piece):
                            game_over = True
                        else:
                            board, cleared = clear_lines(board)
                            score += cleared * 100
                            lines += cleared
                            piece = new_piece(board_w)
                            if collides(board, piece):
                                game_over = True
                        last_drop = now

            # 自动下落
            if not game_over and now - last_drop >= fall_interval:
                if not try_move(board, piece, 0, 1):
                    if not lock_piece(board, piece):
                        game_over = True
                    else:
                        board, cleared = clear_lines(board)
                        score += cleared * 100
                        lines += cleared
                        piece = new_piece(board_w)
                        if collides(board, piece):
                            game_over = True
                last_drop = now

            # 渲染
            if not game_over:
                display = [row[:] for row in board]
                for ox, oy in SHAPES[piece.type][piece.rot]:
                    x = piece.x + ox
                    y = piece.y + oy
                    if 0 <= y < board_h and 0 <= x < board_w:
                        display[y][x] = piece.color

                frame = board_to_frame(display)
                score_text = f'Score: {score:>6}  Lines: {lines:>3}  棋盘: {board_w}x{board_h}\n'
                myprint('\033[H' + score_text + parse(frame))

            if game_over:
                time.sleep(0.5)
                disable_raw_mode(old_settings)
                return show_game_over(score, lines, board_w, board_h)

            time.sleep(0.01)
    
    finally:
        # 确保终端恢复
        disable_raw_mode(old_settings)


def main():
    """主函数"""
    try:
        while True:
            # 显示主菜单
            action = show_menu()
            
            if action == 'quit':
                break
            elif action == 'new_game':
                # 获取棋盘大小
                size = show_size_input()
                if size is None:
                    continue  # 返回主菜单
                
                board_w, board_h = size
                
                # 开始游戏
                while True:
                    result = game_loop(board_w, board_h)
                    
                    if result == 'quit':
                        return
                    elif result == 'menu':
                        clear_screen()
                        break  # 返回主菜单
                    elif result == 'restart':
                        continue  # 再来一局
    
    except KeyboardInterrupt:
        pass
    finally:
        # 确保终端完全恢复
        myprint('\033[?1049l\033[?25h')
        clear_screen()


if __name__ == '__main__':
    main()