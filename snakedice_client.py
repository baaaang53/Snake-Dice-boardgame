# Import socket module
import socket
from _thread import *
import threading
from threading import Thread
import tkinter
from tkinter import *
import random
import sys
import time


def movement(canvas, horse, prev, aft) :


    canvas.after(300,givetime(canvas, horse))

    for i in range(prev,aft):
        if ((i>=1 and i<=5) or (i>=13 and i<=17) or (i>=25 and i<=29)) :
            canvas.after(100, moveright(canvas,horse))
        elif (i==6 or i==12 or i==18 or i==24 or i==30):
            canvas.after(100, moveup(canvas, horse))
        else :
            canvas.after(100, moveleft(canvas, horse))

def gogogo(canvas, horse, prev, dx, dy) :


    canvas.after(300, givetime(canvas, horse))


    for i in range(10) :
        movehorizontal(canvas, horse, dx*93/10)
        movevertical(canvas, horse, -dy*92/10)
        canvas.after(100, givetime(canvas, horse))


def givetime(canvas, horse) :
    canvas.update()

def movehorizontal(canvas, horse, dx) :
    canvas.move(horse, dx, 0)
    canvas.update()

def movevertical(canvas, horse, dy) :
    canvas.move(horse, 0, dy)
    canvas.update()

def moveright(canvas, horse) :
    canvas.move(horse, 93, 0)
    canvas.update()

def moveleft(canvas, horse) :
    canvas.move(horse, -93, 0)
    canvas.update()

def moveup(canvas, horse) :
    canvas.move(horse, 0, -92)
    canvas.update()

def movedown(canvas, horse) :
    canvas.move(horse, 0, 92)
    canvas.update()

window = Tk()
window.geometry("800x600")
takenick = 'default'


# 여기는 server로부터 메시지 받은 걸 처리하는 곳.
def rcvMsg(sock) :
    while True:
        try:
            data = sock.recv(1024)
            dataarr = data.decode('utf-8').split(',')


            dicenum =""
            enable = True
            # 주사위 던지는 함수다
            def throwdice(*args) :
                global dicenum
                if(enable) :
                    dicenum =  str(random.randint(1, 6))
                    sock.send(dicenum.encode('utf-8'))
                else :
                    textmsg.configure(text="말이 이동중입니다. 잠시만 기다려주세요")
                    time.sleep(1.1)

            def theend() :
                sys.exit()

            if not data:
                break

            #정원이 초과되었을 때. server는 msg = alreadyst를 보낸다.
            elif (data.decode('utf-8') == "alreadyst") :
                # Toplevel(window)
                newin = tkinter.Toplevel(window)
                newin.geometry("400x300")
                newline = Label(newin, text="게임이 이미 시작되었습니다")
                newline.pack()
                okbutton = Button(newin, text="확인", command=theend)
                okbutton.pack()

            # 게임을 시작하라는 명령을 받았을 때. 새 창을 띄운다. - 게임
            elif (dataarr[0] == 'startgame'):
                gamechang = tkinter.Toplevel(window)
                gamechang.title("뱀 주사위 놀이 -" + takenick)
                gamechang.geometry("800x750")


                textmsg = Label(gamechang, text="게임을 시작합니다.")
                textmsg.pack()


                global canvas
                canvas = Canvas(gamechang, width=800, height=730, bg="#c3c3c3")
                canvas.pack()


                filename = "gameboard.png"

                board = PhotoImage(file=filename).subsample(2)
                redpuck = PhotoImage(file="red.png").subsample(15)
                bluepuck = PhotoImage(file="blue.png").subsample(15)
                greenpuck = PhotoImage(file="green.png").subsample(15)
                yellowpuck = PhotoImage(file="yellow.png").subsample(15)

                canvas.create_image(10,20,anchor = NW, image = board)
                canvas.create_image(640, 120, image = redpuck)#630, 130
                canvas.create_image(640, 160, image =bluepuck)# 630, 170,
                canvas.create_image(640, 200,  image =greenpuck)#630, 210,
                canvas.create_image(640, 240, image =yellowpuck)# 630, 250,

                global horse1, horse2, horse3, horse4
                horse1 = canvas.create_image(35, 665,  image = redpuck)#54, 678
                horse2 = canvas.create_image(35, 625,  image = bluepuck) #54, 638
                horse3 = canvas.create_image(75, 665,  image = greenpuck)#94,678
                horse4 = canvas.create_image(75, 625,  image = yellowpuck)#94.638

                global rollres
                global res_1, res_2, res_3, res_4, res_5, res_6
                res_1 = PhotoImage(file = "res_1.png").subsample(5)
                res_2 = PhotoImage(file = "res_2.png").subsample(5)
                res_3 = PhotoImage(file = "res_3.png").subsample(5)
                res_4 = PhotoImage(file = "res_4.png").subsample(5)
                res_5 = PhotoImage(file = "res_5.png").subsample(5)
                res_6 = PhotoImage(file = "res_6.png").subsample(5)
                rollinit = PhotoImage(file="result_init.png").subsample(5)
                rollres = canvas.create_image(670,400, image = rollinit)

                canvas.create_text(670,470, fill = "black", text = "주사위 결과")

                canvas.create_rectangle(630, 550, 700,620, fill="#225f7b", tags = "dice")
                canvas.create_text(665,585, fill = "white", text = "주사위 던지기", tags = "dice")
                canvas.tag_bind("dice", "<Button-1>", throwdice)

            elif (data.decode('utf-8') == "waiting") :
                newtext = Label(window, text = "상대방의 접속을 기다리는 중입니다.")
                newtext.pack()

            elif (dataarr[0] == "victory") :
                fin = tkinter.Toplevel(window)
                fin.title("게임종료")
                fin.geometry("400x300")
                newline = Label(fin, text="%s 이 승자입니다!"%dataarr[1])
                newline.pack()
                okbutton = Button(fin, text="확인", command=theend)
                okbutton.pack()


            elif (dataarr[0] == "connecterror") :
                textmsg.configure(text = "접속 상태 이상으로"+dataarr[1]+"님의 통신이 두절되었습니다.")

            elif (dataarr[0] == "leave") :
                textmsg.configure(text = dataarr[1] +"님이 나갔습니다.")

            elif(dataarr[0] =='0') :
                canvas.create_text(700, 115, anchor="center", text=dataarr[1])
                canvas.create_text(700, 155, anchor="center", text=dataarr[2])
                canvas.create_text(700, 195, anchor="center", text=dataarr[3])
                canvas.create_text(700, 235, anchor="center", text=dataarr[4])


            elif(dataarr[0] == '1') :

                enable = False
                dicenum = int(dataarr[2])-int(dataarr[1])
                diceimage = PhotoImage(file ="res_%s.png"%str(dicenum)).subsample(5)
                canvas.itemconfig(rollres, image = diceimage)

                movement(canvas, horse1, int(dataarr[1]), int(dataarr[2]))
                gogogo(canvas, horse1, int(dataarr[2]), int(dataarr[3]), int(dataarr[4]))
                enable = True


            elif(dataarr[0] =='2') :

                enable = False
                dicenum = int(dataarr[2]) - int(dataarr[1])
                diceimage = PhotoImage(file="res_%s.png" % str(dicenum)).subsample(5)
                canvas.itemconfig(rollres, image=diceimage)

                movement(canvas, horse2, int(dataarr[1]), int(dataarr[2]))
                gogogo(canvas, horse2, int(dataarr[2]), int(dataarr[3]), int(dataarr[4]))
                enable = True

            elif (dataarr[0] == '3'):

                enable = False
                dicenum = int(dataarr[2]) - int(dataarr[1])
                diceimage = PhotoImage(file="res_%s.png" % str(dicenum)).subsample(5)
                canvas.itemconfig(rollres, image=diceimage)

                movement(canvas, horse3, int(dataarr[1]), int(dataarr[2]))
                gogogo(canvas, horse3, int(dataarr[2]), int(dataarr[3]), int(dataarr[4]))
                enable = True


            elif (dataarr[0] == '4'):

                enable = False
                dicenum = int(dataarr[2]) - int(dataarr[1])
                diceimage = PhotoImage(file="res_%s.png" % str(dicenum)).subsample(5)
                canvas.itemconfig(rollres, image=diceimage)

                movement(canvas, horse4, int(dataarr[1]), int(dataarr[2]))
                gogogo(canvas, horse4, int(dataarr[2]), int(dataarr[3]), int(dataarr[4]))
                enable = True


            else :
                textmsg.configure(text=data.decode('utf-8'))
                print(data.decode('utf-8'))



        except Exception as e:

            pass


def runGame():

    # local host IP '127.0.0.1'
    HOST = '127.0.0.1'
    # Define the port on which you want to connect
    PORT = 8080


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 서버에 connect
    s.connect((HOST, PORT))
    t = Thread(target=rcvMsg, args = (s, ))
    t.daemon = True
    t.start()

    window.title("로그인")
    window.geometry("500x300")
    window.resizable(False, False)
    global takenick
    takenick = "default"

    # 함수들
    def onPressEnter(event):
        global takenick
        takenick = nickname.get()
        s.send(takenick.encode('utf-8'))

    # 상단 텍스트
    toplabel = Label(window, text="뱀 주사위 놀이")
    toplabel.pack()

    # 로그인 텍스트요
    loginlabel = Label(window, text="닉네임을 입력 후 엔터를 치세요")
    loginlabel.pack()

    # 닉네임 입력창
    nickname = tkinter.Entry(window)
    nickname.bind("<Return>", onPressEnter)  # 메시지 받아주기
    nickname.pack()






    window.mainloop()

    # message you send to server
    message = "hello"

    s.close()


if __name__ == '__main__':
    runGame()