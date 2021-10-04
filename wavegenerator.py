from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import math

from constants import HardwareConstants

def inertial(vIn, vOut, a, startVolt):
    """
    Computes the values for acceleration or deceleration to a specific speed. 
    !Not including the startVolt!
    """
    a = abs(a)
    if vIn > vOut:
        a = -a
    
    inertialPart = np.array([])
    timespan = abs(math.floor((vOut-vIn)/a))
    t = np.arange(timespan)
    inertialPart = 0.5*a*t[1::]**2+vIn*t[1::]+startVolt #Making the array with the voltage values, we are not taking into acount the first value as this is the value of the previous sample
    return inertialPart

def changeDirection(v, a, speed, startVolt, endVolt):
    """
    Takes the fastest route from specified starting point startVolt 
    to an end point endVolt. The incoming and outgoing speed should be the same
    as the algorithm makes use of symmetry. 
    All units are with pixels, volts and seconds. 
    """
    wave = np.array([])
    
    #Setting speed to right direction
    speed = abs(speed)
    if endVolt < startVolt:
        speed = -speed
    
    #Inertial 1
    inertialPart = inertial(v, speed, a, startVolt)
    
    #Linear
    inertialPart2 = inertial(-v, -speed, a, endVolt)
    inertialPart2 = np.flip(inertialPart2, 0)
    
    if inertialPart[-1] < inertialPart2[0]:
        #Specifying the threshold to be halfway (due to symmetry)
        threshold = (startVolt+endVolt)/2
        
        #Taking values above/below threshold
        inertialPart = inertialPart[inertialPart>threshold]
        inertialPart2 = inertialPart2[inertialPart2<threshold]
        
        #Removing sample if end point of first inertialpart is to close to start point of second inertialpart
        if inertialPart2[0]-inertialPart[-1] > inertialPart2[1]-inertialPart[0]:
            inertialPart = inertialPart[:-1]
            
        #Adding to total array
        wave = np.append(wave, inertialPart) #Adding the array to the total path
        wave = np.append(wave, inertialPart2)
        return wave
    else:
        wave = np.append(wave, inertialPart)
        endVoltLinear = inertialPart2[0]
        timespanRampDown = math.ceil(abs((endVoltLinear-wave[-1])/speed))#Computing the time span the rampdown should take.
                                                                         #We ceil the timespan so we do not exceed the maximum galvo speed.       
        
        linearPart = np.linspace(wave[-1], endVoltLinear, timespanRampDown)
        
        wave = np.append(wave, linearPart[1::]) #First value of linear part is the same as last value of wave, therefore we do not take it into account
        
        #Inertial 2
        wave = np.append(wave, inertialPart2)
        
        return wave
    
def xValuesSingleSawtooth(sampleRate = 1000, voltXMin = 0, voltXMax = 5, xPixels = 1024, sawtooth = True):
    """
    This function generates the xValues for !!!ONE PERIOD!!! of the sawtooth/triangle wave.
    
    First part: linearly moving up
    Second part: accelerating to the rampdown speed (maximum galvo speed for sawtooth)
    Third part: linearly moving down
    Fourth part: accelerating to rampup speed
    """
    #---------Defining standard variables------------
    constants = HardwareConstants()
    speedGalvo = constants.maxGalvoSpeed #Volt/s
    aGalvo = constants.maxGalvoAccel #Acceleration galvo in volt/s^2
    aGalvoPix = aGalvo/(sampleRate**2) #Acceleration galvo in volt/pixel^2
    xArray = np.array([]) #Array for x voltages
    rampUpSpeed = (voltXMax-voltXMin)/xPixels #Ramp up speed in volt/pixel
    rampDownSpeed = -speedGalvo/sampleRate #Ramp down speed in volt/pixel (Default sawtooth)
    
    assert abs(rampUpSpeed) < abs(rampDownSpeed), "Your reading speed exceeds the maximum speed of the galvo, please use a lower rate or add more pixels."
    
    #-----------Checking for triangle wave-----------
    if sawtooth == False:
        rampDownSpeed = -rampUpSpeed 
    
    #---------------------------------------------------------------------------
    #---------------------------x pixel wave function---------------------------
    #---------------------------------------------------------------------------
    
    #-----------Defining the ramp up (x)------------
    rampUp = np.linspace(voltXMin, voltXMax, xPixels)
    xArray = np.append(xArray, rampUp) #Adding the voltage values for the ramp up
    
    rampDown = changeDirection(rampUpSpeed, aGalvoPix, rampDownSpeed, xArray[-1], voltXMin)
    xArray = np.append(xArray, rampDown)
    
    return xArray

def yValuesFullSawtooth(sampleRate, voltYMin, voltYMax, xPixels, yPixels, lineSize):
    """
    This functiong generates the !!!FULL!!! yArray (stepfunction) for the sawtooth or triangle wave.
    
    lineSize defines the length of each step.
    For the trianglewave this is ~half the wavelength and for the sawtooth it is 
    the full wavelength. 
    """
    constants = HardwareConstants()
    speedGalvo = constants.maxGalvoSpeed #Volt/s
    speedGalvo = speedGalvo/sampleRate #Speed in volt/pixels
    aGalvo = constants.maxGalvoAccel #Acceleration galvo in volt/s^2
    aGalvoPix = aGalvo/(sampleRate**2) #Acceleration galvo in volt/pixel^2
    
    stepSize = (voltYMax-voltYMin)/yPixels
    
    #Creating the stepfunction
    extendedYArray = np.ones(xPixels)*voltYMin  #The first line is created manually as this is shorter
                                                #The step is starting at the beginning of the intertial part
    for i in np.arange(yPixels-1)+1:
        extendedYArray = np.append(extendedYArray, np.ones(lineSize)*i*stepSize+voltYMin)
    
    #Swing back
    swingBack = changeDirection(0, aGalvoPix, speedGalvo, extendedYArray[-1], voltYMin)
    extendedYArray = np.append(extendedYArray, swingBack)
    #extraPixels = (lineSize*yPixels-extendedYArray.size) #Some extra pixels are needed to make x and y the same size 
    #extendedYArray = np.append(extendedYArray, np.ones(extraPixels)*voltYMin)
    
    return extendedYArray

def rotateXandY(xArray, yArray, voltXMin, voltXMax, voltYMin, voltYMax, imAngle):
    """
    Rotates x and corresponding y array for galvos around its center point.
    """
    radAngle = math.pi/180*imAngle #Converting degrees to radians
    
    #Shifting to the center
    xArray = xArray-((voltXMax-voltXMin)/2+voltXMin)
    yArray = yArray-((voltYMax-voltYMin)/2+voltYMin)
    
    #Converting the x and y arrays
    rotatedXArray = xArray*math.cos(radAngle)-yArray*math.sin(radAngle)
    rotatedYArray = xArray*math.sin(radAngle)+yArray*math.cos(radAngle)
    
    #Shifting it back
    finalXArray = rotatedXArray+((voltXMax-voltXMin)/2+voltXMin)
    finalYArray = rotatedYArray+((voltYMax-voltYMin)/2+voltYMin)
    
    return finalXArray, finalYArray

def repeatWave(wave, repeats):
    """
    Repeats the wave a set number of times and returns a new repeated wave.
    """
    extendedWave = np.array([])
    for i in range(repeats):
        extendedWave = np.append(extendedWave, wave)
    return extendedWave

def waveRecPic(sampleRate = 4000, imAngle = 0, voltXMin = 0, voltXMax = 5, 
                 voltYMin = 0, voltYMax = 5, xPixels = 1024, yPixels = 512, 
                 sawtooth = True):
    """
    Generates a the x and y values for making rectangular picture with a scanning laser.
    imAngle is the image angle in degrees.
    sawtooth is True for generating a sawtooth.
    """
    xArray = xValuesSingleSawtooth(sampleRate, voltXMin, voltXMax, xPixels, sawtooth)
    lineSize = xArray.size
    if sawtooth == False:
        lineSize = round(lineSize/2) #The size that each line in the y values should have
    finalY = yValuesFullSawtooth(sampleRate, voltYMin, voltYMax, xPixels, yPixels, lineSize)
    
    #Looping it to get the desired amount of periods for x
    if sawtooth == True:
        finalX = repeatWave(xArray, yPixels)
    else:
        repeats = int(math.ceil(yPixels/2))
        finalX = repeatWave(xArray, repeats)
        
        #Checking if we should remove the last ramp down    
        if yPixels%2 == 1: 
            finalY = finalX[0:-lineSize]
    #Adding extra pixels if needed
    if finalX.size>finalY.size:
        extraPixels = (finalX.size-finalY.size) #Some extra pixels are needed to make x and y the same size 
        finalY = np.append(finalY, np.ones(extraPixels)*voltYMin)
    elif finalX.size<finalY.size:
        extraPixels = (finalY.size-finalX.size) #Some extra pixels are needed to make x and y the same size 
        finalX = np.append(finalX, np.ones(extraPixels)*voltXMin)
    #Rotating
    if imAngle > 0:
        finalX, finalY = rotateXandY(finalX, finalY, voltXMin, voltXMax, voltYMin,
                                     voltYMax, imAngle)
    return finalX, finalY

def blockWave(sampleRate, frequency, voltMin, voltMax, dutycycle):
    """
    Generates a one period blockwave. 
    sampleRate      samplerate set on the DAQ (int)
    frequency       frequency you want for the block wave (int)
    voltMin         minimum value of the blockwave (float)
    voltMax         maximum value of the blockwave (float)
    dutycycle       duty cycle of the wave (wavelength at voltMax) (float)
    """
    wavelength = int(sampleRate/frequency) #Wavelength in number of samples
    #The high values 
    high = np.ones(math.ceil(wavelength*dutycycle))*voltMax
    #Low values
    low = np.ones(math.floor(wavelength*(1-dutycycle)))*voltMin
    #Adding them
    return np.append(high, low)
    
def testSawtooth():
    """
    For generating a picture of the wavefunctions.
    This was made to check if the waveforms were sensible, before integrating 
    them into the program. 
    """
    sRate = 2000000
    imAngle = 0
    VxMax = 3
    VxMin = -3
    VyMax = 3
    VyMin = -3
    xPixels = 2048
    yPixels = 2
    sawtooth = True
    
    xValues, yValues = waveRecPic(sRate, imAngle, VxMin, VxMax, VyMin, VyMax, 
                                                    xPixels, yPixels, sawtooth)
     
    plt.axhline(y=-3, color='k', label = '_nolegend_')
    plt.axhline(y=3, color='k', label = '_nolegend_')                                             
    plt.plot(np.arange(xValues.size), xValues)
    plt.plot(np.arange(yValues.size), yValues, ls = 'dashed')
    plt.xlabel('sample number')
    plt.ylabel('Volt')
    plt.legend(['x-values', 'y-values'], loc='best')
    plt.show()
    