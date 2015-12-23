# -*- coding: utf-8 -*-
"""
Created on Sat Dec 05 22:40:50 2015

@author: admin
"""

import sys
import numpy as np
from PyQt4 import QtGui, QtCore, Qt
from PyQt4 import Qwt5 as Qwt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *
import matplotlib.pyplot as plt

class Window(QtGui.QMainWindow):
    
    def __init__(self):
        super(Window,self).__init__()
        self.setGeometry(50,50,800,600)
        self.setWindowTitle('Memory Data Analysis Tool')
        self.__initUI()
        self.__initMenu()
        self.__initZooming()
        self.__initPanning()
        
    def __initUI(self):
        self.btnSize = 100   
        self.txtSize = 20
        self.lftMargin = 10
        self.topMargin = 40
        self.btmMargin = 10
        
        exitBtn = QtGui.QPushButton('EXIT',self)
        exitBtn.clicked.connect(QtCore.QCoreApplication.instance().quit)
        exitBtn.resize(self.btnSize,self.btnSize/4)
        exitBtn.move(self.lftMargin,self.topMargin)
        
        loadDataBtn = QtGui.QPushButton('Load Data',self)
        loadDataBtn.clicked.connect(self.showDialog)
        loadDataBtn.resize(self.btnSize,self.btnSize/4)
        loadDataBtn.move(self.lftMargin,self.topMargin+self.btnSize/4)
        
        self.effResult = QtGui.QLineEdit(self)
        self.effResult.resize(self.btnSize,self.txtSize)
        self.effResult.move(self.lftMargin,self.topMargin+self.btnSize/4*2)
            
        self.numOfInputs = 6;
        self.intRangeTable = QtGui.QTableWidget(self)
        self.intRangeTable.setRowCount(self.numOfInputs)
        self.intRangeTable.setColumnCount(1)
        self.intRangeTable.resize(self.btnSize,205)
        self.intRangeTable.move(self.lftMargin,self.topMargin+self.btnSize/4*2+self.txtSize)
        self.intRangeTable.cellChanged.connect(self.setIntRange)
        self.intRangeArray = np.zeros(self.numOfInputs)
        
        self.dataPlot = Qwt.QwtPlot(self)
        grid = Qwt.QwtPlotGrid
        
        self.curve = Qwt.QwtPlotCurve('data plot')
        self.curve1 = Qwt.QwtPlotCurve('data plot')
        self.curve2 = Qwt.QwtPlotCurve('data plot')
        
        self.show()
    
    def __initZooming(self):
        self.zoomer = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                        Qwt.QwtPlot.yLeft,
                                        Qwt.QwtPicker.DragSelection,
                                        Qwt.QwtPicker.AlwaysOff,
                                        self.dataPlot.canvas())
        self.zoomer.setRubberBandPen(QPen(Qt.black))
        self.zoomer.setEnabled(False)
        
    def __initPanning(self):
        self.panner = Qwt.QwtPlotPanner(self.dataPlot.canvas())
        self.panner.setEnabled(False)
        
    def __initMenu(self):
        menu = QMenu("menu", self)
        
        self.mouseActGroup = QActionGroup(self, exclusive=True)
        menu.addAction(self.mouseActGroup.addAction(QAction('zoom', menu, checkable=True)))
        menu.addAction(self.mouseActGroup.addAction(QAction('pan', menu, checkable=True)))
        self.mouseActGroup.triggered.connect(self.onMouseActGroupTriggered)
        
        self.menuBar().addMenu(menu)
        
    def onMouseActGroupTriggered(self, action):        
        actionText = self.mouseActGroup.checkedAction().text()
        if actionText == 'zoom':
            self.zoomer.setEnabled(True)
            self.panner.setEnabled(False)
        elif actionText == 'pan':
            self.zoomer.setEnabled(False)
            self.panner.setEnabled(True)
        
    def resizeEvent(self, event):
        self.dataPlot.setGeometry(QtCore.QRect(self.btnSize*3/2, self.topMargin, self.width()-self.btnSize*3/2-self.lftMargin, self.height()-self.topMargin-self.btmMargin))
        
#    def mouseMoveEvent (self, event):
#        print event.pos()
    
    def showDialog(self):
        self.zoomer.zoom(0)
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open a first data file', '.', 'txt files (*.txt);;All Files (*.*)')
        f = open(fname, 'r')
        with f:
         self.data = np.genfromtxt(f, skip_header=10, skip_footer=1)
         self.tdata1 = self.data[:,1]
         self.cdata1 = self.data[:,0]  
         
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open a secnd data file', '.', 'txt files (*.txt);;All Files (*.*)')
        f = open(fname, 'r')
        with f:
         self.data = np.genfromtxt(f, skip_header=10, skip_footer=1)
         self.tdata = self.data[:,1]
         self.cdata = self.data[:,0]  
        
        self.plotData()
        self.zoomer.setZoomBase()
         
    def setIntRange(self):
         self.intRangeArray[self.intRangeTable.currentRow()] = self.intRangeTable.currentItem().text() 

         if np.count_nonzero(self.intRangeArray) == self.numOfInputs:
             np.sort(self.intRangeArray)
             self.intRangeArrayAll = np.zeros(2*int(self.intRangeArray[5])+2)
             
             peakWidth = self.intRangeArray[1] - self.intRangeArray[0]
             self.intRangeArrayAll[0:2] = [self.intRangeArray[0], self.intRangeArray[1]]
             inputPulse = np.sum(self.cdata1[self.intRangeArray[0]:self.intRangeArray[1]]) - np.sum(self.cdata1[self.intRangeArray[0]-peakWidth:self.intRangeArray[0]])
             outputPulse = 0;
             peakWidth = self.intRangeArray[3] - self.intRangeArray[2]
             nextPeakStarts = self.intRangeArray[4] - self.intRangeArray[2]
             for idx in range(int(self.intRangeArray[5])):
                 bkg = np.sum(self.cdata[self.intRangeArray[2]+idx*nextPeakStarts-peakWidth:self.intRangeArray[2]+idx*nextPeakStarts])
                 outputPulse = outputPulse + np.sum(self.cdata[self.intRangeArray[2]+idx*nextPeakStarts:self.intRangeArray[2]+idx*nextPeakStarts+peakWidth]) - bkg
                 self.intRangeArrayAll[2*idx+2:2*idx+4] = [self.intRangeArray[2]+idx*nextPeakStarts, self.intRangeArray[2]+idx*nextPeakStarts+peakWidth]
                 
             self.effResult.setText(str(outputPulse/inputPulse))
             self.plotData()
        
    def plotData(self):        
        self.curve.detach()
        self.curve.setData(range(len(self.tdata)), self.cdata)
        self.curve.setPen(QPen(Qt.blue,2))
        self.curve.attach(self.dataPlot)
        
        self.curve1.detach()
        self.curve1.setData(range(len(self.tdata1)), self.cdata1)
        self.curve1.setPen(QPen(Qt.red,2))
        self.curve1.attach(self.dataPlot)
        
        if np.count_nonzero(self.intRangeArray) == self.numOfInputs:      
            self.curve2.detach()
            self.curve2.setData(self.intRangeArrayAll,np.zeros(len(self.intRangeArrayAll)))
            self.curve2.setPen(QPen(Qt.blue,1,Qt.NoPen))
            self.curve2.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Rect,
                                                QBrush(),
                                            QPen(Qt.green),
                                            QSize(7, 7)))
            self.curve2.attach(self.dataPlot)
        
            self.dataPlot.replot()
    
def main(): 
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()