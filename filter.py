# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 12:55:22 2018

@author: lhuismans
"""
import visa

class ELL9Filter:
    """
    This class initializes a ELL9K filter stage, to be able to control the
    device. 
    """
    def __init__(self, address):
        self.address = address
        self.rm = visa.ResourceManager()
        
    def Home(self):
        """
        Moves the stage to its home position.
        """
        with self.rm.open_resource(self.address) as motor: #You can find the COM# using ELLO
            motor.write('0ho0') #Moves the stage of channel 0 to home
            
    def Forward(self):
        """
        Moves the stage one position forward.
        """
        with self.rm.open_resource(self.address) as motor:
            motor.write('0fw') #Moves the stage of channel 0 one position forward
            motor.close()
            
    def Backward(self):
        """
        Moves the stage one position backward.
        """
        with self.rm.open_resource(self.address) as motor:
            motor.write('0bw') #Moves the stage of channel 0 one position backward
    
    
    def MoveToPosition(self, position):
        """
        Moves the stage to an absolute position.
        The positions are labeled 0, 1, 2 and 3, each linked to a filter.
        """
        assert position < 4, "Choose a position 0, 1, 2 or 3"
        
        if position == 0:
            with self.rm.open_resource(self.address) as motor:
                motor.write('0ma00000000')
        elif position == 1:
            with self.rm.open_resource(self.address) as motor:
                motor.write("0ma0000001F")
        elif position == 2:
            with self.rm.open_resource(self.address) as motor:
                motor.write("0ma0000003E")
        elif position == 3:
            with self.rm.open_resource(self.address) as motor:
                motor.write("0ma0000005D")
    
    def GetPosition(self):
        """
        Retreives the current position of the filter and prints the value.
        """
        with self.rm.open_resource(self.adress) as motor:
            print(motor.query('0gp'))
            
    def Close(self):
        """
        Closes the resource.
        """
        self.rm.close()
