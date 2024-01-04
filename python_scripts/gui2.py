import qdarkstyle
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import numpy as np
import serial
from serial.tools import list_ports
import sys
import time
from numba import jit
import threading
import csv
import pandas as pd

matplotlib.use('Qt5Agg')

class ComboBox(QComboBox):
    popupAboutToBeShown = pyqtSignal()

    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(ComboBox, self).showPopup()

class Window(QMainWindow): 
 
    def __init__(self):

        super().__init__()
        self.setGeometry(100, 100, 1200, 800) 
        self.setWindowTitle("APP")
        self.setWindowIcon(QIcon('kahvelab.png'))
        self.tabWidget()
        self.Widgets()
        self.layouts()
        self.init_variables()
        self.show()

    def tabWidget(self):

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, "PULSE OXIMETER")
    
    def init_variables(self):

        self.counter = 0

    def Widgets(self):

        self.PlotFigureCanvas()
        self.rec_thread = threading.Thread(target=self.receive, args=(1,))

        self.baudrate_list_qlabel = QLabel("Baud Rate")
        self.baudrate_cb = QComboBox(self)
        self.baudrate_cb.addItems(["----------", "300", "600", "1200", "2400", 
                                   "4800", "9600", "14400", "19200", 
                                   "28800", "38400", "56000", "57600", 
                                   "115200", "128000", "256000"])
        self.baudrate_cb.currentTextChanged.connect(self.baudrate_clicked_func)

        self.com_qlabel = QLabel("Enter COM", self)
        self.com_cb = ComboBox(self)
        self.com_cb.addItem("----------")
        self.com_cb.popupAboutToBeShown.connect(self.update_coms_func)

        self.connect_button = QPushButton("Connect", self)
        self.connect_button.clicked.connect(self.connect_MCU)

        self.configure_button = QPushButton("START", self)
        self.configure_button.clicked.connect(self.start_func)

        self.serial_monitor_list =  QListWidget()
        self.serial_monitor_list.addItem("Welcome PULSE OXIMETER GUI!")  

        self.clear_serial_monitor = QPushButton("CLEAR", self)
        self.clear_serial_monitor.clicked.connect(self.clear_list)

    def PlotFigureCanvas(self):

        self.fig    = plt.figure(figsize=(10, 8))
        self.fig.patch.set_facecolor('lightcyan')
        self.figCanvas = FigureCanvas(self.fig)
        self.toolbar  = NavigationToolbar(self.figCanvas, self)
        plt.ion()
        self.axes = self.fig.add_subplot(111)
        self.axes.set_xlabel("Time(ms)")
        self.axes.set_ylabel("ADC DATA(V)")
        self.axes.set_title("RED and IR LED ADC DATA")
        self.axes.get_legend()
        self.axes.grid("on")
    
    def plott(self, x, y, color, variable_name):
        self.axes.plot(x, y, ".", color = color, label = variable_name)  
        self.figCanvas.draw()
        self.fig.canvas.flush_events()
        
    def serial_monitor(self, item):

        self.serial_monitor_list.addItem(item)

    def clear_list(self):

        self.serial_monitor_list.clear()

    def receive(self, working_time):

        TERMINATOR = '\n'.encode('UTF8')
        end_time = time.time() + working_time
        while time.time() < end_time:

            line = self.mcu.read_until(TERMINATOR)
            data = line.decode('UTF8').strip()
            dataint = int(data[1::])*3.3/4096
            if data[0] == '1':
                self.writer.writerow([dataint, 0])
                #self.plott(self.counter, dataint, color = "red", variable_name = "RED LED")
            elif data[0] == '0':   
                self.writer.writerow([dataint, 0])
                #self.plott(self.counter, dataint, color = "purple", variable_name = "IR LED")
            self.counter += 1

    def start_func(self):

        csvfile = open('output.csv', 'w')
        self.writer = csv.writer(csvfile, lineterminator='\n')
        self.writer.writerow(["red_data", "ir_data"])
        self.time_initial = time.perf_counter()
        self.send(1)
        self.rec_thread.start()
        try:
            self.rec_thread.join()
        except KeyboardInterrupt:
            print("Program interrupted by user.")
            self.rec_thread._stop()
        finally:
            self.rec_thread.join()
        self.send(0)
        
    def send(self, text: str):

        line = '%s\r\f' % text
        self.mcu.write(line.encode('utf-8'))

    def connect_MCU(self):

        self.com = self.com_cb.currentText()
        self.clear_list()

        if self.com != "" and self.baud_rate != 0:

            self.mcu = serial.Serial(self.com, self.baud_rate, timeout = 0.3)
            time.sleep(0.1)
            self.serial_monitor("Connected!")

    def baudrate_clicked_func(self):

        self.baud_rate = int(self.baudrate_cb.currentText())

    def update_coms_func(self):
        
        self.com_cb.clear()
        com_list = list_ports.comports()

        for port in com_list:

            port = str(port)
            port_name = port.split("-")
            self.com_cb.addItem(port_name[0])
        
    def layouts(self):

        self.main_layout  = QHBoxLayout()
        self.right_layout = QFormLayout()
        self.left_layout  = QFormLayout()
        self.plot_layout  = QVBoxLayout()
        self.left_Hbox1   = QHBoxLayout()
        self.left_Hbox2   = QHBoxLayout()
        self.right_Vbox   = QVBoxLayout()

        # Left layout
        self.left_layout_group_box = QGroupBox("")
        self.left_Hbox1.addWidget(self.baudrate_list_qlabel)
        self.left_Hbox1.addWidget(self.baudrate_cb)
        self.left_Hbox1.addStretch()
        self.left_Hbox1.addWidget(self.com_qlabel)
        self.left_Hbox1.addWidget(self.com_cb)
        self.left_Hbox1.addStretch()
        self.left_Hbox1.addWidget(self.connect_button)
        self.left_layout.addRow(self.left_Hbox1)

        self.plot_layout.addWidget(self.toolbar)
        self.plot_layout.addWidget(self.figCanvas)
        self.left_layout.addRow(self.plot_layout)

        self.left_Hbox2.addStretch()
        self.left_Hbox2.addWidget(self.configure_button)
        self.left_layout.addRow(self.left_Hbox2) 

        self.left_layout_group_box.setLayout(self.left_layout)

        # Right layout     
        self.right_layout_group_box = QGroupBox("Serial Monitor")

        self.right_Vbox.addWidget(self.serial_monitor_list) 
        self.right_Vbox.addWidget(self.clear_serial_monitor)   
        self.right_layout.addRow(self.right_Vbox)

        self.right_layout_group_box.setLayout(self.right_layout)

        self.main_layout.addWidget(self.left_layout_group_box, 60)
        self.main_layout.addWidget(self.right_layout_group_box, 40)
        self.tab1.setLayout(self.main_layout)  

def main():

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet()) 
    window = Window()
    sys.exit(app.exec_())

if __name__ == "__main__":

    main()