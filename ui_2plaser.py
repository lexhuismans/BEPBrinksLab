import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QGroupBox, QVBoxLayout, QHBoxLayout, QLineEdit, QRadioButton
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QPen, QColor
from PyQt5.QtCore import Qt

import numpy as np
import matplotlib.pyplot as plt

#Importing self made modules
import wavegenerator
import measure
from configuration import Configuration
from twophotonlaser import TwoPScan

#Import and configure PyQtGraph stuff.
import pyqtgraph as pg
pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'w')
pg.setConfigOption('useOpenGL', True)
pg.setConfigOption('leftButtonPan', False)

class TwoPLaser(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.twoPhotonLaser = TwoPScan()
        
        #-------------------------For the user interface-----------------------
        self.setMinimumSize(100, 100)    
        self.setWindowTitle("Two Photon Laser Scanner") 
        
        #--------------------------For the entries-----------------------------
        settingsBox = QGroupBox("Settings")
        settings = QGridLayout()
        self.sRate = QLineEdit("5000")
        self.imAngle = QLineEdit("0")
        self.VxMin = QLineEdit("0")
        self.VxMax = QLineEdit("5")
        self.VyMin = QLineEdit("0")
        self.VyMax = QLineEdit("5")
        self.xPixels = QLineEdit("1024")
        self.yPixels = QLineEdit("512")
        
        #-------------Validate that inputs are integers------------------------
        self.sRate.setValidator(QIntValidator())
        self.imAngle.setValidator(QIntValidator())
        self.VxMin.setValidator(QDoubleValidator())
        self.VxMax.setValidator(QDoubleValidator())
        self.VyMin.setValidator(QDoubleValidator())
        self.VyMax.setValidator(QDoubleValidator())
        self.xPixels.setValidator(QIntValidator())
        self.yPixels.setValidator(QIntValidator())
        
        #Button to set variables
        
        settings.addWidget(QLabel("Sample Rate"), 0, 0) 
        settings.addWidget(QLabel("Image Angle"), 1, 0)
        settings.addWidget(QLabel("Min Voltage X"), 2, 0)
        settings.addWidget(QLabel("Max Voltage X"), 3, 0)
        settings.addWidget(QLabel("Min Voltage Y"), 4, 0)
        settings.addWidget(QLabel("Max Voltage Y"), 5, 0)
        settings.addWidget(QLabel("Pixels in X"), 6, 0)
        settings.addWidget(QLabel("Pixels in Y"), 7, 0)
        settings.addWidget(self.sRate, 0, 1)
        settings.addWidget(self.imAngle, 1,1)
        settings.addWidget(self.VxMin, 2, 1)
        settings.addWidget(self.VxMax, 3, 1)
        settings.addWidget(self.VyMin, 4, 1)
        settings.addWidget(self.VyMax, 5, 1)
        settings.addWidget(self.xPixels, 6, 1)
        settings.addWidget(self.yPixels, 7, 1)
        settingsBox.setLayout(settings)
        
        #-----------------------For the waveform-------------------------------
        waveformBox = QGroupBox("Waveform")
        waveform = QHBoxLayout()
        self.radioSawtooth = QRadioButton("Sawtooth")
        self.radioTriangle = QRadioButton("Triangle")
        self.radioSawtooth.setChecked(True)
        waveform.addWidget(self.radioSawtooth)
        waveform.addWidget(self.radioTriangle)
        waveformBox.setLayout(waveform)
        
        #---------------------For the measurements-----------------------------
        measureBox = QGroupBox("Measure")
        measure = QHBoxLayout()
        self.measureButton = QPushButton("Measure")
        self.measureButton.clicked.connect(self.measure)
        self.calibrateButton = QPushButton("Calibrate")
        self.calibrateButton.clicked.connect(self.calibrate)
        measure.addWidget(self.measureButton)
        measure.addWidget(self.calibrateButton)
        measureBox.setLayout(measure)
        
        #------------------------For the live graph----------------------------
        self.plotWidget = pg.PlotWidget()
        self.plotWidget.showGrid(x = True, y = True, alpha = 0.3)
        #Setting the pen
        self.pen = QPen()
        self.pen.setColor(QColor(145,255,244))
        self.pen.setWidth(.7)
        self.pen.setStyle(Qt.DashLine)
        self.plot = self.plotWidget.plot(pen=self.pen)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updatePreview)
        self.timer.start(500)
        
        #-----------------Adding everything to the sorting containers----------
        leftPanel = QVBoxLayout()
        leftPanel.addWidget(settingsBox)
        leftPanel.addWidget(waveformBox)
        leftPanel.addWidget(measureBox)
        
        self.rightPanel = QHBoxLayout()
        self.rightPanel.addWidget(self.plotWidget)
        
        master = QHBoxLayout()
        master.addLayout(leftPanel)
        master.addLayout(self.rightPanel)
        
        self.setLayout(master)
      
    def updatePreview(self):
        """Updates the preview window"""
        #Plotting the graph
        #Checking if sawtooth or triangle wave should be plotted
        if self.radioSawtooth.isChecked():
            sawtooth = True
        else:
            sawtooth = False
        
        try:#Try to get the values   
            xValues, lineSize = wavegenerator.xValuesSingleSawtooth(int(self.sRate.text()),
                                    float(self.VxMin.text()),
                                    float(self.VxMax.text()),
                                    int(self.xPixels.text()),
                                    sawtooth)
        except: #If not all values are filled in the default values are used
            print("Using default")
            xValues, lineSize = wavegenerator.xValuesSingleSawtooth()
        twolineXValues = np.append(xValues, xValues)    
        self.plot.setData(twolineXValues)
    
    def calibrate(self):
        """Starts a calibration measurement"""
        #Plotting the graph
        #Checking if sawtooth or triangle wave should be plotted
        if self.radioSawtooth.isChecked():
            sawtooth = True
        else:
            sawtooth = False
        
        try:#Try to get the values   
            xValues, yValues = wavegenerator.genSawtooth(int(self.sRate.text()),
                                    int(self.imAngle.text()),
                                    float(self.VxMax.text()),
                                    float(self.VyMax.text()),
                                    float(self.VyMin.text()),
                                    float(self.VxMin.text()),
                                    int(self.xPixels.text()),
                                    int(self.yPixels.text()),
                                    sawtooth)
        except: #If not all values are filled in the default values are used
            print("Using default")
            xValues, yValues = wavegenerator.genSawtooth()
         
        outputData, inputData = measure.calibrate(int(self.sRate.text()), self.aiChannel.currentText(), 
                                                  self.aoChannelX.currentText(), xValues)
        
        tValues = np.arange(inputData.size)    
        #Plotting the data (feedback)
        plt.plot(tValues, outputData, 'b', tValues, inputData, 'r')
        plt.show()
    
    def setValues(self):
        self.twoPhotonLaser.sampleRate = self.sRate.text()
        self.twoPhotonLaser.imAngle = self.imAngle.text()
        self.twoPhotonLaser.galvoXMin = self.VxMin.text()
        self.twoPhotonLaser.galvoXMax = self.VxMax.text()
        self.twoPhotonLaser.galvoYMin = self.VyMin.text()
        self.twoPhotonLaser.galvoYMax = self.VyMax.text()
        self.twoPhotonLaser.xPixels = self.xPixels.text()
        self.twoPhotonLaser.yPixels = self.yPixels.text()
        self.twoPhotonLaser.sawtooth = self.radioSawtooth.isChecked()

    def measure(self):
        #Setting all the values to the measurement
        self.setValues()
        
        #Getting the x and y output
        try:#Try to get the values   
            xValues, yValues = wavegenerator.waveRecPic(self.twoPhotonLaser.sampleRate,
                                self.twoPhotonLaser.imAngle,
                                self.twoPhotonLaser.galvoXMin,
                                self.twoPhotonLaser.galvoXMax,
                                self.twoPhotonLaser.galvoYMin,
                                self.twoPhotonLaser.galvoYMax,
                                self.twoPhotonLaser.xPixels,
                                self.twoPhotonLaser.yPixels,
                                self.twoPhotonLaser.sawtooth)
        except: #If not all values are filled in the default values are used
            print("Using default")
            xValues, yValues = wavegenerator.waveRecPic()
        
        with nidaqmx.Task() as writeTask, nidaqmx.Task() as readTask:
            
        
        """
        self.twoPhotonLaser.setOutput(xValues, yValues)
        
        pmtOutput = self.twoPhotonLaser.measure()
        print(pmtOutput)
        """

if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        mainWin = TwoPLaser()
        mainWin.show()
        app.exec_()
    run_app()
