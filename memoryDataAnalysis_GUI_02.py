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

def counter():
    counter.idx += 1
    return counter.idx
counter.idx = -1

class CommandAdd(QUndoCommand):
    def __init__(self,x,intRangeArray,intRangeArrayYValues,cdata1,cdata):
        super(CommandAdd, self).__init__()
        self.intRangeArray = intRangeArray
        self.intRangeArrayYValues = intRangeArrayYValues
        self.x = x
        self.cdata1 = cdata1
        self.cdata = cdata

    def redo(self):
        self.intRangeArray.append(self.x)
        if len (self.intRangeArray) < 3:
            self.intRangeArrayYValues.append(self.cdata1[self.intRangeArray[-1]])
        else:
            self.intRangeArrayYValues.append(self.cdata[self.intRangeArray[-1]])

    def undo(self):
        print self.intRangeArray
        self.intRangeArray.remove(self.intRangeArray[-1])
        self.intRangeArrayYValues.remove(self.intRangeArrayYValues[-1])
        print self.intRangeArray

class Window(QtGui.QMainWindow):
    
    def __init__(self):
        super(Window,self).__init__()
        self.setGeometry(50,50,1000,800)
        self.setWindowTitle('Memory Data Analysis Tool')
        self.__initUI()
        self.__initMenu()
        self.__initZooming()
        self.__initPanning()
        self.__initPicking()
        self.__initCounter()
        
    def __initUI(self):
        self.undoStack = QUndoStack(self)
        
        self.lftMargin = 10
        self.topMargin = 60
        self.btmMargin = 10
        
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
                                        Qwt.QwtPicker.AlwaysOn,
                                        self.dataPlot.canvas())
        self.zoomer.setRubberBandPen(QPen(Qt.black))
        self.zoomer.setEnabled(False)
        
    def __initPanning(self):
        self.panner = Qwt.QwtPlotPanner(self.dataPlot.canvas())
        self.panner.setEnabled(False)
        
    def __initPicking(self):
        self.picker = Qwt.QwtPlotPicker(Qwt.QwtPlot.xBottom,
                               Qwt.QwtPlot.yLeft,
                               Qwt.QwtPicker.PointSelection,
                               Qwt.QwtPlotPicker.RectRubberBand,
                               Qwt.QwtPicker.ActiveOnly,
                               self.dataPlot.canvas())
        self.picker.setEnabled(False)
                               
        self.picker.selected.connect(self.mousePressed)
        
    def __initMenu(self):
        menuFile = QMenu("File", self)
        menuEdit = QMenu("Edit", self)
        toolbar = QToolBar(self)
        
        loadDataAction =  QAction(QIcon('icons/open.ico'),'Load Data', menuFile)
        loadDataAction.setShortcut('Ctrl+O')
        loadDataAction.triggered.connect(self.showDialog)       
        menuFile.addAction(loadDataAction)  
        menuFile.addSeparator()  
        
        exitAction = QAction(QIcon('icons/exit.ico'),'Exit', menuFile)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(QtCore.QCoreApplication.instance().quit)
        menuFile.addAction(exitAction)
        
        self.undoAction = QAction(QIcon('icons/undo.ico'),'Undo', menuEdit)
        self.undoAction.setShortcut('Ctrl+Z')
        self.undoAction.setEnabled(False)
        self.undoAction.triggered.connect(self.undoStack.undo) 
        menuEdit.addAction(self.undoAction)
        
        self.redoAction = QAction(QIcon('icons/redo.ico'),'Redo', menuEdit)
        self.redoAction.setShortcut('Ctrl+Y')
        self.redoAction.setEnabled(False)
        self.redoAction.triggered.connect(self.undoStack.redo) 
        menuEdit.addAction(self.redoAction)
        menuEdit.addSeparator()
        
        self.mouseActGroup = QActionGroup(self, exclusive=True)
        zoomAction = QAction(QIcon('icons/search.ico'),'Zoom', menuEdit, checkable=True)       
        zoomAction.setShortcut('Z')
        menuEdit.addAction(self.mouseActGroup.addAction(zoomAction))
        panAction = QAction(QIcon('icons/hand.ico'),'Pan', menuEdit, checkable=True)
        panAction.setShortcut('P')
        menuEdit.addAction(self.mouseActGroup.addAction(panAction))
        pickAction = QAction(QIcon('icons/hand-touch.ico'),'Pick', menuEdit, checkable=True)
        pickAction.setShortcut('C')
        menuEdit.addAction(self.mouseActGroup.addAction(pickAction))
        self.mouseActGroup.triggered.connect(self.onMouseActGroupTriggered)
        menuEdit.addSeparator()
        
        resetCounterAction = QAction('Reset Ranges', menuEdit)
        resetCounterAction.triggered.connect(self.__initCounter)
        menuEdit.addAction(resetCounterAction)
        
        refreshIntAction = QAction('Refresh efficiency', menuEdit)
        refreshIntAction.triggered.connect(self.calcIntegral)
        menuEdit.addAction(refreshIntAction)
        
        self.effResult = QtGui.QLineEdit(self)
        self.effResult.setReadOnly(True)
        
        toolbar.addAction(loadDataAction)
        toolbar.addSeparator()
        toolbar.addAction(self.mouseActGroup.addAction(zoomAction))
        toolbar.addAction(self.mouseActGroup.addAction(panAction))
        toolbar.addAction(self.mouseActGroup.addAction(pickAction))
        toolbar.addSeparator()
        toolbar.addAction(self.undoAction)
        toolbar.addAction(self.redoAction)
        toolbar.addSeparator()
        toolbar.addAction(resetCounterAction)
        toolbar.addAction(refreshIntAction)
        toolbar.addWidget(self.effResult)
        toolbar.addSeparator()
        toolbar.addAction(exitAction)   
        
        self.menuBar().addMenu(menuFile)
        self.menuBar().addMenu(menuEdit)
        self.addToolBar(toolbar)
        
    def __initCounter(self):
        self.intRangeArray = []
        self.intRangeArrayYValues = []
        self.plotData()
        self.effResult.setText(str(0))      
        
    def onMouseActGroupTriggered(self, action):        
        actionText = self.mouseActGroup.checkedAction().text()
        if actionText == 'Zoom':
            self.zoomer.setEnabled(True)
            self.panner.setEnabled(False)
            self.picker.setEnabled(False)
        elif actionText == 'Pan':
            self.zoomer.setEnabled(False)
            self.panner.setEnabled(True)
            self.picker.setEnabled(False)
        elif actionText == 'Pick':
            self.zoomer.setEnabled(False)
            self.panner.setEnabled(False)
            self.picker.setEnabled(True)
            
    def mousePressed(self,pos): 
        command = CommandAdd(int(pos.x()),self.intRangeArray,self.intRangeArrayYValues,self.cdata1,self.cdata)
        self.undoStack.push(command)
        if self.undoStack.index() > 0:
            self.redoAction.setEnabled(True)
            self.undoAction.setEnabled(True)
        self.calcIntegral()
        self.plotData()

    def calcIntegral(self):
        if len(self.intRangeArray) > 3:    
            peakWidth = self.intRangeArray[1] - self.intRangeArray[0]
            inputPulse = np.sum(self.cdata1[self.intRangeArray[0]:self.intRangeArray[1]]) - np.sum(self.cdata1[self.intRangeArray[0]-peakWidth:self.intRangeArray[0]])
            outputPulse = 0;
            peakWidth = self.intRangeArray[3] - self.intRangeArray[2]
        
            for idx in range(int(len(self.intRangeArray)/2) - 1):
                bkg = np.sum(self.cdata[self.intRangeArray[2*idx+2]-peakWidth:self.intRangeArray[2*idx+2]])
                outputPulse = outputPulse + np.sum(self.cdata[self.intRangeArray[2*idx+2]:self.intRangeArray[2*idx+3]]) - bkg
        
            self.effResult.setText(str(outputPulse/inputPulse))
        
    def resizeEvent(self, event):
        self.dataPlot.setGeometry(QtCore.QRect(self.lftMargin, self.topMargin, self.width()-self.lftMargin, self.height()-self.topMargin-self.btmMargin))
    
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
        
    def plotData(self):   
        try:
            self.cdata
        except:
            pass
        else:
            self.curve.detach()
            self.curve.setData(range(len(self.tdata)), self.cdata)
            self.curve.setPen(QPen(Qt.blue,2))
            self.curve.attach(self.dataPlot)
            
            self.curve1.detach()
            self.curve1.setData(range(len(self.tdata1)), self.cdata1)
            self.curve1.setPen(QPen(Qt.red,2))
            self.curve1.attach(self.dataPlot)
            
            self.curve2.detach()
            self.curve2.setData(self.intRangeArray,self.intRangeArrayYValues)
            self.curve2.setPen(QPen(Qt.blue,1,Qt.NoPen))
            self.curve2.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Rect,
                                            QBrush(),
                                            QPen(Qt.green,3),
                                            QSize(7, 7)))
            self.curve2.attach(self.dataPlot)
        
        self.dataPlot.replot()

def main(): 
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()