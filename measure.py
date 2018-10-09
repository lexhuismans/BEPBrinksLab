import matplotlib.pyplot as plt
import numpy as np
import math
import nidaqmx
from nidaqmx.stream_writers import AnalogSingleChannelWriter
from nidaqmx.stream_readers import AnalogSingleChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter

def sawtooth(ai_chan, ao_chan_x, ao_chan_y, sRate, imAngle, outputX, outputY, xPixels, yPixels, exPixels):
    """
    Notes:
        Variables:
            ai_chan = string specifying the analog input channel
            ao_chan_x, ao_chan_y = string, specifying the analog output channel for x and y
    
    """
    print("Measurement started")
    writingRate = sRate
    readingRate = writingRate
    
    #radAngle = math.pi/180*imAngle
    #exPixelsX = int(math.cos(radAngle)*exPixels) #Amount of excess pixels in X
    #exPixelsY = int(math.sin(radAngle)*exPixels) #Amount of excess pixels in Y
    
    totalxPixels = exPixels+xPixels
    totalyPixels = yPixels
    
    print("total x pixels", totalxPixels, "xpixels", xPixels, "exPixels", exPixels)
    inputData = np.zeros(outputX.size+1) #Need the extra one because of the sample shift due to the trigger
    outputData = np.array([outputX, outputY])
    outputChannels = ao_chan_x + ", " + ao_chan_y
    with nidaqmx.Task() as writeTask, nidaqmx.Task() as readTask:  
            writeTask.ao_channels.add_ao_voltage_chan(outputChannels)
            readTask.ai_channels.add_ai_voltage_chan(ai_chan)
            
            #In the USB6001 DAQ there seems to be no SampleClock, therefore we cannot sync the signals without an external trigger/clock
            #sample_clock = '/Dev2/ai/SampleClock'
            
            writeTask.timing.cfg_samp_clk_timing(rate = writingRate,
                                                 sample_mode = nidaqmx.constants.AcquisitionType.FINITE,
                                                 samps_per_chan = outputX.size)
            readTask.timing.cfg_samp_clk_timing(rate = readingRate,
                                                sample_mode = nidaqmx.constants.AcquisitionType.FINITE,
                                                samps_per_chan = inputData.size)              
            writeTask.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source = '/Dev2/ai/StartTrigger') #Setting the trigger on the analog input
            
            reader = AnalogSingleChannelReader(readTask.in_stream)
            writer = AnalogMultiChannelWriter(writeTask.out_stream)
    
            estT = outputX.size/writingRate
            writer.write_many_sample(outputData)
            
            writeTask.start()
            reader.read_many_sample(inputData, timeout = estT+5)   
            
            writeTask.wait_until_done(timeout = estT+5)
            readTask.wait_until_done(timeout = estT+5)
            print("Done with data")
    
    #----------------------------Creating the Image----------------------------
    print("Creating the image")
    #Creating the array for the image
    imArray = inputData[1::].reshape((totalyPixels, totalxPixels)) #Not taking into account the first sample
    
    #Plotting the image
    plt.imshow(imArray, cmap = plt.cm.gray)
    plt.show()
    
def triangle(ai_chan, ao_chan_x, ao_chan_y, sRate, imAngle, outputX, outputY, xPixels, yPixels, exPixels):
    print("Measurement started")
    writingRate = sRate
    readingRate = writingRate
    
    radAngle = math.pi/180*imAngle
    exPixelsX = int(math.cos(radAngle)*exPixels) #Amount of excess pixels in X
    exPixelsY = int(math.sin(radAngle)*exPixels) #Amount of excess pixels in Y
    
    totalxPixels = 2*exPixelsX+xPixels #2 times excess pixels because we overshoot on two sides
    totalyPixels = 2*exPixelsY+yPixels
    
    inputData = np.zeros(outputX.size+1)#Need the extra one because of the sample shift due to the trigger
    outputData = np.array([outputX, outputY])
    outputChannels = ao_chan_x + ", " + ao_chan_y
    with nidaqmx.Task() as writeTask, nidaqmx.Task() as readTask:  
            writeTask.ao_channels.add_ao_voltage_chan(outputChannels)
            readTask.ai_channels.add_ai_voltage_chan(ai_chan)
            
            #In the USB6001 DAQ there seems to be no SampleClock, therefore we cannot sync the signals without an external trigger/clock
            #sample_clock = '/Dev2/ai/SampleClock'
            
            writeTask.timing.cfg_samp_clk_timing(rate = writingRate,
                                                  sample_mode = nidaqmx.constants.AcquisitionType.FINITE,
                                                  samps_per_chan = outputX.size)
            readTask.timing.cfg_samp_clk_timing(rate = readingRate,
                                                sample_mode = nidaqmx.constants.AcquisitionType.FINITE,
                                                samps_per_chan = inputData.size)              
            writeTask.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source = '/Dev2/ai/StartTrigger') #Setting the trigger on the analog input
            
            reader = AnalogSingleChannelReader(readTask.in_stream)
            writer = AnalogMultiChannelWriter(writeTask.out_stream)
            
            estT = outputX.size/writingRate
            writer.write_many_sample(outputData)
            writeTask.start()
            reader.read_many_sample(inputData, timeout = estT+5)   
            
            writeTask.wait_until_done(timeout = estT+5)
            readTask.wait_until_done(timeout = estT+5)
    
    #----------------------------Creating the Image----------------------------
    #Creating the array for the image
    imArray = np.zeros((totalyPixels, totalxPixels)) #Not taking into account the first sample
    
    #Resolving the sample shift
    inputData = inputData[1::]
    
    #Now we have to loop over the positions because the reshape function does not work
    forward = True
    xPix = exPixelsX    #Defines the x position 
    yPix = 0            #Defines the y position
    
    #Doing the first iteration in case we start at x=0
    imArray[yPix, xPix] = inputData[0]
    xPix += 1
    
    #Going through all the other values
    i = 1
    while i < inputData.size:
        imArray[yPix, xPix] = inputData[i]
        
        #Moving one y position up when reaching one end of the image
        if xPix == (totalxPixels-1): 
            xPix = totalxPixels-exPixelsX-1
            yPix += 1
            #Going to the next value manually
            i += 1
            if i == inputData.size: break #Making sure i does not exceed the input data array
            imArray[yPix, xPix] = inputData[i]
            forward = not forward
        elif xPix == 0:
            xPix = exPixelsX
            yPix += 1
            #Going to the next value manually
            i += 1
            if i == inputData.size: break #Making sure i does not exceed the input data array
            imArray[yPix, xPix] = inputData[i]
            forward = not forward
   
        if forward == True:
            xPix += 1 #Moving one up if moving forward over the x pixels
        else:
            xPix -= 1 #Moving one down if moving backward over the x pixels
            
        i += 1 #Going to the next value of the input data
                
    #Plotting the image
    plt.imshow(imArray, cmap = plt.cm.gray)
    plt.show()
      
def calibrate(sRate, aiChan, aoChan, xValues):
    writingRate = sRate
    readingRate = writingRate
    outputData = xValues
    inputData = np.zeros(outputData.size+1)
        
    with nidaqmx.Task() as writeTask, nidaqmx.Task() as readTask:  
        writeTask.ao_channels.add_ao_voltage_chan(aoChan)
        readTask.ai_channels.add_ai_voltage_chan(aiChan)
        
        #In the USB6001 DAQ there seems to be no SampleClock, therefore we cannot sync the signals without an external trigger/clock
        #sample_clock = '/Dev2/ai/SampleClock'
        
        writeTask.timing.cfg_samp_clk_timing(rate = writingRate,
                        sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS,
                        samps_per_chan = outputData.size)
        readTask.timing.cfg_samp_clk_timing(rate = readingRate,
                        sample_mode = nidaqmx.constants.AcquisitionType.FINITE,
                        samps_per_chan = inputData.size)              
        writeTask.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source = '/Dev2/ai/StartTrigger') #Setting the trigger on the analog input
        #readTask.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source = '/Dev2/ao/StartTrigger')
        
        reader = AnalogSingleChannelReader(readTask.in_stream)
        writer = AnalogSingleChannelWriter(writeTask.out_stream)
        
        writer.write_many_sample(outputData)
        writeTask.start()
        reader.read_many_sample(inputData, timeout = outputData.size/readingRate+4)
        
    #The ai/StartTrigger 'takes' one sample from writing so the actual writing starts one sample later, therefore the inputData starts one sample later
    inputData = inputData[1::]
    
    return outputData, inputData
    
    
    
    
    