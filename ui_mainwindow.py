# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 14:16:53 2019

@author: lhuismans
"""
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QGridLayout, QPushButton, QGroupBox, QVBoxLayout, QComboBox, QLineEdit

import sys
import ui_configurationwindow
import ui_patchclamp_sealtest
from configuration import Configuration

try:
   import cPickle as pickle
except:
   import pickle

class MainWindow(QMainWindow):
    def __init__(self):
        #------------------Loading the configurations--------------------------
        """Open the configuration object."""
        self.configs = Configuration()
        
        #------------------Initializing the GUI--------------------------------
        QMainWindow.__init__(self)
        
        self.setMinimumSize(240, 180)
        self.setWindowTitle("Main Window")
        
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        
        #-------------------Basic Measurements---------------------------------
        basicMeasurementContainer = QGroupBox("Basic Measuremetns")
        self.basicMeasurementLayout = QVBoxLayout()
        
        self.stageButton = QPushButton("Stage")
        self.basicMeasurementLayout.addWidget(self.stageButton)
        
        self.patchclampSealTestButton = QPushButton("Patchclamp Seal Test")
        self.basicMeasurementLayout.addWidget(self.patchclampSealTestButton)
        self.patchclampSealTestButton.clicked.connect(lambda: self.openPatchclampSealTest())
        
        self.dmdButton = QPushButton("DMD")
        self.basicMeasurementLayout.addWidget(self.dmdButton)
        
        self.laserButton = QPushButton("2P-laser scanner")
        self.basicMeasurementLayout.addWidget(self.laserButton)
        self.laserButton.clicked.connect(lambda: self.openLaser())
        
        self.cameraButton = QPushButton("Camera")
        self.basicMeasurementLayout.addWidget(self.cameraButton)
        
        basicMeasurementContainer.setLayout(self.basicMeasurementLayout)
        
        #-------------------Configuration--------------------------------------
        self.configurationButton = QPushButton("Configurations")
        self.configurationButton.clicked.connect(lambda: self.openConfig())
        
        #-------------------Test Singleton------------------------------------
        self.singletonTestButton = QPushButton("Show configuration")
        self.singletonTestButton.clicked.connect(lambda: self.printConfig())
        
        #--------------------Adding everything to central widget---------------
        master = QVBoxLayout() #Containing all the components
        master.addWidget(basicMeasurementContainer)
        master.addWidget(self.configurationButton)
        master.addWidget(self.singletonTestButton)
        centralWidget.setLayout(master)
    
    def openPatchclampSealTest(self):
        """Opens the patchclamp window."""
        patchWindow = ui_patchclamp_sealtest.PatchclampSealTestUI()
        patchWindow.show()
        
    def openLaser(self):
        """Opens the 2p laser scanner window."""
        print("Opened laser scanner")
        
    def openConfig(self):
        """Opens the configuration window"""
        configWindow = ui_configurationwindow.ConfigurationWindow()
        configWindow.show()
        
    def printConfig(self):
        print("Filter 1: ", self.configs.filter1Port)
        print("Filter 2: ", self.configs.filter2Port)
        print("Filter 3: ", self.configs.filter3Port)
        print("DMD Port: ", self.configs.dmdPort)
        print("DMD Serial Number: ", self.configs.dmdSerialNumber)
        print("Stage Port: ", self.configs.stagePort)
        
        print("Patchclamp Voltage-in Channel: ", self.configs.patchVoltInChannel)
        print("Patchclamp Voltage-out Channel: ", self.configs.patchVoltOutChannel)    
        print("Patchclamp Current-out Channel: ", self.configs.patchCurOutChannel)
        print("PMT Channel: ", self.configs.pmtChannel)
        print("AOTF Channel: ", self.configs.aotfChannel)
        print("Galvo x Channel: ", self.configs.galvoXChannel)
        print("Galvo y Channel: ", self.configs.galvoYChannel)
        
        print("Clock1: ", self.configs.clock1Channel)
        print("Clock2: ", self.configs.clock2Channel)
        print("Trigger1: ", self.configs.trigger1Channel)
        print("Trigger2: ", self.configs.trigger2Channel)
        
if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        mainWin = MainWindow()
        mainWin.show()
        app.exec_()
    run_app()