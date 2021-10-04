# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 11:29:23 2019

@author: lhuismans

We could think of not using the with statement for communicating with the DAQ.
If we do this there should be a method for closing the Task. 
This could be done with the delete dunder (__del__):
    https://eli.thegreenplace.net/2009/06/12/safely-using-destructors-in-python/
Or adding a close() method which should be called each time.

However using close() will result in the Task not being closed if the program shows
any exceptions.

Concept derived from: 
    https://stackoverflow.com/questions/974813/cleaning-up-an-internal-pysqlite-connection-on-object-destruction
"""
from __future__ import division
from constants import HardwareConstants
from configuration import Configuration

import nidaqmx
import numpy as np

from nidaqmx.stream_readers import AnalogSingleChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter
    
class TwoPScan:
    def __init__(self):
        self.hardwConst = HardwareConstants()
        self.configs = Configuration()
        
        self.sampleRate = 5000
        
    def injectTask(self, writeTask, readTask):
        """
        Inject the write and read task into the class so measurements can be done.
        """
        self.writeTask = writeTask
        self.readTask = readTask
        
        pmtChan = self.configs.pmtChannel
        xGalvoChan = self.configs.galvoXChannel
        yGalvoChan = self.configs.galvoYChannel
        
        self.writeTask.ao_channels.add_ao_voltage_chan(xGalvoChan)
        self.writeTask.ao_channels.add_ao_voltage_chan(yGalvoChan)
        self.readTask.ai_channels.add_ai_voltage_chan(pmtChan)
        
        self.writeTask.triggers.sync_type.SLAVE = True
        self.readTask.triggers.sync_type.MASTER = True
        
    def makeSinglePic(self, writeTask, readTask):
        #Check if the measurement is possible and execute
        if self.checkMeasurement():
            self.writeTask.timing.cfg_samp_clk_timing(rate = self.sampleRate,
                                                 sample_mode = nidaqmx.constants.AcquisitionType.FINITE,
                                                 samps_per_chan = self.outputData.size)
            self.readTask.timing.cfg_samp_clk_timing(rate = self.sampleRate,
                                                sample_mode = nidaqmx.constants.AcquisitionType.FINITE,
                                                samps_per_chan = self.inputData.size)              
            
            reader = AnalogSingleChannelReader(self.readTask.in_stream)
            writer = AnalogMultiChannelWriter(self.writeTask.out_stream)
    
            estT = self.outputData.size/self.sampleRate
            writer.write_many_sample(self.outputData)
            
            self.writeTask.start()
            reader.read_many_sample(self.inputData, timeout = estT+5)
            
            return self.inputData
    
    def checkMeasurement(self):
        """Check if the current settings could be used for a physically possible
        measurement. Returns False if not possible and True if possible. 
        Check if ramp up/down does not exceed maximum galvo speed""" 
        rampUpSpeed = (self.galvoXMax-self.galvoXMin)/self.xPixels
        
        if self.hardwConst.maxGalvoSpeed < rampUpSpeed:
            print("Set speed exceedsd maximum galvo speed")
            return False
        
        return True
    
    def setTrigger(self, trigger):
        trigger = str(trigger)
        self.writeTask.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source = trigger)
        
    def setOutput(self, xValues, yValues):
        """Set the output data, the format for the write task to be a 2D numpy array
        with the data for each channel on each row."""
        self.inputData = np.zeros(xValues.size+1)
        self.outputData = np.array([xValues, yValues])
        
    #--------------------------Python setter and getters-----------------------
    """
    For the use of properties see: 
        https://www.python-course.eu/python3_properties.php
    """
    
    @property
    def sampleRate(self):
        return self.__sampleRate
    
    @sampleRate.setter
    def sampleRate(self, sampleRate):
        self.__sampleRate = int(sampleRate)
        
    @property
    def imAngle(self):
        return self.__imAngle
    
    @imAngle.setter
    def imAngle(self, angle):
        self.__imAngle = int(angle)
        
    @property
    def galvoXMax(self):
        return self.__galvoXMax
    
    @galvoXMax.setter
    def galvoXMax(self, maxVolt):
        self.__galvoXMax = float(maxVolt)
        
    @property
    def galvoXMin(self):
        return self.__galvoXMin
    
    @galvoXMin.setter
    def galvoXMin(self, minVolt):
        self.__galvoXMin = float(minVolt)
        
    @property
    def galvoYMax(self):
        return self.__galvoYMax
    
    @galvoYMax.setter
    def galvoYMax(self, maxVolt):
        self.__galvoYMax = float(maxVolt)
        
    @property
    def galvoYMin(self):
        return self.__galvoYMin
    
    @galvoYMin.setter
    def galvoYMin(self, minVolt):
        self.__galvoYMin = float(minVolt)
        
    @property
    def xPixels(self): 
        return self.__xPixels
    
    @xPixels.setter
    def xPixels(self, pixels):
        self.__xPixels = int(pixels)
        
    @property
    def yPixels(self):
        return self.__yPixels
    
    @yPixels.setter
    def yPixels(self, pixels):
        self.__yPixels = int(pixels)
        
    @property
    def sawtooth(self):
        return self.__sawtooth
    
    @sawtooth.setter
    def sawtooth(self, sawtooth):
        self.__sawtooth = bool(sawtooth)
        
    @property
    def outputData(self):
        return self.__outputData
    
    @outputData.setter
    def outputData(self, outputData):
        self.__outputData = outputData.astype(float)