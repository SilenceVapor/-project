# zwh
import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar

RIGHT = 3
LEFT = 2
FRONT = 1

class QRmodule():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)

    #读取摄像头的一帧画面
    def getimage(self):
        ret,img = self.cap.read()
        if ret == True:
            return img
        else:
            print("error: can't get image!")

    def recognizeQR(self,img):
        #二值化
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cv2.imshow('binary',binary)
        #找出二维码轮廓
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #选出四边形轮廓
        polycontours = []
        for contour in contours:
            tmp = cv2.approxPolyDP(contour, 10, True)
            if len(tmp) == 4:
                polycontours.append(tmp)
        #选择四边形轮廓中面积最大的
        maxArea = 0
        maxContour = None
        for contour in polycontours:
            if (len(contour) != 4):
                continue
            if cv2.contourArea(contour) > maxArea:
                maxArea = cv2.contourArea(contour)
                maxContour = contour
        #放缩图片，得到旋转矩阵
        #cv2.drawContours(img,maxContour,-1,(0,255,0),5)
        Points = np.array(maxContour, dtype=np.float32).reshape(4, 2)
        dstPoints = np.array([[0, 200],
                              [200, 200],
                              [200, 0],
                              [0, 0]], dtype=np.float32)
        transMat = cv2.getPerspectiveTransform(Points, dstPoints)
        QRimg = cv2.warpPerspective(img, transMat, (200, 200))
        #cv2.imshow("QRimg",QRimg)
        #cv2.waitKey(0)

        QrValues = []
        QrValues += pyzbar.decode(QRimg)
        ret, QRimg = cv2.threshold(QRimg, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        QrValues += pyzbar.decode(QRimg)
        heart = np.mean(maxContour.reshape(4, 2), axis=0)
    
        if len(heart) == 0:
            return False, False, None, None
        position = None
        diff = heart - img.shape[1] / 2
        if diff > 100:
            position = RIGHT
        elif diff < -100:
            position = LEFT
        else:
            position = FRONT
        if len(QrValues) == 0:
            return True, False, position, [Points]
        else:
            return True, True, position, [Points,QrValues[0]]

    def getdistance(self,points):
        # 参考https://blog.csdn.net/mao_hui_fei/article/details/80822339
        h = 10 #摄像头高度
        Dmin = 25 #摄像头画面距摄像头最近距离
        Dmax = 100 #摄像头画面据摄像头最远距离
        D1 = 20
        beta = np.arctan(30/20) #水平视场角

        heart = np.mean(points,axis=0) #二维码中心像素点坐标
        x0 = heart[0]
        y0 = heart[1]
        width = 640
        height = 480

        alpha = np.arctan(Dmin / h) #俯仰角
        theta = np.arctan(Dmax / h) -alpha #垂直视场角

        d0 = (height-y0)*theta/height #步进小距离
        y1 = h*np.tan(alpha+d0) #二维码中心距摄像头的y方向距离

        b1 = (y1+D1)*np.tan(beta/2)
        x1 = 2*b1*(x0-width/2) /width #二维码中心距摄像头的x方向距离

        return x1,y1


    def findQRCode(self):
        img = self.getimage()
        isfind, isrecognize, position, rawdata = self.recognizeQR(img)
        data = []
        if isfind == 1:
            distance = self.getdistance(rawdata[0])
            data.append(distance)
            if isrecognize == 1:
                Id = int(rawdata[1].data.decode("utf-8").split(" ")[2])
                data.append(Id)
        return isfind, isrecognize, position, data


