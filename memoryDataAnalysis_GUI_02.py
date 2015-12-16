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

class Window(QtGui.QMainWindow):
    
    def __init__(self):
        super(Window,self).__init__()
        self.setGeometry(50,50,800,600)
        self.setWindowTitle('Memory Data Analysis Tool')
        self.__initUI()
        self.__initZooming()
        
    def __initUI(self):
        exitBtn = QtGui.QPushButton('EXIT',self)
        exitBtn.clicked.connect(QtCore.QCoreApplication.instance().quit)
        exitBtn.resize(100,50)
        exitBtn.move(690,10)
        
        loadDataBtn = QtGui.QPushButton('Load Data',self)
        loadDataBtn.clicked.connect(self.showDialog)
        loadDataBtn.resize(100,50)
        loadDataBtn.move(690,60)
        
        self.effResult = QtGui.QLineEdit(self)
        self.effResult.resize(100,20)
        self.effResult.move(690,110)
            
        self.intRangeTable = QtGui.QTableWidget(self)
        self.intRangeTable.setRowCount(4)
        self.intRangeTable.setColumnCount(1)
        self.intRangeTable.resize(100,145)
        self.intRangeTable.move(690,150)
        self.intRangeTable.cellChanged.connect(self.setIntRange)
        self.intRangeArray = np.array([0, 0, 0, 0])
        
        self.dataPlot = Qwt.QwtPlot(self)
        self.dataPlot.setGeometry(QtCore.QRect(10, 10, 650, 580))
        self.dataPlot.setObjectName("dataPlot")
        self.dataPlot.setAxisTitle(Qwt.QwtPlot.xBottom, 'x -->')
        self.dataPlot.setAxisTitle(Qwt.QwtPlot.yLeft, 'y -->')
        grid = Qwt.QwtPlotGrid
        
        self.curve = Qwt.QwtPlotCurve('data plot')
        self.curve2 = Qwt.QwtPlotCurve('data plot')
        
        self.show()
    
    def __initZooming(self):
        self.zoomer = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                        Qwt.QwtPlot.yLeft,
                                        Qwt.QwtPicker.DragSelection,
                                        Qwt.QwtPicker.AlwaysOn,
                                        self.dataPlot.canvas())
        self.zoomer.setRubberBandPen(QPen(Qt.black))
        
    def showDialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open a data file', '.', 'txt files (*.txt);;All Files (*.*)')
        f = open(fname, 'r')
        with f:
         self.data = np.genfromtxt(f, skiprows=1)
         self.tdata = self.data[:,0]
         self.cdata = self.data[:,1]  
         self.plotData()
         self.zoomer.setZoomBase()
         
    def setIntRange(self):
         self.intRangeArray[self.intRangeTable.currentRow()] = self.intRangeTable.currentItem().text() 
         np.sort(self.intRangeArray)
         self.plotData()
         if np.count_nonzero(self.intRangeArray)==4:
             self.effResult.setText(str((np.sum(self.cdata[self.intRangeArray[2]:self.intRangeArray[3]])/np.sum(self.cdata[self.intRangeArray[0]:self.intRangeArray[1]]))))
        
    def plotData(self):
        self.zoomer.zoom(0)
        
        self.curve.detach()
        self.curve.setData(range(len(self.tdata)), self.cdata)
        self.curve.setPen(QPen(Qt.blue,2))
        self.curve.attach(self.dataPlot)
        
        self.curve2.detach()
        self.curve2.setData(self.intRangeArray,np.zeros(len(self.intRangeArray)))
        self.curve2.setPen(QPen(Qt.blue,1,Qt.NoPen))
        self.curve2.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Rect,
                                        QBrush(),
                                        QPen(Qt.red),
                                        QSize(7, 7)))
        self.curve2.attach(self.dataPlot)
        
        self.dataPlot.replot()
    
def main(): 
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()