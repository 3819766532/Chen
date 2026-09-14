# ============================================================
# 免责声明：本代码仅供学习交流使用，请勿用于非法用途。
# 使用本代码所产生的一切后果由使用者自行承担，
# 作者不承担任何法律责任。
# ============================================================

import random
r=random.randint
A=100
e=150
q1=0
def 死亡判定():
    global A,e
    if A<=0:
        print("你死了")
        return 2
    if e<=0:
        print("🎉🎉🎉你战胜了魔王，你取得了胜利🎉🎉🎉")
        return 1
def 敌方行动():
    global A,e
    if e-50>=A:
        y=r(20,60)
        A=A-y
        print(f"魔王对你造成了{y}点伤害，你的生命值剩余{A}")
    if e-50<A:
        y=r(40, 80)
        A=A-y
        print(f"魔王对你造成了{y}点伤害，你的生命值剩余{A}")

def 我方行动():
    global A,e,q1
    i=r(1,50)
    c=1
    q=2+q1
    while 1:
        y=0
        try:
            print(f"你的行动次数剩余{q}")
            y=int(input("你想做什么？1.输出伤害 2.回血 3.查看预期值 4.献祭 5.保存体力 6.结束回合"))
        except:
            print("请输入合法数字")   
        if y==1:
            if q>0:
                q-=1
                y=0
                try:
                    y=int(input("你想造成多少伤害？"))
                except:
                     print("请输入合法数字")   
                if y>i:
                    print("过度的贪婪需要付出代价")
                    A=A-10
                    print(f"你损失了10点生命值，你的生命值剩余{A}")
                if y<=i:
                    e=e-y
                    print(f"你对魔王造成了{y}点伤害，敌方生命值剩余{e}")
                    a=死亡判定()
                    if a==1:
                        break
            else:
                print("你的行动次数不够")
        elif y==2:
            if q>0:
                q-=1
                y=0
                try:
                    y=int(input("你想恢复多少生命值？"))
                except:
                    print("请输入合法数字")    
                if y>i:
                    print("过度的贪婪需要付出代价")
                    A=A-10
                    print(f"你损失了10点生命值，你的生命值剩余{A}")
                if y<=i:
                    A=A+y
                    print(f"你的生命值回复至{A}")
            else:
                print("你的行动次数不够")
        elif y==3:
            if q<=0:
                print("你的行动次数不够")
            if q>0:
                q-=1
                print(f"敌人心里预期值为{i}")
        elif y==4:
            if q>0:
                if c>0:
                    q-=1
                    c-=1
                    y=0
                    try:
                        y=int(input("你要献祭多少生命值？1.30,2.50,3.75"))
                    except:
                        print("请输入合法数字")
                    if y==1:
                        A-=30
                        q+=2
                        print(f"你的生命值剩余{A},行动次数恢复至{q}")
                    elif y==2:
                        A-=50
                        q+=3
                        print(f"你的生命值剩余{A},行动次数恢复至{q}")
                    elif y==3:
                        A-=75
                        q+=4
                        print(f"你的生命值剩余{A},行动次数恢复至{q}")
                    else:
                        print("请输入合法数字")    
                    死亡判定()
                    a=死亡判定()
                    if a==2:
                        exit()
                elif c<=0:
                    print("你的献祭次数不足，每回合最多献祭1次")
            elif q<=0:
                print("你的行动次数不够")
        elif y==5:
            if q<=0:
                print("你的行动次数不够")
            if q>0:
                q-=1
                q1+=1        
                print("你的行动次数上限增加了")    
        elif y==6:
            break
        else:
            print("请输入合法数字")
while 1:
    print("=====你的回合=====")
    我方行动()
    a=死亡判定()
    if a==1:
        break
    print("=====魔王回合=====")
    敌方行动()
    a=死亡判定()
    if a==2:
        break