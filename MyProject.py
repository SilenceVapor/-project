import MyBot
import time
import QRcode
import numpy as np

# direction MACRO
STOP = 0
FRONT = 1
LEFT = 2
RIGHT = 3
BACK = 4

# hyperparameters
excellentdistance = 20
MAX_TRY_TIME = 5

# robot&camera instance
Bot = MyBot.MyBot()
QRmodule = QRcode.QRmodule()

# map:
grid = [[0, 3], [1, 4], [2, 5]]
pointList = [[0, 0, 1], [1, 0, 1], [2, 0, 1], [0, 1, 1], [1, 1, 1], [2, 1, 1]]
route = [[-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1]]

routeFlag = 0
ub = 1
db = 0
lb = 0
rb = 2

# task:
START = 0
DESTINATION = 5


# xyf
def getNextDFS(pre, cur, dst):
    global pointList, route, routeFlag
    if cur == dst:
        return None, None, 1

    if routeFlag == 1:
        return route[cur][0], route[cur][1], 1

    cx = pointList[cur][0]
    cy = pointList[cur][1]

    pointList[cur][2] = 0
    if cx + 1 <= rb and pointList[grid[cx + 1][cy]][2] == 1:
        nn, ndc, routeFlag = getNextDFS(cur, grid[cx + 1][cy], dst)
        if routeFlag == 1:
            nxt = grid[cx + 1][cy]
            route[cur][0] = nxt
    if routeFlag != 1 and cy + 1 <= ub and pointList[grid[cx][cy + 1]][2] == 1:
        nn, ndc, routeFlag = getNextDFS(cur, grid[cx][cy + 1], dst)
        if routeFlag == 1:
            nxt = grid[cx][cy + 1]
            route[cur][0] = nxt
    if routeFlag != 1 and cx - 1 >= lb and pointList[grid[cx - 1][cy]][2] == 1:
        nn, ndc, routeFlag = getNextDFS(cur, grid[cx - 1][cy], dst)
        if routeFlag == 1:
            nxt = grid[cx - 1][cy]
            route[cur][0] = nxt
    if routeFlag != 1 and cy - 1 >= db and pointList[grid[cx][cy - 1]][2] == 1:
        nn, ndc, routeFlag = getNextDFS(cur, grid[cx][cy - 1], dst)
        if routeFlag == 1:
            nxt = grid[cx][cy - 1]
            route[cur][0] = nxt
    pointList[cur][2] = 1

    if routeFlag == 0:
        return None, None, 0

    if pre == -1:
        px = cx - 1
        py = cy
    else:
        px = pointList[pre][0]
        py = pointList[pre][1]

    nx = pointList[nxt][0]
    ny = pointList[nxt][1]

    directionChange = -1
    if px < cx and cy < ny:
        directionChange = LEFT
    elif px < cx and cy > ny:
        directionChange = RIGHT
    elif px > cx and cy < ny:
        directionChange = RIGHT
    elif px > cx and cy > ny:
        directionChange = LEFT
    elif py < cy and cx < nx:
        directionChange = RIGHT
    elif py < cy and cx > nx:
        directionChange = LEFT
    elif py > cy and cx < nx:
        directionChange = LEFT
    elif py > cy and cx > nx:
        directionChange = RIGHT
    elif px == nx and py == ny:
        directionChange = BACK
    else:
        directionChange = FRONT

    route[cur][1] = directionChange
    return nxt, directionChange, 1

# xyf
def getDistance(cur, nxt):
    return 1    # always 1 block

# zwh
# 启发式随机路标搜索
def ExceptionHandle(errorcode):
    QRydistance = -1
    Id = -1
    flag = False

    if errorcode == 0:
        print("Routing error! Abort!")
        exit()

    if errorcode == 1:
        print("Can't find QRCode! Try!")
        try_time = 0
        while try_time < MAX_TRY_TIME:
            try_time += 1
            cnt = 0
            while cnt < 5 and flag == False:
                if try_time%2 == 0:
                    Bot.left_time(t=0.05 * cnt + 0.3)
                else:
                    Bot.right_time(t=0.05 * cnt + 0.1)
                randtime = np.random.rand() * try_time * 0.1
                isforward = 1 if np.random.rand() > 0.5 else 0
                if isforward == 1:
                    Bot.forward_time(randtime)
                else:
                    Bot.backward_time(randtime)
                cnt += 1
                isfind, isrecognize, position, data = QRmodule.findQRCode()
                if isfind == 1:
                    QRxdistance = data[0][0]
                    QRydistance = data[0][1]
                    if position == RIGHT:
                        ChangeBotDirection(RIGHT)
                        Bot.forward_time(t=abs(QRxdistance) * 0.1)
                        time.sleep(1)
                        ChangeBotDirection(LEFT)
                    elif position == LEFT:
                        ChangeBotDirection(LEFT)
                        Bot.forward_time(t=abs(QRxdistance) * 0.1)
                        time.sleep(1)
                        ChangeBotDirection(RIGHT)
                    if isrecognize == 0:
                        if QRydistance > excellentdistance:
                            Bot.forward_time(t=(QRydistance - excellentdistance) * 0.1)
                        else:
                            Bot.backward_time(t=(excellentdistance - QRydistance) * 0.1)
                    else:
                        Id = data[1]
                        flag = True
            if flag == True:
                break
        if flag == False:
            print("Can't find QRCode again! Abort!")
            exit()
    return QRydistance, Id

# xyf
def ChangeBotDirection(direction):
    if direction == LEFT:
        Bot.move_time(cmd=LEFT, t=0.45)  # turn 90
    elif direction == RIGHT:
        Bot.move_time(cmd=RIGHT, t=0.66)  # turn 90
    elif direction == BACK:
        Bot.move_time(cmd=RIGHT, t=1.33)  # turn 180
    time.sleep(1)

# xyf zwh
def run():
    global Bot, START, DESTINATION, STOP, FRONT, LEFT, RIGHT, BACK
    # job (one jump):
    pre = -1
    cur = START
    QRxdistance = 0
    QRydistance = 0
    Id = -1

    while True:
        if cur == DESTINATION:
            break

        # get next point and how to turn
        nxt, directionChange, reachable = getNextDFS(pre, cur, DESTINATION)

        # no route
        if reachable != 1:
            ExceptionHandle(0)
            break

        # turn to the correct direction
        ChangeBotDirection(directionChange)

        # march 0.8 block
        distance = getDistance(cur, nxt)
        Bot.forward_time(t=distance * 0.8)
        time.sleep(1)

        tryTime = 0
        while tryTime < 3:
            tryTime = tryTime + 1
            # scan if there is a QR in camera or not
            isfind, isrecognize, position, data = QRmodule.findQRCode()

            # if none, take a small extra step and scan again
            if isfind == 0:
                Bot.forward_time(t=distance * 0.1)
                time.sleep(1)
            elif isrecognize == 0:
                QRxdistance = data[0][0]
                if position == RIGHT:
                    ChangeBotDirection(RIGHT)
                    Bot.forward_time(t=abs(QRxdistance)*0.1)
                    time.sleep(1)
                    ChangeBotDirection(LEFT)
                elif position == LEFT:
                    ChangeBotDirection(LEFT)
                    Bot.forward_time(t=abs(QRxdistance)*0.1)
                    time.sleep(1)
                    ChangeBotDirection(RIGHT)
                QRydistance = data[0][1]
                if QRydistance > excellentdistance:
                    Bot.forward_time(t=(QRydistance-excellentdistance) * 0.1)
                else:
                    Bot.backward_time(t=(excellentdistance-QRydistance) * 0.1)
            else:
                QRxdistance = data[0][0]
                if position == RIGHT:
                    ChangeBotDirection(RIGHT)
                    Bot.forward_time(t=abs(QRxdistance) * 0.1)
                    time.sleep(1)
                    ChangeBotDirection(LEFT)
                elif position == LEFT:
                    ChangeBotDirection(LEFT)
                    Bot.forward_time(t=abs(QRxdistance) * 0.1)
                    time.sleep(1)
                    ChangeBotDirection(RIGHT)
                QRydistance = data[0][1]
                Id = data[1]
                break

        if tryTime == 3:
            QRydistance,Id = ExceptionHandle(1)
        else:
            # get above the QR
            Bot.forward_time(t=QRydistance*0.1)
            time.sleep(1)
            pre = cur
            cur = Id

if __name__ == "__main__":
    run()


