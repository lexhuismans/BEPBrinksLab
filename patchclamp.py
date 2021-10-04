# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 12:21:01 2019

@author: lhuismans

Notes:
    
"""
import nidaqmx
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogSingleChannelWriter

from PyQt5.QtCore import pyqtSignal, QThread

import numpy as np

from configuration import Configuration
from wavegenerator import blockWave
from constants import MeasurementConstants

class ContinuousPatchThread(QThread):
    """
    Class for performing a continuous patchclamp measurement. It inherits the
    QThread so the main python code still runs while the measurment is done.
    """
    measurement = pyqtSignal(np.ndarray, np.ndarray) #The signal for the measurement, we can connect to this signal
    def __init__(self, wave, sampleRate, readNumber, *args, **kwargs):
        """
        wave is the output data
        sampleRate is the sampleRate of the DAQ
        readNumber is the 
        """
        super().__init__(*args, **kwargs)
        self.patchVoltInChan = None
        self.patchVoltOutChan = None
        self.patchCurOutChan = None
        
        self.sampleRate = sampleRate
        self.readNumber = readNumber
        
        self.wave = wave
        
        self.configs = Configuration()
    
    def setTiming(self, writeTask, readTask):
        #Check if they are on the same device
        readDev = self.patchCurOutChan.split('/')[0]
        writeDev = self.patchVoltInChan.split('/')[0]
        
        #Check if they are on the same device
        if readDev == writeDev: 
            writeClock = '/' + self.patchCurOutChan.split('/')[0] + '/ai/SampleClock' #Getting the device and its sampleClock 
        elif readDev == self.configs.clock1Channel.split('/')[1]: #Checking if readTask is on same device as clock1.
            readTask.export_signals.samp_clk_output_term = self.configs.clock1Channel
            writeClock = self.configs.clock2Channel
        elif readDev == self.configs.clock2Channel.split('/')[1]:
            readTask.export_signals.samp_clk_output_term = self.configs.clock2Channel
            writeClock = self.configs.clock1Channel
        else:
            assert(True, "No corresponding clocks defined")
                
        readTask.timing.cfg_samp_clk_timing(rate = self.sampleRate,
                                                sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS,
                                                samps_per_chan = self.readNumber) #Read number is used to determine the buffer size.
        writeTask.timing.cfg_samp_clk_timing(rate = self.sampleRate,
                                                source=writeClock,
                                                sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS)
            
    def run(self):
        """
        Starts writing a waveform continuously to the patchclamp. While reading 
        the buffer periodically
        """
        self.patchVoltOutChan = self.configs.patchVoltOutChannel
        self.patchCurOutChan = self.configs.patchCurOutChannel
        self.patchVoltInChan = self.configs.patchVoltInChannel
        
        #DAQ
        with nidaqmx.Task() as writeTask, nidaqmx.Task() as readTask:  
            writeTask.ao_channels.add_ao_voltage_chan(self.patchVoltInChan)
            readTask.ai_channels.add_ai_voltage_chan(self.patchVoltOutChan)
            readTask.ai_channels.add_ai_voltage_chan(self.patchCurOutChan)
            
            self.setTiming(writeTask, readTask)
            
            reader = AnalogMultiChannelReader(readTask.in_stream)
            writer = AnalogSingleChannelWriter(writeTask.out_stream)
            
            writer.write_many_sample(self.wave)
            
            """Reading data from the buffer in a loop. 
            The idea is to let the task read more than could be loaded in the buffer for each iteration.
            This way the task will have to wait slightly longer for incoming samples. And leaves the buffer
            entirely clean. This way we always know the correct numpy size and are always left with an empty
            buffer (and the buffer will not slowly fill up)."""
            output = np.zeros([2, self.readNumber])
            writeTask.start() #Will wait for the readtask to start so it can use its clock
            readTask.start()
            while not self.isInterruptionRequested():
                reader.read_many_sample(data = output, 
                                        number_of_samples_per_channel = self.readNumber)
                
                #Emiting the data just received as a signal
                #output = np.around(output, 7) #Round all values
                self.measurement.emit(output[0,:], output[1,:])    
          
class PatchclampSealTest:
    """Class for doing a patchclamp seal test. A continuous measurement can be done
    of which the data is returned continuously as well.
    We want to use the nidaqmx.task.timing to assign a clock and a conversion rate to the task.
    Then we need to make sure to call the read function regularly to read all the samples automatically generated by the card.
    
    The measurement for the sealtest does not need to be checked. Only a pop up window in the UI provided asking if the gains
    set in the UI are corresponding to the gains on the patchclamp.
    """
    def __init__(self):
        """Initiate all the values."""
        self.constants = MeasurementConstants()
        self.sampleRate = self.constants.patchSealSampRate
        self.frequency = self.constants.patchSealFreq
        self.voltMin = self.constants.patchSealMinVol
        self.voltMax = self.constants.patchSealMaxVol
        self.dutycycle = self.constants.patchSealDuty
        self.readNumber= 1000 #Readnumber for the measurementThread (should be a multiple of the wavelength)
        
        wave = blockWave(self.sampleRate, self.frequency, self.voltMin, self.voltMax, self.dutycycle)
        self.measurementThread = ContinuousPatchThread(wave, self.sampleRate, self.readNumber)
    
    def setWave(self, inVolGain):
        self.voltMax = self.constants.patchSealMaxVol/inVolGain
        self.measurementThread.wave = blockWave(self.sampleRate, self.frequency,
                                                self.voltMin, self.voltMax, 
                                                self.dutycycle)
        
    def start(self):
        self.measurementThread.start() #Start executing what is inside run()
    
    def aboutToQuitHandler(self):
        self.measurementThread.requestInterruption()
        self.measurementThread.wait()
      
