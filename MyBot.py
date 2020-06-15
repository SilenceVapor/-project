# xyf zwh
import RPi.GPIO as GPIO
import time


class MyBot(object):
    #operation macro
    STOP = 0
    FRONT = 1
    LEFT = 2
    RIGHT = 3
    BACK = 4

    def __init__(self, in1=22, in2=27, ena=18, in3=25, in4=24, enb=23):
        self.r = 2.2    # cm
        self.pi = 3.1415926

        self.IN1 = in1
        self.IN2 = in2
        self.IN3 = in3
        self.IN4 = in4
        self.ENA = ena  #左轮马达
        self.ENB = enb  #右轮马达
        self.PA = 70    #占空比
        self.PB = 60
        self.PA_turn = 60
        self.PB_turn = 45

        GPIO.setmode(GPIO.BCM)  #设置引脚编号方式为BCM
        GPIO.setwarnings(False) #禁用warning，引脚可能被多个脚本使用
        #设置输入输出通道
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.ENB, GPIO.OUT)
        self.L_Motor = GPIO.PWM(self.ENA, 500) #频率设置为500Hz
        self.R_Motor = GPIO.PWM(self.ENB, 500)
        self.L_Motor.start(self.PA)
        self.R_Motor.start(self.PB)
        self.stop()

    def forward(self, speed=None):
        if speed is None:
            self.L_Motor.ChangeDutyCycle(self.PA)
            self.R_Motor.ChangeDutyCycle(self.PB)
        else:
            self.L_Motor.ChangeDutyCycle(speed)
            self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, True)
        GPIO.output(self.IN2, False)
        GPIO.output(self.IN3, True)
        GPIO.output(self.IN4, False)

    def stop(self):
        self.L_Motor.ChangeDutyCycle(0)
        self.R_Motor.ChangeDutyCycle(0)
        GPIO.output(self.IN1, False)
        GPIO.output(self.IN2, False)
        GPIO.output(self.IN3, False)
        GPIO.output(self.IN4, False)

    def backward(self, speed=None):
        if speed is None:
            self.L_Motor.ChangeDutyCycle(self.PA)
            self.R_Motor.ChangeDutyCycle(self.PB)
        else:
            self.L_Motor.ChangeDutyCycle(speed)
            self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, False)
        GPIO.output(self.IN2, True)
        GPIO.output(self.IN3, False)
        GPIO.output(self.IN4, True)

    def left(self, speed):
        if speed is None:
            self.L_Motor.ChangeDutyCycle(self.PA_turn+20)
            self.R_Motor.ChangeDutyCycle(self.PB_turn+20)
        else:
            self.L_Motor.ChangeDutyCycle(speed)
            self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, False)
        GPIO.output(self.IN2, True) #左轮向后转
        GPIO.output(self.IN3, False)
        GPIO.output(self.IN4, True) #右轮向前转

    def right(self, speed=None):
        if speed is None:
            self.L_Motor.ChangeDutyCycle(self.PA_turn)
            self.R_Motor.ChangeDutyCycle(self.PB_turn)
        else:
            self.L_Motor.ChangeDutyCycle(speed)
            self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, True)
        GPIO.output(self.IN2, False)
        GPIO.output(self.IN3, False)
        GPIO.output(self.IN4, True)

    def forward_time(self, t=1, speed=None):
        self.forward(speed)
        time.sleep(t)
        self.stop()

    def backward_time(self, t=1, speed=None):
        self.backward(speed)
        time.sleep(t)
        self.stop()

    def left_time(self, t=1, speed=None):
        self.left(speed)
        time.sleep(t)
        self.stop()

    def right_time(self, t=1, speed=None):
        self.right(speed)
        time.sleep(t)
        self.stop()

    def move_time(self, cmd, t=1, speed=None):
        if cmd == MyBot.STOP:
            self.stop()
        elif cmd == MyBot.FRONT:
            self.forward_time(t, speed)
        elif cmd == MyBot.LEFT:
            self.left_time(t, speed)
        elif cmd == MyBot.RIGHT:
            self.right_time(t, speed)
        elif cmd == MyBot.BACK:
            self.backward_time(t, speed)
        else:
            print("Unknown cmd!")

    def setPWMA(self, value):
        self.PA = value
        self.L_Motor.ChangeDutyCycle(self.PA)

    def setPWMB(self, value):
        self.PB = value
        self.R_Motor.ChangeDutyCycle(self.PB)

    def setMotor(self, left, right):
        if (right >= 0) and (right <= 100):
            GPIO.output(self.IN1, GPIO.HIGH)
            GPIO.output(self.IN2, GPIO.LOW)
            self.L_Motor.ChangeDutyCycle(right)
        elif (right < 0) and (right >= -100):
            GPIO.output(self.IN1, GPIO.LOW)
            GPIO.output(self.IN2, GPIO.HIGH)
            self.R_Motor.ChangeDutyCycle(0 - right)
        if (left >= 0) and (left <= 100):
            GPIO.output(self.IN3, GPIO.HIGH)
            GPIO.output(self.IN4, GPIO.LOW)
            self.L_Motor.ChangeDutyCycle(left)
        elif (left < 0) and (left >= -100):
            GPIO.output(self.IN3, GPIO.LOW)
            GPIO.output(self.IN4, GPIO.HIGH)
            self.R_Motor.ChangeDutyCycle(0 - left)


if __name__ == '__main__':
    Bot = MyBot()
    Bot.forward_time(t=2)

