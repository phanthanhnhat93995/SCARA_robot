from tkinter import *
import serial  # import the serial library
import serial.tools.list_ports
import time
import math

L2 = 135.0
L3 = 135.0
d4 = 63.0
Bu = 50.0 # GỐC BÙ
Htt = 20 # CHIỀU CAO THỰC TẾ TỪ NAM CHÂM
# Horizontal distance from Joint3 to the center of the tool mounted on the end effector.
H_distanceTool = 50.9
# Vertical distance from Joint3 to the bottom of the tool mounted on the end effector.
V_distanceTool = -23.0
# Joint1 height.
heightFromGround = 132.0

L2Square = pow(L2, 2)
L3Square = pow(L3, 2)

RAD2DEG = 180.0 / math.pi
DEG2RAD = math.pi / 180.0


class RobotControl(Frame):

    def __init__(self, parent=None, **options):
        '''Giao dien chuong trinh duoc lap trinh o day'''
        Frame.__init__(self, parent, **options)

        self.arduino = None

        # List all COM Port available
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'COM' in p.description or 'Arduino' in p.description
        ]
        if not arduino_ports:
            arduino_ports = ['UNKNOWN']
        print(arduino_ports)

        # GUI VÙNG KẾT NỐI *********************************************************************************************
        f0 = LabelFrame(self, bg='#00FFFF', text='VÙNG KẾT NỐI',
                        font='Times 20 bold', labelanchor=N, relief="groove", borderwidth=8)
        K_KETNOI = LabelFrame(f0, bg='#E7FDF0', bd=0)
        K_KETNOI.place(x=37, y=10, width=340, height=225)
        Label(K_KETNOI, text='Port:', bg='#E7FDF0', font='Times 16 bold',
              relief="groove", borderwidth=5).grid(row=0, column=1, sticky=W)
        self.COM = StringVar()
        self.COM.set(arduino_ports[0])  # default value
        OptionMenu(K_KETNOI, self.COM, *arduino_ports).grid(row=0, column=2)
        # Display availabe BaudRate Port -------------------------------------------------------------------------------
        Label(K_KETNOI, text='Baud Rate:', bg='#E7FDF0', font='Times 16 bold',
              relief="groove", borderwidth=5).grid(row=1, column=1, sticky=W)
        self.Baudrate = StringVar()
        self.Baudrate.set('115200')  # default value
        OptionMenu(K_KETNOI, self.Baudrate, '115200', '250000', '9600').grid(row=1, column=2)
        # Send Gcode ---------------------------------------------------------------------------------------------------
        self.btnSend = Button(K_KETNOI, text='Send:', command=self.onSend, borderwidth=5,
                              font='Times 15 bold', bg='red', fg='white').grid(row=2, column=1, sticky=W)
        # Bước 1 -------------------------------------------------------------------------------------------------------
        self.var = StringVar()
        self.ent = Entry(K_KETNOI, width=20, textvariable=self.var, font='Times 13', borderwidth=5)
        self.ent.insert(0, '')  # set text
        self.ent.grid(row=2, column=2, sticky=W)
        K_CONNECT = LabelFrame(K_KETNOI, bg='#E7FDF0', bd=0)
        K_CONNECT.place(x=110, y=120, width=200, height=110)
        self.btnCONNECT = Button(K_CONNECT, bd=1,text='Kết nối', borderwidth=5, command=self.onConnect)
        self.btnCONNECT.place(x=65,y=0,width=70,height=70)
        self.btnCONNECT = Button(K_CONNECT, bd=1,text='Kết nối', borderwidth=5,  command=self.onConnect)
        self.btnCONNECT.place(x=65, y=0, width=70, height=70)

        self.txtConnect = Label(K_CONNECT, fg="#000000", bg='#E7FDF0', text='Connect to Robot',
                        font='Times 15 bold')
        self.txtConnect.place(x=0, y=70, width=200, height=30)

        f0.place(x=400, y=0,width=400,height=280)

        # GUI VÙNG THÔNG TIN *******************************************************************************************
        f1 = LabelFrame(self, bg='#CC99CC', text='VÙNG THÔNG TIN',
                        font='Times 20 bold', labelanchor=N, relief="ridge", borderwidth=8)
        K_THONGTIN=LabelFrame(f1,bg='#FCFCFC',bd=0)
        K_THONGTIN.place(x=35,y=30,width=340,height=150)


        self.ROBO=Label(f1,relief="flat",borderwidth=10, bg="#FCFCFC")
        self.ROBO.place(x=70,y=175, width=250, height=250)
        # X ------------------------------------------------------------------------------------------------------------
        Label(K_THONGTIN, text='X:', bg='#FCFCFC', anchor=N, width=4, justify=LEFT, relief="groove", borderwidth=5,
              font=("Times", 20, 'bold')).grid(row=0, column=0)
        self.v11 = StringVar()
        self.v11.set('0.0')
        Label(K_THONGTIN, textvariable=self.v11, bg='#FCFCFC', fg='red', anchor=N, width=6,
              justify=LEFT, font=("Times", 20, 'bold')).grid(row=0, column=1)
        # Y ------------------------------------------------------------------------------------------------------------
        Label(K_THONGTIN, text='Y:', bg='#FCFCFC', anchor=N, width=4, justify=LEFT, relief="groove", borderwidth=5,
              font=("Times", 20, 'bold')).grid(row=1, column=0)
        self.v12 = StringVar()
        self.v12.set('0.0')
        Label(K_THONGTIN, textvariable=self.v12, bg='#FCFCFC', fg='red', anchor=N, width=6,
              justify=LEFT, font=("Times", 20, 'bold')).grid(row=1, column=1)
        # Z ------------------------------------------------------------------------------------------------------------
        Label(K_THONGTIN, text='Z:', bg='#FCFCFC', anchor=N, width=4, justify=LEFT, relief="groove", borderwidth=5,
              font=("Times", 20, 'bold')).grid(row=2, column=0)
        self.v13 = StringVar()
        self.v13.set('0.0')
        Label(K_THONGTIN, textvariable=self.v13, bg='#FCFCFC', fg='red', anchor=N, width=6,
              justify=LEFT, font=("Times", 20, 'bold')).grid(row=2, column=1)
        # R0 -----------------------------------------------------------------------------------------------------------
        Label(K_THONGTIN, text='R0:', bg='#FCFCFC', anchor=N, width=4, justify=LEFT, relief="groove", borderwidth=5,
              font=("Times", 20, 'bold')).grid(row=0, column=2)
        self.v14 = StringVar()
        self.v14.set('0.0')
        Label(K_THONGTIN, textvariable=self.v14, bg='#FCFCFC', fg='red', anchor=N, width=6,
              justify=LEFT, font=("Times", 20, 'bold')).grid(row=0, column=3)
        # R1 -----------------------------------------------------------------------------------------------------------
        Label(K_THONGTIN, text='R1:', bg='#FCFCFC', anchor=N, width=4, justify=LEFT, relief="groove", borderwidth=5,
              font=("Times", 20, 'bold')).grid(row=1, column=2)
        self.v15 = StringVar()
        self.v15.set('0.0')
        Label(K_THONGTIN, textvariable=self.v15, bg='#FCFCFC', fg='red', anchor=N, width=6,
              justify=LEFT, font=("Times", 20, 'bold')).grid(row=1, column=3)
        # R2 -----------------------------------------------------------------------------------------------------------
        Label(K_THONGTIN, text='R2:', bg='#FCFCFC', anchor=N, width=4, justify=LEFT, relief="groove", borderwidth=5,
              font=("Times", 20, 'bold')).grid(row=2, column=2)
        self.v16 = StringVar()
        self.v16.set('0.0')
        Label(K_THONGTIN, textvariable=self.v16, bg='#FCFCFC', fg='red', anchor=N, width=6,
              justify=LEFT, font=("Times", 20, 'bold')).grid(row=2, column=3)

        f1.place(x=0,y=0,width=400,height=250)

        # GUI VÙNG ĐỘNG HỌC THUẬN **************************************************************************************
        f2 = LabelFrame(self, bg='#FFFF99', text='VÙNG ĐỘNG HỌC THUẬN', font='Times 20 bold', labelanchor=N,
                        relief="sunken", borderwidth=8)
        K_DHT = LabelFrame(f2, bg='#E6E6FA', bd=0)
        K_DHT.place(x=60, y=13, width=300, height=175)
        # R0 -----------------------------------------------------------------------------------------------------------
        Label(K_DHT, text='R0:', bg='#E6E6FA', width=4, anchor=CENTER, relief="groove", borderwidth=5,
              font=("Times", 20, 'bold')).grid(row=0, column=1)
        self.v21 = StringVar()
        self.e21 = Entry(K_DHT, textvariable=self.v21, font='Times 13', borderwidth=5)
        self.e21.insert(0, '')  # set text
        self.e21.grid(row=0, column=2)
        # R1 -----------------------------------------------------------------------------------------------------------
        Label(K_DHT, text='R1:', bg='#E6E6FA', width=4, anchor=CENTER, relief="groove", borderwidth=5,
              font=("Times", 20, 'bold')).grid(row=1, column=1)
        self.v22 = StringVar()
        self.e22 = Entry(K_DHT, textvariable=self.v22, font='Times 13', borderwidth=5)
        self.e22.insert(0, '')  # set text
        self.e22.grid(row=1, column=2)
        # R2 -----------------------------------------------------------------------------------------------------------
        Label(K_DHT, text='R2:', bg='#E6E6FA', width=4, anchor=CENTER, relief="groove", borderwidth=5,
              font=("Times", 20, 'bold')).grid(row=2, column=1)
        self.v23 = StringVar()
        self.e23 = Entry(K_DHT, textvariable=self.v23, font='Times 13', borderwidth=5)
        self.e23.insert(0, '')  # set text
        self.e23.grid(row=2, column=2)
        # NÚT NHẤN MOVE ------------------------------------------------------------------------------------------------
        Button(K_DHT, bg='red', fg='white', text="Move", font='Times 13 bold', borderwidth=5,
               command=self.dht).grid(row=3, column=2, columnspan=2)

        f2.place(x=0,y=410,width=400,height=230)

        # GUI VÙNG ĐỘNG HỌC NGHỊCH *************************************************************************************
        f3 = LabelFrame(self, bg='#FFFF99', text='VÙNG ĐỘNG HỌC NGHỊCH',
                        font='Times 20 bold', labelanchor=N, relief="sunken", borderwidth=8)
        K_DHN = LabelFrame(f3, bg='#E6E6FA', bd=0)
        K_DHN.place(x=60, y=13, width=300, height=175)
        # X ------------------------------------------------------------------------------------------------------------
        Label(K_DHN, text='X: ', bg='#E6E6FA', width=4, anchor=CENTER, relief="groove", borderwidth=5,
              font=("Times", 20, 'bold')).grid(row=0, column=1)
        self.v31 = StringVar()
        self.e31 = Entry(K_DHN, textvariable=self.v31, font='Times 13', borderwidth=5)
        self.e31.insert(0, '')  # set text
        self.e31.grid(row=0, column=2)
        # Y ------------------------------------------------------------------------------------------------------------
        Label(K_DHN, text='Y: ', bg='#E6E6FA', width=4, anchor=CENTER, relief="groove", borderwidth=5,
              font=("Times", 20, 'bold')).grid(row=1, column=1)
        self.v32 = StringVar()
        self.e32 = Entry(K_DHN, textvariable=self.v32, font='Times 13', borderwidth=5)
        self.e32.insert(0, '')  # set text
        self.e32.grid(row=1, column=2)
        # Z ------------------------------------------------------------------------------------------------------------
        Label(K_DHN, text='Z: ', bg='#E6E6FA', width=4, anchor=CENTER, relief="groove", borderwidth=5,
              font=("Times", 20, 'bold')).grid(row=2, column=1)
        self.v33 = StringVar()
        self.e33 = Entry(K_DHN, textvariable=self.v33, font='Times 13', borderwidth=5)
        self.e33.insert(0, '')  # set text
        self.e33.grid(row=2, column=2)
        # NÚT NHẤN MOVE ------------------------------------------------------------------------------------------------
        Button(K_DHN, bg='red', fg='white', text="Move", font='Times 13 bold', borderwidth=5,
               command=self.dhn).grid(row=3, column=2, columnspan=2)

        f3.place(x=400,y=410,width=400,height=230)
        # GUI VÙNG SET HOME ********************************************************************************************
        f5 = LabelFrame(self, bg='#0099FF', text='VÙNG SET HOME',
                        font='Times 20 bold', labelanchor=N, relief="sunken", borderwidth=8)
        # NÚT NHẤN SET HOME --------------------------------------------------------------------------------------------
        self.btHOME = Button(f5, bd=0, command=self.sethome,text="HOME",compound=TOP,borderwidth=5,
                             font='Times 15 bold')
        self.btHOME.place(x=160,y=15,width=80,height=80)

        self.btnAuto = Button(f5, bd=0, command=self.onAuto,text="Auto",compound=TOP,borderwidth=5,
                             font='Times 15 bold')
        self.btnAuto.place(x=0,y=15,width=80,height=80)


        f5.place(x=0,y=260,width=400,height=150)
        # GUI VÙNG GẮP VẬT *********************************************************************************************
        f4 = LabelFrame(self, bg='#0099FF', text='VÙNG GẮP VẬT',
                        font='Times 20 bold', labelanchor=N, relief="sunken", borderwidth=8)
        # NÚT NHẤN MOVE ------------------------------------------------------------------------------------------------
        #**************************************************************************
        self.btngapnha = Button(f4, bd=0,borderwidth=5,text="GẮP", command=self.ongap)
        self.btngapnha.place(x=155,y=20,width=90,height=50)
        self.btngapnha = Button(f4, bd=0,borderwidth=5,text="GẮP", command=self.ongap)
        self.btngapnha.place(x=155,y=20,width=90,height=50)
        f4.place(x=400,y=260,width=400,height=150)
        K_INFOR = LabelFrame( bg='#E6E6FA', bd=0)
        K_INFOR.place(x=0, y=200, width=350, height=180)

        Label(K_INFOR, text='Position 1', fg='red').grid(column=0, row=0)
        Label(K_INFOR, text='X1:').grid(column=0, row=1)
        self.xV1 = StringVar()
        self.xV1.set('0.0')
        Label(K_INFOR, textvariable=self.xV1).grid(column=1, row=1)
        Label(K_INFOR, text='Y1:').grid(column=0, row=2)
        self.yV1 = StringVar()
        self.yV1.set('0.0')
        Label(K_INFOR, textvariable=self.yV1).grid(column=1, row=2)
        Label(K_INFOR, text='Z1:').grid(column=0, row=3)
        self.zV1 = StringVar()
        self.zV1.set('0.0')
        Label(K_INFOR, textvariable=self.zV1).grid(column=1, row=3)
        self.btnGet1 = Button(K_INFOR, text='Get Point 1', command=self.onGetpoint1, font=("Arial", 10, 'bold'))
        self.btnGet1.grid(row=4, column=0, sticky=E)
        Label(K_INFOR, text='Position 2', fg='red').grid(column=3, row=0)
        Label(K_INFOR, text='X2:').grid(column=3, row=1)
        self.xV2 = StringVar()
        self.xV2.set('0.0')
        Label(K_INFOR, textvariable=self.xV2).grid(column=4, row=1)
        Label(K_INFOR, text='Y2:').grid(column=3, row=2)
        self.yV2 = StringVar()
        self.yV2.set('0.0')
        Label(K_INFOR, textvariable=self.yV2).grid(column=4, row=2)
        Label(K_INFOR, text='Z2:').grid(column=3, row=3)
        self.zV2 = StringVar()
        self.zV2.set('0.0')
        Label(K_INFOR, textvariable=self.zV2).grid(column=4, row=3)
        self.btnGet2 = Button(K_INFOR, text='Get Point 2', command=self.onGetpoint2, font=("Arial", 10, 'bold'))
        self.btnGet2.grid(row=4, column=3, sticky=E)

        Label(K_INFOR, text='Point Z', fg='red').grid(column=0, row=5)
        Label(K_INFOR, text='Z3:').grid(column=0, row=6)
        self.zV3 = StringVar()
        self.zV3.set('0.0')
        Label(K_INFOR, textvariable=self.zV3).grid(column=1, row=6)
        self.btnGetz = Button(K_INFOR, text='Get Z', command=self.onGetz, font=("Arial", 10, 'bold'))
        self.btnGetz.grid(row=6, column=2, sticky=E)
        K_INFOR.place(x=900, y=100, width=250, height=200)


    # SET HOME ******************************************************************************************************
    def sethome(self):
        if self.arduino is not None and self.arduino.is_open:
            print('M2')
            self.arduino.write(bytes('M2\r', 'utf-8'))
            self.arduino.write(bytes('G2 X' + str(0) + ' Y' + str(0) + ' Z' + str(0) + '\r', 'utf-8'))

    # GẮP THẢ VẬT ******************************************************************************************************
    global is_ongap
    is_ongap = True
    def ongap(self):
        global is_ongap
        if self.arduino is not None and self.arduino.is_open:
            if is_ongap:
                if self.arduino is not None and self.arduino.is_open:
                    print('M3')
                    self.arduino.write(bytes('M3\r', 'utf-8'))
                is_ongap = False
            else:
                print('M5')
                if self.arduino is not None and self.arduino.isOpen():
                    self.arduino.write(bytes('M5\r', 'utf-8'))
                is_ongap = True

    # ĐỘNG HỌC THUẬN ***************************************************************************************************
    def dht(self):
        # get the actual angle of the arm joint
        d1 = float(self.v21.get())  #R0
        th2 = float(self.v22.get()) #R1
        th3 = float(self.v23.get()) #R2
        if th2 > 0 and th2 <= 90:
            #th2_b = round((th2 * 0) / 90)
            th2_b = - 4
        elif th2 > 90 and th2 <= 180:
            th2_b = - 4.5
            #th2_b = round((th2 * 0) / 90)
        elif th2 == 0:
            th2_b = - 5

        if self.arduino is not None and self.arduino.is_open:
            print('G2 X' + str(th2 + th2_b) + ' Y' + str(th3) + ' Z' + str(d1))
            self.arduino.write(bytes('G2 X' + str(th2 + th2_b) + ' Y' + str(th3) + ' Z' + str(d1) + '\r', 'utf-8'))
            self.v14.set(d1)  #R0
            self.v15.set(th2)  #R1
            self.v16.set(th3)  #R2

            Px, Py, Pz = self.coordinatesFromAngles(th2, th3, d1)
            self.v11.set("{0:.2f}".format(Px)) #X
            self.v12.set("{0:.2f}".format(Py)) #Y
            self.v13.set("{0:.2f}".format(Pz)) #Z

            self.v31.set("{0:.2f}".format(Px)) #X
            self.v32.set("{0:.2f}".format(Py)) #Y
            self.v33.set("{0:.2f}".format(Pz)) #Z

    def coordinatesFromAngles(self, th2_angle, th3_angle, d1):
        th2 = th2_angle * DEG2RAD
        th3 = th3_angle * DEG2RAD
        # calculate x, y from side view
        # Note: x is radius in top view and y is z height in top view
        Px = round(L3 * math.cos(th2 + th3) + L2 * math.cos(th2))
        Py = round(L3 * math.sin(th2 + th3) + L2 * math.sin(th2))
        Pz = d1 + Htt

        return Px, Py, Pz

    #ĐỘNG HỌC NGHỊCH **************************************************************************************************
    def dhn(self):
        Px = float(self.v31.get())
        Py = float(self.v32.get())
        Pz = float(self.v33.get())
        #if Px == 150 and Py >=150 and Py <= 190:
            #th2_b = -11.86
            #th2_c = 6.54

        # calculate angle of joints
        th2_N, th3_N, d1_N = self.anglesFromCoordinates(Px, Py, Pz)

        if Px == 270 and Py == 0:
            th2_b = -5
            th2_c = 0
        elif Px == 270 and Py == 270:
            th2_b = 0
            th2_c = 0
        elif Px >= 210 and Py >= 120:
            th2_b = -3.55
            th2_c = 1.47
        elif Px >= 150 and Px <= 200 and Py >= 120:
            th2_b = -6.0
            th2_c = 1.5
        elif Px >= 200 and Px <= 230 and Py <= 120:
            th2_b = 6.0
            th2_c = 1.5
        elif Px >= 110 and Px <= 150 and Py >= 120:
            th2_b = -7.8
            th2_c = 2.5
        elif Px >= 70 and Px <= 110 and Py >= 120 and Py <= 160 :
            th2_b = -7.5
            th2_c = 1.0
        elif Px >= 70 and Px <= 110 and Py >= 170  :
            th2_b = -5
            th2_c = 0
        elif Px >= 30 and Px <= 70 and Py >= 120 and Py <= 160 :
            th2_b = -7.5
            th2_c = 1.0
        elif Px >= 30 and Px <= 70 and Py >= 170  :
            th2_b = -5
            th2_c = 0
        elif Px <= -110 and Px >= -150 and Py >= 120:
            th2_b = -1.3
            th2_c = - 2
        elif Px >= -70 and Px >= -110 and Py >= 120:
            th2_b = -1.3
            th2_c = 0
        elif Px <= -150 and Px >= -190 and Py >= 120:
            th2_b = -1.3
            th2_c = - 2.5
        elif Px <= -190 and Px >= -230 and Py >= 120:
            th2_b = -1.3
            th2_c = - 2.5
        # compute actual angle sent to arduino

        if self.arduino is not None and self.arduino.is_open:
            print('G2 X' + str(th2_N + th2_b) + ' Y' + str(th3_N + th2_c) + ' Z' + str(d1_N))
            self.arduino.write(bytes('G2 X' + str(th2_N + th2_b) + ' Y' + str(th3_N + th2_c) + ' Z' + str(d1_N) + '\r', 'utf-8'))

            self.v11.set(Px) #X
            self.v12.set(Py) #Y
            self.v13.set(Pz) #Z

            self.v14.set("{0:.2f}".format(d1_N)) #R0
            self.v15.set("{0:.2f}".format(th2_N)) #R1
            self.v16.set("{0:.2f}".format(th3_N)) #R2

            self.v21.set("{0:.2f}".format(d1_N))
            self.v22.set("{0:.2f}".format(th2_N))
            self.v23.set("{0:.2f}".format(th3_N))
    def onGetpoint1(self):
        self.xV1.set(self.v11.get())
        self.yV1.set(self.v12.get())
        self.zV1.set(self.v13.get())

    def onGetpoint2(self):
        self.xV2.set(self.v11.get())
        self.yV2.set(self.v12.get())
        self.zV2.set(self.v13.get())

    def onGetz(self):
        self.zV3.set(self.v13.get())

    def onAuto(self):
        Px = float(self.xV1.get())
        Py = float(self.yV1.get())
        Pz = float(self.zV1.get())
        Px1 = float(self.xV2.get())
        Py1 = float(self.yV2.get())
        Pz1 = float(self.zV2.get())
        Pz2 = float(self.zV3.get())



        th2_N, th3_N, d1_N = self.anglesFromCoordinates(Px, Py, Pz)
        th2_N2, th3_N2, d1_N2 = self.anglesFromCoordinates(Px1, Py1, Pz1)

        if Px == 270 and Py == 0:
            th2_b = -5
            th2_c = 0
        elif Px == 270 and Py == 270:
            th2_b = 0
            th2_c = 0
        elif Px >= 210 and Py >= 120:
            th2_b = -3.55
            th2_c = 1.47
        elif Px >= 150 and Px <= 200 and Py >= 120:
            th2_b = -6.0
            th2_c = 1.5
        elif Px >= 200 and Px <= 230 and Py <= 120:
            th2_b = 6.0
            th2_c = 1.5
        elif Px >= 110 and Px <= 150 and Py >= 120:
            th2_b = -7.8
            th2_c = 2.5
        elif Px >= 70 and Px <= 110 and Py >= 120 and Py <= 160 :
            th2_b = -7.5
            th2_c = 1.0
        elif Px >= 70 and Px <= 110 and Py >= 170  :
            th2_b = -5
            th2_c = 0
        elif Px >= 30 and Px <= 70 and Py >= 120 and Py <= 160 :
            th2_b = -7.5
            th2_c = 1.0
        elif Px >= 30 and Px <= 70 and Py >= 170  :
            th2_b = -5
            th2_c = 0
        elif Px <= -110 and Px >= -150 and Py >= 120:
            th2_b = -1.3
            th2_c = - 2
        elif Px >= -70 and Px >= -110 and Py >= 120:
            th2_b = -1.3
            th2_c = 0
        elif Px <= -150 and Px >= -190 and Py >= 120:
            th2_b = -1.3
            th2_c = - 2.5
        elif Px <= -190 and Px >= -230 and Py >= 120:
            th2_b = -1.3
            th2_c = - 2.5
        if Px1 == 270 and Py1 == 0:
            th2_b1 = -5
            th2_c2 = 0
        elif Px1 == 270 and Py1 == 270:
            th2_b1 = 0
            th2_c2 = 0
        elif Px1 >= 210 and Py1 >= 120:
            th2_b1 = -3.55
            th2_c2 = 1.47
        elif Px1 >= 150 and Px1 <= 200 and Py1 >= 120:
            th2_b1 = -6.0
            th2_c2 = 1.5
        elif Px1 >= 200 and Px1 <= 230 and Py1 <= 120:
            th2_b1 = 6.0
            th2_c2 = 1.5
        elif Px1 >= 110 and Px1 <= 150 and Py1 >= 120:
            th2_b1 = -7.8
            th2_c2 = 2.5
        elif Px1 >= 70 and Px1 <= 110 and Py1 >= 120 and Py1 <= 160 :
            th2_b1 = -7.5
            th2_c2 = 1.0
        elif Px1 >= 70 and Px1 <= 110 and Py1 >= 170  :
            th2_b1 = -5
            th2_c2 = 0
        elif Px1 >= 30 and Px1 <= 70 and Py1 >= 120 and Py1 <= 160 :
            th2_b1 = -7.5
            th2_c2 = 1.0
        elif Px1 >= 30 and Px1 <= 70 and Py1 >= 170  :
            th2_b1 = -5
            th2_c2 = 0
        elif Px1 <= -110 and Px1 >= -150 and Py1 >= 120:
            th2_b1 = -1.3
            th2_c2 = - 2
        elif Px1 >= -70 and Px1 >= -110 and Py1 >= 120:
            th2_b1 = -1.3
            th2_c2 = 0
        elif Px1 <= -150 and Px1 >= -190 and Py1 >= 120:
            th2_b1 = -1.3
            th2_c2 = - 2.5
        elif Px1 <= -190 and Px1 >= -230 and Py1 >= 120:
            th2_b1 = -1.3
            th2_c2 = - 2.5

        key = 1
        for i in range(10):
            if key == 1:
                self.arduino.write(bytes('G2 X' + str(th2_N + th2_b) + ' Y' + str(th3_N + th2_c) + ' Z' + str(d1_N) + '\r','utf-8'))
                # Qua diem gap
                time.sleep(5)
                print('1')
                self.arduino.write(bytes('G2 X' + str(th2_N + th2_b) + ' Y' + str(th3_N + th2_c) + ' Z' + str(Pz2 + 20) + '\r', 'utf-8'))  # Ha xuong gap
                time.sleep(7)
                self.arduino.write(bytes('M3' '\r', 'utf-8'))
                time.sleep(5)
                print('pick')
                self.arduino.write(bytes('G2 X' + str(th2_N + th2_b) + ' Y' + str(th3_N + th2_c) + ' Z' + str(d1_N) + '\r', 'utf-8'))  # Di len
                time.sleep(5)
                print('2')
                self.arduino.write(bytes('G2 X' + str(th2_N2 + th2_b1) + ' Y' + str(th3_N2 + th2_c2) + ' Z' + str(d1_N2) + '\r', 'utf-8'))  # Qua diem tha
                time.sleep(5)
                print('3')
                self.arduino.write(bytes('G2 X' + str(th2_N2 + th2_b1) + ' Y' + str(th3_N2 + th2_c2) + ' Z' + str(Pz2 -40) + '\r', 'utf-8'))  # Xuong tha vat
                time.sleep(5)
                print('Drop')
                self.arduino.write(bytes('M5' '\r', 'utf-8'))
                time.sleep(5)
                self.arduino.write(bytes('G2 X' + str(th2_N2 + th2_b1) + ' Y' + str(th3_N2 + th2_c2) + ' Z' + str(d1_N2) + '\r','utf-8'))
                time.sleep(5)



    def anglesFromCoordinates(self, Px, Py, Pz):

        d1 = Pz - Htt

        th3 = math.acos((Px * Px + Py * Py - L2 * L2 - L3 * L3) / (2 * L2 * L3))

        th2 = math.atan2(Py, Px) - math.atan((L3 * math.sin(th3)) / (L2 + L3 * math.cos(th3)))

        th2 = th2 * 180.0 / math.pi
        th3 = th3 * 180.0 / math.pi
        return th2, th3, d1
    # def anglesFromCoordinates2(self, Px1, Py1, Pz1):
    #
    #     d1 = Pz1 - Htt
    #
    #     th3 = math.acos((Px1 * Px1 + Py1 * Py1 - L2 * L2 - L3 * L3) / (2 * L2 * L3))
    #
    #     th2 = math.atan2(Py1, Px1) - math.atan((L3 * math.sin(th3)) / (L2 + L3 * math.cos(th3)))
    #
    #     th2 = th2 * 180.0 / math.pi
    #     th3 = th3 * 180.0 / math.pi
    #     return th2, th3, d1

    def onSend(self):
        if self.arduino is not None and self.arduino.is_open:
            print(self.ent.get())
            self.arduino.write(bytes(self.ent.get() + '\r', 'utf-8'))

    global is_connect
    is_connect = True

    def onConnect(self):
        self.v11.set(270.00) #X
        self.v12.set(0.0) #Y
        self.v13.set(20.00) #Z
        self.v14.set(0.0) #R0
        self.v15.set(0.0) #R1
        self.v16.set(0.0) #R2

        self.v21.set(0.0) #R0 NHẬP
        self.v22.set(0.0) #R1 NHẬP
        self.v23.set(0.0) #R2 NHẬP

        self.v31.set(270.00) #X NHẬP
        self.v32.set(0.00) #Y NHẬP
        self.v33.set(20.00) #Z NHẬP
        global is_connect
        if is_connect:

            self.txtConnect.config(text="Connecting...", fg="#FF0000")
            self.connect_arduino()
            self.txtConnect.config(text="Disconnect to Robot", fg="#00EE00")
            if self.arduino is not None and self.arduino.is_open:
                print('M17')
                self.arduino.write(bytes('M17\r', 'utf-8'))
            is_connect = False
        else:
            self.txtConnect.config(text="Connect to Robot", fg="#000000")
            if self.arduino is not None and self.arduino.isOpen():
                print('M18')
                self.arduino.write(bytes('M18\r', 'utf-8'))
            self.disconnect_arduino()
            is_connect = True


    def connect_arduino(self):
        print('Connecting...')
        self.arduino = serial.Serial(self.COM.get(), self.Baudrate.get())
        time.sleep(3)
        print('Connection established successfully')

    def disconnect_arduino(self):
        if self.arduino.isOpen():
            print('Disconnecting...')
            self.arduino.close()
            time.sleep(3)
            print('Disconnection established successfully')

window=None
def Exit_win():
    global window
    window.destroy()

if __name__ == '__main__':
    window = Tk()
    window.wm_title("ROBOT CONTROL", )
    window.geometry('1300x650+150+20')
    can = Canvas(window,height=800,width=800)
    Textwin1 = Label(window, relief="groove", borderwidth=10,
                     text='ROBOT SCARA CONTROL', bg='#FFFFFF', font="Times 25 bold")
    Textwin1.place(x=820, y=0, width=460, height=70)
    Textwin2 = Label(window,justify=LEFT, relief="groove", borderwidth=10, padx=10, pady=10,
                     text='SV: hien\nMSSV: xxx\nGVHD: Nguyễn Thiên Chương', bg='#FFFFFF',
                     font="Times 25 bold italic")
    Textwin2.place(x=815,y=480)
    RobotControl(window).place(x=0,y=0,width=800,height=750)
    Exit = Button(window, bd=1, borderwidth=5, bg="#3399FF", command=Exit_win, text="EXIT", compound='top',
                  font=("Times 15 bold"), fg="red")
    Exit.place(x=1000,y=350,width=70,height=95)
    can.pack()
    window.mainloop()
