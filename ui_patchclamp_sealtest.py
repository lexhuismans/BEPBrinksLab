# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 15:17:17 2019

@author: lhuismans

Part of this code was derived from:
    https://github.com/sidneycadot/pyqt-and-graphing/blob/master/PyQtGraphing.py
    
"""
from __future__ import division
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox

import pyqtgraph as pg

import sys
import numpy as np
import math
from scipy.optimize import curve_fit

from patchclamp import PatchclampSealTest
from constants import MeasurementConstants

#Setting graph settings
"""
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOption('useOpenGL', True)
pg.setConfigOption('leftButtonPan', False)
"""
pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'w')
pg.setConfigOption('useOpenGL', True)
pg.setConfigOption('leftButtonPan', False)

class SlidingWindow(pg.PlotWidget):
    """SlidingWindow gives access to the windowSize most recent values that were appended to it.
    Since the class inherits the pg.PlotWidget it can be added to the UI as a plot widget with a 
    sliding window. It is not yet verified that this will work. However it is worth a try ;)."""
    def __init__(self, windowSize, *args, **kwargs):
        super().__init__(*args, **kwargs) #Call the pg.PlotWidget so this class has the same behaviour as the PlotWidget object
        self.data = np.array([])
        self.n = 0
        self.windowSize = windowSize
        
        self.pen = QPen()
        self.pen.setColor(QColor(145,255,244))
        self.pen.setWidth(.7)
        self.pen.setStyle(Qt.DashLine)
        self.plotData = self.plot(pen=self.pen) #call plot, so it is not needed to calll this in the UI. However, you can still change the pen variables in the UI.
        
    def append_(self, values):
        """Append new values to the sliding window."""
        lenValues = len(values)
        if self.n+lenValues > self.windowSize:
            #Buffer is full so make room.
            copySize = self.windowSize-lenValues
            self.data = self.data[-copySize:]
            self.n = copySize
            
        self.data = np.append(self.data, values)
        
        self.n += lenValues
        
    def updateWindow(self):
        """Get a window of the most recent 'windowSize' samples (or less if not available)."""
        self.plotData.setData(self.data)
        
class PatchclampSealTestUI(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #------------------------Initiating patchclamp class-------------------
        self.sealTest = PatchclampSealTest()
        self.sealTest.measurementThread.measurement.connect(self.handleMeasurement) #Connecting to the measurement signal
        
        #----------------------------------------------------------------------
        #----------------------------------GUI---------------------------------
        #----------------------------------------------------------------------
        self.setMinimumSize(300,120)
        self.setWindowTitle("Patchclamp Seal Test")
        
        #------------------------------Gains-----------------------------------
        gainContainer = QGroupBox("Gains")
        gainLayout = QGridLayout()
        
        gainLayout.addWidget(QLabel("Input Voltage"), 0, 0)
        self.inVolGainList = QComboBox()
        self.inVolGainList.addItems(['1/10', '1', '1/50'])
        gainLayout.addWidget(self.inVolGainList, 1, 0)
        
        gainLayout.addWidget(QLabel("Output Voltage"), 0, 1)
        self.outVolGainList = QComboBox()
        self.outVolGainList.addItems(['10', '2', '5', '1', '20', '50', '100'])
        gainLayout.addWidget(self.outVolGainList, 1, 1)
        
        gainLayout.addWidget(QLabel("Output Current"), 0, 2)
        self.outCurGainList = QComboBox()
        self.outCurGainList.addItems(['1', '2', '5', '10', '20', '50', '100'])
        gainLayout.addWidget(self.outCurGainList, 1, 2)
        
        gainLayout.addWidget(QLabel("Probe"), 0, 3)
        self.probeGainList = QComboBox()
        self.probeGainList.addItems(['100M\u03A9','10G\u03A9'])
        gainLayout.addWidget(self.probeGainList, 1, 3)
        
        gainContainer.setLayout(gainLayout)
        
        #----------------------------Control-----------------------------------
        controlContainer = QGroupBox("Control")
        controlLayout = QHBoxLayout()
    
        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(lambda: self.measure())
        
        self.stopButton = QPushButton("Stop")
        self.stopButton.clicked.connect(lambda: self.stopMeasurement())
        
        controlLayout.addWidget(self.startButton)
        controlLayout.addWidget(self.stopButton)
        controlLayout.addWidget(gainContainer)
        
        controlContainer.setLayout(controlLayout)
        
        #-----------------------------Plots------------------------------------
        plotContainer = QGroupBox("Output")
        self.plotLayout = QVBoxLayout() #We set the plotLayout as an attribute of the object (i.e. self.plotLayout instead of plotLayout)
                                        #This is to prevent the garbage collector of the C++ wrapper from deleting the layout and thus triggering errors.
                                        #Derived from: https://stackoverflow.com/questions/17914960/pyqt-runtimeerror-wrapped-c-c-object-has-been-deleted
                                        # and http://enki-editor.org/2014/08/23/Pyqt_mem_mgmt.html
        
        self.outVolPlotWidget = SlidingWindow(2500) #Should be bigger than the readvalue
        self.outCurPlotWidget = SlidingWindow(2500) #Should be bigger than the readvalue
        
        self.plotLayout.addWidget(QLabel('Voltage (mV):'))
        self.plotLayout.addWidget(self.outVolPlotWidget)
        self.plotLayout.addWidget(QLabel('Current (pA):'))
        self.plotLayout.addWidget(self.outCurPlotWidget)
        
        valueContainer = QGroupBox("Resistance/Capacitance")
        self.valueLayout = QHBoxLayout()
        self.resistanceLabel = QLabel("Resistance: ")
        self.capacitanceLabel = QLabel("Capacitance: ")
        self.valueLayout.addWidget(self.resistanceLabel)
        self.valueLayout.addWidget(self.capacitanceLabel)
        valueContainer.setLayout(self.valueLayout)
        self.plotLayout.addWidget(valueContainer)
        
        plotContainer.setLayout(self.plotLayout)
        #---------------------------Adding to master---------------------------
        master = QVBoxLayout()
        master.addWidget(controlContainer)
        master.addWidget(plotContainer)
        
        self.setLayout(master)
        
        #--------------------------Setting variables---------------------------
        self.changeVolInGain(self.inVolGainList.currentText())
        self.changeVolOutGain(self.outVolGainList.currentText())   
        self.changeCurOutGain(self.outCurGainList.currentText())
        self.changeProbeGain(self.probeGainList.currentText())
        
        self.inVolGainList.currentIndexChanged.connect(lambda: self.changeVolInGain(self.inVolGainList.currentText()))
        self.outVolGainList.currentIndexChanged.connect(lambda: self.changeVolOutGain(self.outVolGainList.currentText()))
        self.outCurGainList.currentIndexChanged.connect(lambda: self.changeCurOutGain(self.outCurGainList.currentText()))
        self.probeGainList.currentIndexChanged.connect(lambda: self.changeProbeGain(self.probeGainList.currentText()))
        
    def measure(self):
        """Pop up window asking to check the gains.
        Returns 
        True if the measurement can be done
        and 
        False if not.
        """
        check = QMessageBox.question(self, 'GAINS!', "Are all the gains corresponding?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if check == QMessageBox.Yes:
            """Start the patchclamp measurement"""
            self.sealTest.setWave(self.inVolGain)
            self.sealTest.start()
        
    def handleMeasurement(self, voltOut, curOut):
        """Handle the measurement. Update the graph."""
        #Rescaling using gains
        voltOut = voltOut/self.outVolGain
        curOut = curOut/self.outCurGain/self.probeGain
        
        self.outVolPlotWidget.append_(voltOut*1000)
        self.outCurPlotWidget.append_(curOut*1*10**12)
        self.updateGraphs()
        
        self.updateLabels(curOut, voltOut)
        
    def updateGraphs(self):
        """Update graphs."""
        self.outCurPlotWidget.updateWindow()
        self.outVolPlotWidget.updateWindow()
    
    def updateLabels(self, curOut, voltOut):
        """Update the resistance and capacitance labels.
        http://scipy-lectures.org/intro/scipy/auto_examples/plot_curve_fit.html
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html"""
        constants = MeasurementConstants()
        sampPerCyc = int(constants.patchSealSampRate/constants.patchSealFreq)
        
        try: 
            curOutCyc = curOut.reshape(int(curOut.size/sampPerCyc), sampPerCyc)
            curData = np.mean(curOutCyc, axis = 0)
        except:
            curData = curOut
        
        voltData = voltOut 
        try:
            #Computing resistance
            tres = np.mean(voltData)
            dV = np.mean(voltData[voltData>tres])-np.mean(voltData[voltData<tres]) #Computing the voltage difference
            dIss = np.mean(curData[math.floor(0.15*sampPerCyc):math.floor(sampPerCyc/2)-2])-np.mean(curData[math.floor(0.65*sampPerCyc):sampPerCyc-2]) #Computing the current distance
            membraneResistance = dV/(dIss*1000000) #Ohms law (MegaOhm)
            self.resistanceLabel.setText("Resistance:  %.4f M\u03A9" % membraneResistance)
        except: 
            self.resistanceLabel.setText("Resistance:  %s" % 'NaN')
            
        try:
            #Computing capacitance
            points = 10
            maxCur = np.amax(curData)
            maxCurIndex = np.where(curData == maxCur)[0][0]
            curFit = curData[maxCurIndex+1:maxCurIndex+1+points]-0.5*(np.mean(curData[math.floor(0.15*sampPerCyc):math.floor(sampPerCyc/2)-2])+np.mean(curData[math.floor(0.65*sampPerCyc):sampPerCyc-2]))
            timepoints = np.arange(1, points+1)/constants.patchSealSampRate
            #Fitting the data to an exponential of the form y=a*exp(-b*x) where b = 1/tau and tau = RC
            fit = np.polyfit(timepoints, np.log(curFit), 1) #Converting the exponential to a linear function and fitting it  
            #Extracting data
            current = fit[0]
            resistance = dV/current/2 #Getting the resistance
            tau = 1/fit[1] 
            capacitance = tau/resistance
            self.capacitanceLabel.setText("Capacitance:  %.4f" % capacitance)
        except:
            self.capacitanceLabel.setText("Capacitance:  %s" % 'NaN')
        
    def stopMeasurement(self):
        """Stop the seal test."""
        self.sealTest.aboutToQuitHandler()
        
    def closeEvent(self, event):
        """On closing the application we have to make sure that the measuremnt
        stops and the device gets freed."""
        self.stopMeasurement()
    
    #Change gain
    def changeVolInGain(self, gain):
        if gain == '1':
            self.inVolGain = 1
        elif gain == '1/10':
            self.inVolGain = 0.1
        elif gain == '1/50':
            self.inVolGain = 1./50
        
    def changeVolOutGain(self, gain):
        self.outVolGain = float(gain)
    
    def changeCurOutGain(self, gain):
        self.outCurGain = float(gain)
    
    def changeProbeGain(self, gain):
        if gain == '100M\u03A9':
            self.probeGain = 100*10**6
        elif gain == '10G\u03A9':
            self.probeGain = 10*10**9
        
if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        mainwin = PatchclampSealTestUI()
        mainwin.show()
        app.exec_()
    run_app()