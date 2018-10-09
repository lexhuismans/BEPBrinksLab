from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import math

def previewSawtooth(sRate = 10000, imAngle = 45., VxMax = 5., VyMax = 10., VyMin = 0., 
                                        VxMin = 0., xPixels = 24, yPixels = 5, 
                                        sawtooth = False):
    """ Notes:
     Might want to implement warning for speeds greater than galvo speed.
     Speed, acceleration and pixels have to be realistic for smooth curve
     !!!Fix triangle wave!!! lineSizeTriangle 1 to large!!!
    """
    #---------Defining standard variables------------
    speedGalvo = 100.0 #Volt/s
    aGalvo = 1000.09765625 #Acceleration galvo in volt/s^2
    aGalvoPix = aGalvo/sRate #Acceleration galvo in volt/pixel^2
    xArray = np.array([]) #Array for x voltages
    rampUpSpeed = (VxMax-VxMin)/xPixels #Ramp up speed in volt/pixel
    rampDownSpeed = -speedGalvo/sRate #Ramp down speed in volt/pixel (Default sawtooth)
    
    #-----------Checking for triangle wave-----------
    if sawtooth == False:
        rampDownSpeed = -rampUpSpeed 
    
    #---------------------------------------------------------------------------
    #---------------------------x pixel wave function---------------------------
    #---------------------------------------------------------------------------
    
    #-----------Defining the ramp up (x)------------
    rampUp = np.linspace(VxMin, VxMax, xPixels)
    xArray = np.append(xArray, rampUp) #Adding the voltage values for the ramp up
    
    #-----------Defining the inertial part-------------
    inertialPart = np.array([]) #Making a temporary array for storing the voltage values of the inertial part
    vIn = rampUpSpeed #Speed of "incoming" ramp (volt/pixel)
    vOut = rampDownSpeed #Speed of "outgoing" ramp (volt/pixel)
    a = -aGalvoPix #Acceleration in volt/pixel^2
    timespanInertial = abs(math.floor((rampDownSpeed-rampUpSpeed)/a)) #Calculating the timespan needed
    t = np.arange(timespanInertial)
    inertialPart = 0.5*a*t[1::]**2+vIn*t[1::]+xArray[-1] #Making the array with the voltage values, we are not taking into acount the first value as this is the value of the previous sample
    xArray = np.append(xArray, inertialPart) #Adding the array to the total path
    
    lineSizeTriangle = xArray.size #Defining the linesize for the yArray in case of a triangle wave
    #----------Defining the ramp down----------------
    a = aGalvoPix
    startVoltage = xArray[-1]+rampDownSpeed
    #We calculate the endvoltage by using the timespan for the intertial part and 
    #the starting voltage
    endVoltage = 0.5*a*timespanInertial**2-rampUpSpeed*timespanInertial+VxMin
    
    if sawtooth == True:
        timespanRampDown = abs(math.floor((endVoltage-startVoltage)/rampDownSpeed))
    else:
        timespanRampDown = rampUp.size #If it is a triangle wave the ramp down part should be as big as the ramp up part
        
    rampDown = np.linspace(startVoltage, endVoltage, int(timespanRampDown)) #Specifying the linear path
    xArray = np.append(xArray, rampDown) #Adding the array to the total path
    
    #----------Defining the second inertial part-------------
    inertialPart2 = np.array([])
    vIn = rampDownSpeed #Speed of "incoming" ramp (volt/pixel)
    vOut = rampUpSpeed #Speed of "outgoing" ramp (volt/pixel)
    a = aGalvoPix #Acceleration in volt/pixel^2
    inertialPart2 = 0.5*a*t[1::]**2+vIn*t[1::]+xArray[-1] #We can use the same time units as the first inertial part but not including the last value, as this is part of the next iteration
    xArray = np.append(xArray, inertialPart2)     
    
    #---------------------------------------------------------------------------
    #---------------------------y pixel step function---------------------------
    #---------------------------------------------------------------------------
    
    stepSize = (VyMax-VyMin)/yPixels
    #Different linesizes for triangle/sawtooth
    if sawtooth == True:
        lineSize = xArray.size #The size of 1 line, doing the step at the last sample to reduce potential bleaching
    else:
        lineSize = lineSizeTriangle
       
    extendedyArray = np.array([])
    for i in range(yPixels):
        extendedyArray = np.append(extendedyArray, np.ones(lineSize)*i*stepSize+VyMin)
    
    return xArray, extendedyArray, lineSizeTriangle

def genSawtooth(sRate = 10000, imAngle = 10., VxMax = 5., VyMax = 10., VyMin = 0., 
                                        VxMin = 0., xPixels = 24, yPixels = 12, 
                                        sawtooth = False):
    xArray, extendedyArray, lineSizeTriangle = previewSawtooth(sRate, imAngle, 
                                        VxMax, VyMax, VyMin, VxMin, xPixels, 
                                        yPixels, sawtooth)
    #Looping it to get the desired amount of periods for x
    extendedxArray = np.array([])
    if sawtooth == True:
        for i in range(yPixels):
            extendedxArray = np.append(extendedxArray, xArray)
    else:
        for i in range(int(math.ceil(yPixels/2))):
            extendedxArray = np.append(extendedxArray, xArray)
        #Checking if we should remove the last ramp down    
        if yPixels%2 == 1: 
            extendedxArray = extendedxArray[0:-lineSizeTriangle]
    
    
    #---------------------------------------------------------------------------
    #---------------------------Rotation----------------------------------------
    #---------------------------------------------------------------------------
    radAngle = math.pi/180*imAngle #Converting degrees to radians
    
    #Shifting to the center
    extendedxArray = extendedxArray-((VxMax-VxMin)/2+VxMin)
    extendedyArray = extendedyArray-((VyMax-VyMin)/2+VyMin)
    
    #Converting the x and y arrays
    finalxArray = extendedxArray*math.cos(radAngle)-extendedyArray*math.sin(radAngle)
    finalyArray = extendedxArray*math.sin(radAngle)+extendedyArray*math.cos(radAngle)
    
    #Shifting it back
    #finalxArray = finalxArray+((VxMax-VxMin)/2+VxMin)
    finalyArray = finalyArray+((VyMax-VyMin)/2+VyMin)
    finalxArray = finalxArray+((VxMax-VxMin)/2+VxMin)
    
    plt.plot(np.arange(finalxArray.size), finalxArray)
    plt.plot(np.arange(finalyArray.size), finalyArray)
    plt.show()
    
genSawtooth()
""" backup:
     
"""