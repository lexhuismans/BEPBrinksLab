# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 15:52:06 2019

@author: lhuismans

Notes:
    We still have to implement that the GUI gets saved.

"""
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QGroupBox, QVBoxLayout, QComboBox, QLineEdit

import sys
import nidaqmx
try:
   import cPickle as pickle
except:
   import pickle

from configuration import Configuration

class ConfigurationWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(480,640)
        self.setWindowTitle("Configuration panel")
        
        configs = Configuration()
        #----------------For non-DAQ configurations----------------------------
        nonDaqContainer = QGroupBox("Non-DAQ") #Containter containing Non-DAQ ports
        self.nonDaqLayout = QGridLayout() #Layout manager for Non-DAQ container
        #Adding all the labels
        self.filter1Entry = QLineEdit(configs.filter1Port)
        self.nonDaqLayout.addWidget(self.filter1Entry, 0, 1)
        self.nonDaqLayout.addWidget(QLabel("Filter 1"), 0, 0)
        
        self.filter2Entry = QLineEdit(configs.filter2Port)
        self.nonDaqLayout.addWidget(self.filter2Entry, 1, 1)
        self.nonDaqLayout.addWidget(QLabel("Filter 2"), 1, 0)
        
        self.filter3Entry = QLineEdit(configs.filter3Port)
        self.nonDaqLayout.addWidget(self.filter3Entry, 2, 1)
        self.nonDaqLayout.addWidget(QLabel("Filter 3"), 2, 0)
        
        self.dmdEntry = QLineEdit(configs.dmdPort)
        self.nonDaqLayout.addWidget(self.dmdEntry, 3, 1)
        self.nonDaqLayout.addWidget(QLabel("DMD Port"), 3, 0)
        
        self.dmdSerialNumberEntry = QLineEdit(str(configs.dmdSerialNumber))
        self.nonDaqLayout.addWidget(self.dmdSerialNumberEntry, 4, 1)
        self.nonDaqLayout.addWidget(QLabel("DMD Serial Number"), 4, 0)
        
        self.stageEntry = QLineEdit(configs.stagePort)
        self.nonDaqLayout.addWidget(self.stageEntry, 5, 1)
        self.nonDaqLayout.addWidget(QLabel("Stage port"), 5, 0)
        nonDaqContainer.setLayout(self.nonDaqLayout)
        
        #----------------------------------------------------------------------
        #-------------For DAQ configuration------------------------------------
        #----------------------------------------------------------------------
        daqContainer = QGroupBox("DAQ")
        daqContainerLayout = QVBoxLayout()
        
        daqrestContainer = QGroupBox("Rest")
        self.daqLayout = QGridLayout()
        
        patchContainer = QGroupBox("Patchclamp")
        self.patchLayout = QGridLayout()
        
        timingContainer = QGroupBox("Timing")
        self.timingLayout = QGridLayout()
        
        #--------------------Adding all the labels-----------------------------
        #Patchclamp
        self.patchLayout.addWidget(QLabel("Patchclamp Voltage-In"), 0, 0)
        self.patchLayout.addWidget(QLabel("Patchlamp Voltage-Out"), 1, 0)
        self.patchLayout.addWidget(QLabel("Patchclamp Current-Out"), 2, 0)
        #Others
        self.daqLayout.addWidget(QLabel("PMT"), 1, 0)
        self.daqLayout.addWidget(QLabel("AOTF"), 2, 0)
        self.daqLayout.addWidget(QLabel("Galvo x"), 3, 0)
        self.daqLayout.addWidget(QLabel("Galvo y"), 4, 0)
        self.daqLayout.addWidget(QLabel("2p shutter"), 5, 0)
        self.daqLayout.addWidget(QLabel("488 shutter"), 6, 0)
        self.daqLayout.addWidget(QLabel("640 shutter"), 7, 0)
        #Timing
        self.timingLayout.addWidget(QLabel("Trigger port 1"), 0, 0)
        self.timingLayout.addWidget(QLabel("Trigger port 2"), 1, 0)
        self.timingLayout.addWidget(QLabel("Clock port 1"), 2, 0)
        self.timingLayout.addWidget(QLabel("Clock port 2"), 3, 0)
        
        #--------------------------Adding comboboxes---------------------------
        #Patchclamp
        #Patch volt in
        self.devPatchVoltIn = QComboBox()
        self.channelPatchVoltIn = QComboBox()
        self.devPatchVoltIn.currentIndexChanged.connect(lambda: self.changeDevice(self.devPatchVoltIn, 
                                                                         self.channelPatchVoltIn,
                                                                         True))
        self.addDevices(self.devPatchVoltIn)
        self.patchLayout.addWidget(self.devPatchVoltIn, 0, 1)
        self.patchLayout.addWidget(self.channelPatchVoltIn, 0, 2)
        #Patch volt out
        self.devPatchVoltOut = QComboBox()
        self.channelPatchVoltOut = QComboBox()
        self.devPatchVoltOut.currentIndexChanged.connect(lambda: self.changeDevice(self.devPatchVoltOut, 
                                                                         self.channelPatchVoltOut,
                                                                         False))
        self.addDevices(self.devPatchVoltOut)
        self.patchLayout.addWidget(self.devPatchVoltOut, 1, 1)
        self.patchLayout.addWidget(self.channelPatchVoltOut, 1, 2)
        #Patch current out
        self.devPatchCurOut = QComboBox()
        self.channelPatchCurOut = QComboBox()
        self.devPatchCurOut.currentIndexChanged.connect(lambda: self.changeDevice(self.devPatchCurOut, 
                                                                         self.channelPatchCurOut,
                                                                         False))
        self.addDevices(self.devPatchCurOut)
        self.patchLayout.addWidget(self.devPatchCurOut, 2, 1)
        self.patchLayout.addWidget(self.channelPatchCurOut, 2, 2)
        
        #Others
        #pmt
        self.devPMT = QComboBox()
        self.channelPMT = QComboBox()
        self.devPMT.currentIndexChanged.connect(lambda: self.changeDevice(self.devPMT, 
                                                                  self.channelPMT,
                                                                  False))
        
        self.addDevices(self.devPMT)
        self.daqLayout.addWidget(self.devPMT, 1, 1)
        self.daqLayout.addWidget(self.channelPMT, 1, 2)
        #AOTF
        self.devAOTF = QComboBox()
        self.channelAOTF = QComboBox()
        self.devAOTF.currentIndexChanged.connect(lambda: self.changeDevice(self.devAOTF, 
                                                                  self.channelAOTF,
                                                                  True))
        
        self.addDevices(self.devAOTF)
        self.daqLayout.addWidget(self.devAOTF, 2, 1)
        self.daqLayout.addWidget(self.channelAOTF, 2, 2)
        #galvo x
        self.devGalvoX = QComboBox()
        self.channelGalvoX = QComboBox()
        self.devGalvoX.currentIndexChanged.connect(lambda: self.changeDevice(self.devGalvoX, 
                                                                  self.channelGalvoX,
                                                                  True))
        
        self.addDevices(self.devGalvoX)
        self.daqLayout.addWidget(self.devGalvoX, 3, 1)
        self.daqLayout.addWidget(self.channelGalvoX, 3, 2)
        #galvo y
        self.devGalvoY = QComboBox()
        self.channelGalvoY = QComboBox()
        self.devGalvoY.currentIndexChanged.connect(lambda: self.changeDevice(self.devGalvoY, 
                                                                  self.channelGalvoY,
                                                                  True))
        
        self.addDevices(self.devGalvoY)
        self.daqLayout.addWidget(self.devGalvoY, 4, 1)
        self.daqLayout.addWidget(self.channelGalvoY, 4, 2)
        #2p shutter
        self.dev2pShutter = QComboBox()
        self.channel2pShutter = QComboBox()
        self.dev2pShutter.currentIndexChanged.connect(lambda: self.changeDevice(self.dev2pShutter, 
                                                                  self.channel2pShutter,
                                                                  True, 1))
        
        self.addDevices(self.dev2pShutter)
        self.daqLayout.addWidget(self.dev2pShutter, 5, 1)
        self.daqLayout.addWidget(self.channel2pShutter, 5, 2)
        #488 shutter
        self.dev488Shutter = QComboBox()
        self.channel488Shutter = QComboBox()
        self.dev488Shutter.currentIndexChanged.connect(lambda: self.changeDevice(self.dev488Shutter, 
                                                                  self.channel488Shutter,
                                                                  True, 1))
        
        self.addDevices(self.dev488Shutter)
        self.daqLayout.addWidget(self.dev488Shutter, 6, 1)
        self.daqLayout.addWidget(self.channel488Shutter, 6, 2)
        #640 shutter
        self.dev640Shutter = QComboBox()
        self.channel640Shutter = QComboBox()
        self.dev640Shutter.currentIndexChanged.connect(lambda: self.changeDevice(self.dev640Shutter, 
                                                                  self.channel640Shutter,
                                                                  True, 1))
        
        self.addDevices(self.dev640Shutter)
        self.daqLayout.addWidget(self.dev640Shutter, 7, 1)
        self.daqLayout.addWidget(self.channel640Shutter, 7, 2)
        
        #Timing
        #Trigger 1
        self.devTrigger1 = QComboBox()
        self.channelTrigger1 = QComboBox()
        self.devTrigger1.currentIndexChanged.connect(lambda: self.changeDevice(self.devTrigger1, 
                                                                  self.channelTrigger1,
                                                                  True, 2))
        
        self.addDevices(self.devTrigger1)
        self.timingLayout.addWidget(self.devTrigger1, 0, 1)
        self.timingLayout.addWidget(self.channelTrigger1, 0, 2)
        #Trigger 2
        self.devTrigger2 = QComboBox()
        self.channelTrigger2 = QComboBox()
        self.devTrigger2.currentIndexChanged.connect(lambda: self.changeDevice(self.devTrigger2, 
                                                                  self.channelTrigger2,
                                                                  True, 2))
        
        self.addDevices(self.devTrigger2)
        self.timingLayout.addWidget(self.devTrigger2, 1, 1)
        self.timingLayout.addWidget(self.channelTrigger2, 1, 2)
        #Clock 1
        self.devClock1 = QComboBox()
        self.channelClock1 = QComboBox()
        self.devClock1.currentIndexChanged.connect(lambda: self.changeDevice(self.devClock1, 
                                                                  self.channelClock1,
                                                                  True, 2))
        
        self.addDevices(self.devClock1)
        self.timingLayout.addWidget(self.devClock1, 2, 1)
        self.timingLayout.addWidget(self.channelClock1, 2, 2)
        #Clock 2
        self.devClock2 = QComboBox()
        self.channelClock2 = QComboBox()
        self.devClock2.currentIndexChanged.connect(lambda: self.changeDevice(self.devClock2, 
                                                                  self.channelClock2,
                                                                  True, 2))
        
        self.addDevices(self.devClock2)
        self.timingLayout.addWidget(self.devClock2, 3, 1)
        self.timingLayout.addWidget(self.channelClock2, 3, 2)
        
        #Creating and adding containers
        daqrestContainer.setLayout(self.daqLayout)
        patchContainer.setLayout(self.patchLayout)
        timingContainer.setLayout(self.timingLayout)
        
        daqContainerLayout.addWidget(daqrestContainer)
        daqContainerLayout.addWidget(patchContainer)
        daqContainerLayout.addWidget(timingContainer)
        
        daqContainer.setLayout(daqContainerLayout)
        
        #-------------Apply button---------------------------------------------
        self.applyButton = QPushButton("Apply")
        self.applyButton.clicked.connect(self.applyConfiguration)
        
        #--------------Adding to master----------------------------------------
        master = QVBoxLayout()
        master.addWidget(nonDaqContainer)
        master.addWidget(daqContainer)
        master.addWidget(self.applyButton)
        
        self.setLayout(master)
        
    def addDevices(self, devicebox):
        """Add or change the devices from the dropdown menu. 
        devicebox specifies the combobox where we want to add the devices"""
        devicebox.clear() #Removing old entries
        
        system = nidaqmx.system.System.local()
        for device in system.devices: #Looping over all the devices and adding them to the combobox
            devicebox.addItem(device.name)
        
    def changeDevice(self, devicebox, channelbox, output, portType = 0):
        """Add or change the analog channels from the dropdown menu. channelbox is the combobox
        that needs the channels added. 
        devicebox is the corresponding devicebox. This is needed to supply the right channels.
        output specifies if output or input channesl are needed: 
        True for output, 
        False for input.
        The type of port is selected with portType:
            0: analog
            1: digital
            2: PFI
        """
        deviceName = str(devicebox.currentText())
        channelbox.clear() #Removing old entries
        device = nidaqmx.system.device.Device(deviceName) #Checking which device is selected
        if portType == 0:
            if output:
                for ao in device.ao_physical_chans: #Looping over all the output channels and adding them to the combobox
                    channelbox.addItem(ao.name)
            else: 
                for ai in device.ai_physical_chans: #Looping over all the input channels and adding them to the combobox
                    channelbox.addItem(ai.name)
        elif portType == 1:
            if output:
                for do in device.do_lines:
                    channelbox.addItem(do.name)
            else:
                for di in device.di_ports:
                    channelbox.addItem(di.name)
        elif portType == 2:
            if output:
                for tr in device.terminals:
                    channelbox.addItem(tr)
                
    def applyConfiguration(self):
         """Apply all the configurations."""
         #Open the configuration class
         configs = Configuration()
         
         configs.dmdPort = self.dmdEntry.text()
         configs.dmdSerialNumber = self.dmdSerialNumberEntry.text()
         configs.stagePort = self.stageEntry.text()
         configs.filter1Port = self.filter1Entry.text()
         configs.filter2Port = self.filter2Entry.text()
         configs.filter3Port = self.filter3Entry.text()
         
         configs.aotfChannel = self.channelAOTF.currentText()
         configs.patchVoltInChannel = self.channelPatchVoltIn.currentText()
         configs.patchVoltOutChannel = self.channelPatchVoltOut.currentText()
         configs.patchCurOutChannel = self.channelPatchCurOut.currentText()
         configs.galvoXChannel = self.channelGalvoX.currentText()
         configs.galvoYChannel = self.channelGalvoY.currentText()
         configs.pmtChannel = self.channelPMT.currentText()
         
         configs.trigger1Channel = self.channelTrigger1.currentText()
         configs.trigger2Channel = self.channelTrigger2.currentText()
         configs.clock1Channel = self.channelClock1.currentText()
         configs.clock2Channel = self.channelClock2.currentText()
         configs.saveVariables()
         
         print("Configurations saved succesfully")
if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        configWin = ConfigurationWindow()
        configWin.show()
        app.exec_()
    run_app()