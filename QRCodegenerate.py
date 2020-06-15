# zwh
import pyzbar.pyzbar as pyzbar
import qrcode
import cv2
import numpy as np

def generateQRCode(x,y,id,flag,filename):
    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.ERROR_CORRECT_H,
                       box_size=10, border=4)
    data = str(id) + ' '+ str(x) + ' '+ str(y)+ ' '+ str(flag)
    qr.add_data(data)
    qr.make()
    img = qr.make_image()
    img.save(filename)

def addblackbox(filename):
    img = cv2.imread(filename)
    img_add = cv2.copyMakeBorder(img, 25, 25, 25, 25, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    cv2.imwrite(filename,img_add)

def recognizeQRCode(img):
    cv2.imshow('1',img)
    cv2.waitKey(0)
    data = pyzbar.decode(img)
    print(data)
    print(data[0].data.decode('utf-8'))


generateQRCode(0,0,0,1,'0_1.png')
addblackbox('0_1.png')
generateQRCode(1,0,1,0,'1_0.png')
addblackbox('1_0.png')
generateQRCode(1,0,1,1,'1_1.png')
addblackbox('1_1.png')
generateQRCode(2,0,2,1,'2_1.png')
addblackbox('2_1.png')
generateQRCode(0,1,3,1,'3_1.png')
addblackbox('3_1.png')
generateQRCode(1,1,4,0,'4_0.png')
addblackbox('4_0.png')
generateQRCode(1,1,4,1,'4_1.png')
addblackbox('4_1.png')
generateQRCode(2,1,5,1,'5_1.png')
addblackbox('5_1.png')
