from socket import *
from threading import Thread
import threading
import sys
import time

lock = threading.Lock()
global clientAddress, clientsock

class UserManager :
    '''사용자 관리 및 게임 메세지 전송을 담당하는 클래스
        1) 게임 서버로 입장한 사용자의 등록
        2) 게임을 종료하는 사용자의 퇴장 관리
        3) 사용자가 입장하고 퇴장하는 관리
        4) 사용자가 입력한 메세지(주사위 수)를 게임 서버에 접속한 모두에게 전송

        __init__ : 기본 설정
        addUser : 사용자의 ID를 self.users에 추가
        removeUser : 플레이어가 퇴장했을 때 다루기.
        sendMessageToAll : 내가 갖고 있는 사용자들에게 모두 메시지 보내기.
        diceroll : 36칸에 도착한 사람 판별, 그게 아니면 모두에게 이동 결과 알림
        move : 주사위 값을 받아서 이동        '''

    def __init__(self):
        self.users = {} #사용자의 등록 정보를 담을 사전 {사용자 이름:(소켓, 주소),...}
        self.removed = [] #게임에서 나간 사용자의 이름을 담는다.
        self.userloc = {} #사용자의 위치 정보를 담을 사전 {사용자 이름: 위치정보,...}
        self.gamestart = False #게임의 시작 여부를 표현(4명이 모이면 게임 시작)
        self.turn = 0 #현재 주사위를 던지는 사람의 index

        self.order = []
        self.board = {'1':'0,0', '2':'2,1', '3' : '0,0', '4': '0,0', '5': '0,0', '6': '0,0',
                      '7': '0,0', '8':'1,2', '9':'0,0', '10':'0,0', '11':'0,0', '12':'0,0',
                      '13': '0,0', '14':'2,-2', '15':'0,0', '16':'0,0', '17':'0,0', '18':'0,0',
                      '19': '0,0', '20':'0,0', '21':'-1,-1', '22':'0,0', '23':'0,0', '24':'0,0',
                      '25': '0,0', '26':'0,0', '27':'0,0', '28':'0,1', '29':'0,0', '30':'0,0',
                      '31': '0,0', '32':'0,0', '33':'0,0', '34':'0,0', '35':'-1,-2', '36':'0,0'}
        self.boardloc = {'1':0, '2':7, '3' : 0, '4': 0, '5': 0, '6':0,
                      '7': 0, '8':11, '9':0, '10':0, '11':0, '12':0,
                      '13': 0, '14':-10, '15':0, '16':0, '17':0, '18':0,
                      '19': 0, '20':0, '21':-6, '22':0, '23':0, '24':0,
                      '25': 0, '26':0, '27':0, '28':5, '29':0, '30':0,
                      '31': 0, '32':0, '33':0, '34':0, '35':-11, '36':0,}

    def addUser(self, username, conn, addr): #사용자 ID를 self.users에 추가하는 함수
        if username in self.users:
            conn.send('이미 등록된 사용자입니다.\n'.encode('utf-8'))
            return None

        #새로운 사용자를 등록함
        lock.acquire() #스레드 동기화를 막기위한 락
        self.users[username] = (conn, addr)
        self.userloc[username] = 1
        self.order.append(username)
        if(len(self.users) == 4) :
            self.gamestart = True
            print("게임이 시작되었습니다.")
            usernames = '0'
            for user in self.order :
                usernames = usernames + ','+user
            print(usernames)
        lock.release() #업데이트 후 락 해제
        conn,addr = list(self.users.values())[0]
        self.sendMessageToAll('[%s]님이 입장했습니다.' %username)
        print('+++ 대화 참여자 수 [%d]' %len(self.users))
        if (self.gamestart) :
            self.sendMessageToAll('startgame')
            time.sleep(0.5)
            self.sendMessageToAll(usernames)

            time.sleep(2)
            self.sendMessageToAll('[%s]의 순서입니다.'%self.order[0])

        else :
            time.sleep(0.2)
            self.sendMessageToAll("waiting")
        return username

    def removeUser(self, username):
        if username not in self.users:
            return

        lock.acquire()
        self.removed.append(username)
        del self.users[username]
        del self.userloc[username]
        lock.release()

        self.sendMessageToAll('[%s]님이 퇴장했습니다.' %username)
        print('--- 게임 참여자 수 [%d]' %len(self.users))

        if(len(self.users)==0) :
            self.gamestart=False
            self.turn=0
            self.order = []
            self.movestart = 0

    def sendMessageToAll(self, msg):
        for conn, addr in list(self.users.values()):
            conn.sendall(msg.encode('utf-8'))


    def diceroll(self, username, msg):

        moveresult = self.move(username, msg)
        moveresultarr = moveresult.split(",")

        if(moveresultarr[1] == "36") :
            self.sendMessageToAll(str(self.turn + 1) + ',' + moveresult)
            time.sleep(2.3)
            self.sendMessageToAll("victory,"+self.order[self.turn])

        else :
            self.sendMessageToAll(str(self.turn+1)+','+moveresult)

            self.turn = (self.turn + 1) % 4
            #
            if self.order[self.turn] in self.removed :
                self.turn = (self.turn + 1) % 4

            self.sendMessageToAll('이제 %s의 순서입니다' % (self.order[self.turn]))

    def move(self, username, msg):
        dicenum = int(msg.decode('utf-8'))

        lock.acquire()
        moveloc = self.userloc[username] + dicenum
        if moveloc >= 36:
            origin = self.userloc[username]
            self.userloc[username] = 36
            return str(origin)+','+str(36)+',0,0'

        result = str(self.userloc[username]) + ',' + str(moveloc) + ',' + self.board[str(moveloc)]

        moveloc = moveloc + self.boardloc[str(moveloc)]
        self.userloc[username] = moveloc
        lock.release()

        return result



#main
#2번 실행
def runServer():
    print("+++ 뱀주사위 게임 서버를 시작합니다.")
    print("+++ 서버를 끝내려면 ctrl-c를 누르세요")

    # socket 생성
    host = ""
    port = 8080
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    print("socket created")

    # 소켓과 host, port를 바인드 한다.
    try :
        s.bind((host, port))
        print("socket binded to port", port)
    except :
        print("bind failed")
        sys.exit()

    while True:
        s.listen(1)
        ## socket한테서 정보를 받음
        clientsock, clientAddress = s.accept()
        newthread = ClientThread(clientAddress, clientsock)
        newthread.start()
    s.close()


# thread function
class ClientThread(threading.Thread) :
    userman = UserManager()

    def __init__(self, clientAddress, clientsock):
        threading.Thread.__init__(self)
        self.csocket = clientsock
        self.clientAddress = clientAddress
        print("새로운 사람이 들어옴 : ", clientAddress)

    def run(self):
        username = self.registerUsername()
        print("다음으로부터 온 연결 : ", self.clientAddress)

        try:
            if(username == None) : return None

            msg = self.csocket.recv(1024)
            while msg:
                if(self.userman.gamestart) :
                    if(self.userman.order[self.userman.turn] == username) :
                        if (int(msg.decode('utf-8')) >= 1 or int(msg.decode('utf-8')) <= 6):
                            self.userman.diceroll(username, msg)

                    else :
                        conn, addr = self.userman.users[username]
                        warning = "당신의 차례가 아닙니다!"
                        conn.sendall(warning.encode('utf-8'))


                else :
                    conn, addr = self.userman.users[username]
                    warning = "게임이 아직 시작되지 않았습니다"
                    conn.sendall(warning.encode('utf-8'))

                msg = self.csocket.recv(1024)




        except Exception as e:
            print(e)
            # 상대방의 통신이 불안정해서 접속 종료
            if(e==OSError) :
                print("OSError")
                self.userman.removeUser(username)
                self.userman.sendMessageToAll("connecterror,"+username)

            else :
                self.userman.removeUser(username)
                self.userman.sendMessageToAll("leave,"+username)

            if (self.userman.order[self.userman.turn] == username) :

                self.userman.turn = (self.userman.turn + 1) % 4
                if(self.userman.order[self.userman.turn]) in self.userman.removed:
                    self.userman.turn = (self.userman.turn+1)%4


                time.sleep(2)
                self.userman.sendMessageToAll('이제 %s의 순서입니다' % (self.userman.order[self.userman.turn]))
            if (len(self.userman.users) == 1):
                time.sleep(1)
                self.userman.sendMessageToAll("victory,"+self.userman.order[self.userman.turn])

        print('[%s] 접속종료' %username)
        self.userman.removeUser(username)



    def registerUsername(self):
        while True:
            self.csocket.sendall('로그인ID:'.encode('utf-8'))
            username = self.csocket.recv(1024)
            username = username.decode('utf-8').strip()

            if (len(self.userman.users) >= 4 ):
                msg = "alreadyst"
                self.csocket.sendall(msg.encode('utf-8'))
                self.csocket.close()
                return None

            if self.userman.addUser(username, self.csocket, self.clientAddress):
                return username




# 얘 제일 먼
if __name__ == '__main__':

    runServer()
