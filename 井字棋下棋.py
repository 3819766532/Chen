# ============================================================
# 免责声明：本代码仅供学习交流使用，请勿用于非法用途。
# 使用本代码所产生的一切后果由使用者自行承担，
# 作者不承担任何法律责任。
# ============================================================

import os
import time

def clear():
    os.system('clear')

def show_board(board):
    clear()
    print(f"""
 {board[0]} | {board[1]} | {board[2]}
---+---+---
 {board[3]} | {board[4]} | {board[5]}
---+---+---
 {board[6]} | {board[7]} | {board[8]}
""")

def cheat_ai(board):
    for i in range(9):
        if board[i] == ' ':
            board[i] = 'O'
            if check_win(board, 'O'):
                return
            board[i] = ' '
    for i in range(9):
        if board[i] == ' ':
            board[i] = 'X'
            if check_win(board, 'X'):
                board[i] = 'O'
                return
            board[i] = ' '
    if board[4] == ' ':
        board[4] = 'O'
        return
    for i in range(9):
        if board[i] == ' ':
            board[i] = 'O'
            return

def check_win(board, p):
    win = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for a,b,c in win:
        if board[a]==board[b]==board[c]==p:
            return True
    return False

board = [' '] * 9
print("🔥 超级井字棋 🔥")
time.sleep(1)

while True:
    show_board(board)
    while True:
        try:
            pos = int(input("输入位置(1-9)：")) - 1
            if 0 <= pos <= 8 and board[pos] == ' ':
                break
            else:
                print("位置无效！")
        except:
            print("请输入数字！")
    board[pos] = 'X'
    if check_win(board, 'X'):
        show_board(board)
        print("你赢了？不可能！")
        break
    cheat_ai(board)
    if check_win(board, 'O'):
        show_board(board)
        print("💻 电脑赢了！")
        print("⇣⇣⇣")
        time.sleep(1)
        print("就这？还想赢？")
        time.sleep(1)
        print("建议回去练练再来吧！")
        break
