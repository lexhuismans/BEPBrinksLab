from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import math

def previewSawtooth(sRate = 10000, imAngle = 0, VxMax = 5, VyMax = 10, VyMin = 0, 
                                        VxMin = 0, xPixels = 1024, yPixels = 512, 
                                        sawtooth = True):
    """ Notes:
     This function calculates the points for 1 period for the sawtooth/triangle.
     This is used in the preview inside the GUI. At first the constants are defined,
     e.g. the galvomirror speed/acceleration. After this the wave gets generated
     in 4 parts for the x values.
     First part: linearly moving up
     Second part: accelerating to the rampdown speed (maximum galvo speed for sawtooth)
     Third part: linearly moving down
     Fourth part: accelerating to rampup speed 
     Finally the step function for the y values gets computed. 
    """
    #---------Defining standard variables------------
    speedGalvo = 2000.0 #Volt/s, actual value probably 20000
    aGalvo = 1000.0 #Acceleration galvo in volt/s^2, actual value around 1,54*10^8
    aGalvoPix = aGalvo/sRate #Acceleration galvo in volt/pixel^2
    xArray = np.array([]) #Array for x voltages
    rampUpSpeed = (VxMax-VxMin)/xPixels #Ramp up speed in volt/pixel
    rampDownSpeed = -speedGalvo/sRate #Ramp down speed in volt/pixel (Default sawtooth)

    assert abs(rampUpSpeed) < abs(rampDownSpeed), "Your reading speed exceeds the maximum speed of the galvo, please use a lower rate or add more pixels."
    
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
    timespanInertial = abs(math.floor((vOut-vIn)/a)) #Calculating the timespan needed
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
        timespanRampDown = abs(math.ceil((endVoltage-startVoltage)/rampDownSpeed))
        rampDownSpeed = (endVoltage-startVoltage)/timespanRampDown #Above line changed the rampDownSpeed so we have to recalculate
    else:
        timespanRampDown = rampUp.size #If it is a triangle wave the ramp down part should be as big as the ramp up part
        
    rampDown = np.linspace(startVoltage, endVoltage, timespanRampDown) #Specifying the linear path
    xArray = np.append(xArray, rampDown) #Adding the array to the total path
    
    #----------Defining the second inertial part-------------
    inertialPart2 = np.array([])
    vIn = rampDownSpeed #Speed of "incoming" ramp (volt/pixel)
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
    
    #Creating the 'stairs'
    extendedyArray = np.array([])
    for i in range(yPixels):
        extendedyArray = np.append(extendedyArray, np.ones(lineSize)*i*stepSize+VyMin)
    
    #Creating the swing back (for multiple frames)
    """
    inertialPart = np.array([]) #Making a temporary array for storing the voltage values of the inertial part
    vIn = rampUpSpeed #Speed of "incoming" ramp (volt/pixel)
    vOut = rampDownSpeed #Speed of "outgoing" ramp (volt/pixel)
    a = -aGalvoPix #Acceleration in volt/pixel^2
    timespanInertial = abs(math.floor((vOut-vIn)/a)) #Calculating the timespan needed
    t = np.arange(timespanInertial)
    inertialPart = 0.5*a*t[1::]**2+vIn*t[1::]+xArray[-1] #Making the array with the voltage values, we are not taking into acount the first value as this is the value of the previous sample
    xArray = np.append(xArray, inertialPart) #Adding the array to the total path
    """
    
    return xArray, extendedyArray, lineSizeTriangle

def genSawtooth(sRate = 4000, imAngle = 0, VxMax = 5, VyMax = 5, VyMin = 0, 
                                        VxMin = 0, xPixels = 1024, yPixels = 512, 
                                        sawtooth = True):
    """
    The full function gets computed using the preview of the function previewSawtooth()
    This is done by extending the x array. 
    Note that for the sawtooth the last rampdown is still taken into account.
    For the triangle wave the last rampdown is removed in case the ammount of 
    y pixels is odd. 
    """
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
    finalyArray = finalyArray+((VyMax-VyMin)/2+VyMin)
    finalxArray = finalxArray+((VxMax-VxMin)/2+VxMin)
    
    return finalxArray, finalyArray
    
def testSawtooth():
    sRate = 1000000
    imAngle = 0
    VxMax = 7.5
    VxMin = 0.
    VyMax = 10
    VyMin = 2
    xPixels = 1024
    yPixels = 13
    sawtooth = True
    
    xValues, yValues = genSawtooth(sRate, imAngle, VxMax, VyMax, VyMin, VxMin, 
                                                    xPixels, yPixels, sawtooth)
                                                    
    plt.plot(np.arange(xValues.size), xValues)
    plt.plot(np.arange(yValues.size), yValues)
    plt.show()

""" backup:
     
"""