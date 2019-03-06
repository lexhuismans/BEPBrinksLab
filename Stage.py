# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 12:02:08 2018

@author: lhuismans
"""

import visa
import time 

class LudlStage:
    """
    This class is for controlling the stage using the MAC5000 from ludl. So far
    this only works using a serial to usb connection and having the converting 
    piece provided by Teun and Greta in between. 
    """
    def __init__(self, adress):
        """
        Initializing the stage, Ludl recommends that the user refrain from use 
        of the joystick or RS-232 serial communication until completion of 
        interface initialization routine which is approximately 5 seconds after 
        power up. 
        The COM port has to be specified as a string: "COM#".
        """
        self.adress = adress
        self.rm = visa.ResourceManager()
        time.sleep(5) #Making sure the device is fully powered up. 
        
    def GetPos(self):
        """
        Gets the current position of the stage. A positive reply is of the from:
            :A X Y
        A negative reply is of the form:
            :N -code
        See the documentation to find which code corresponds to which error. 
        """
        with self.rm.open_resource(self.adress) as stage:
            stage.write_termination = "\r"
            print(stage.query('Where X Y')) 
            
    def MoveAbs(self, X, Y):
        """
        Moves the motor to an absolute position defined by X and Y.
        A positive reply is sent back when the command is received correctly.
        The reply does not mean the movement is finished.
        """
        command = 'Move X = %d Y = %d' % (X, Y)
        with self.rm.open_resource(self.adress) as stage:
            stage.write_termination = "\r"
            print(stage.query(command))
            
    
    def MoveVec(self, X, Y):
        """
        Moves the motor to an absolute position but as opposed to moveAbs it 
        adjusts the speeds to plot a straight line.
        """
        command = "Vmove X = %d Y = %d" % (X, Y)
        with self.rm.open_resource(self.adress) as stage:
            stage.write_termination = "\r"
            print(stage.query(command))
            
    def MoveRel(self, xRel, yRel):
        """
        Moves the motor to a relative position.
        Set position to None if this axis is not used. 
        """
        if xRel == None:
            command = "Movrel Y = %d" % yRel
            with self.rm.open_resource(self.adress) as stage:
                stage.write_termination = "\r"
                print(stage.query(command))
        elif yRel == None:
            command = "Movrel X = %d" % xRel
            with self.rm.open_resource(self.adress) as stage:
                stage.write_termination = "\r"
                print(stage.query(command))
        else:
            command = "Movrel X = %d Y = %d" % (xRel, yRel)
            with self.rm.open_resource(self.adress) as stage:
                stage.write_termination = "\r"
                print(stage.query(command))
    
    def Home(self):
        """
        Moves to motors toward the end limit switch. This is reached by running
        the motor to a large negative position. 
        If there are no errors a positive reply is sent back. 
        """
        with self.rm.open_resource(self.adress) as stage:
            stage.write_termination = "\r"
            print(stage.query("Home"))
                
    def SetZero(self):
        """
        Sets the current position as zero position.
        """
        with self.rm.open_resource(self.adress) as stage:
            stage.write_termination = "\r"
            print(stage.query("Here X = 0 Y = 0"))
    
    def Joystick(self, on = True):
        """
        Enable or disable the joystick.
        """
        switch = "+"
        if on == False:
            switch = "-"
        
        command = "Joystick X%s Y%s" % (switch, switch)
        with self.rm.open_resource(self.adress) as stage:
            stage.write_termination = "\r"
            print(stage.query(command))
                
    def Status(self):
        """
        Checks if the motors are still running. 
        Reply:
            "N" if all motors are stopped. 
            "B" if one or more motors are is still running.
        """
        with self.rm.open_resource(self.adress) as stage:
            stage.write_termination = "\r"
            print(stage.query("Status"))
                
    def Reset(self):
        """
        Resets the whole controller and restart from a power up condition. No
        reply is provided.
        """
        with self.rm.open_resource(self.adress) as stage:
            stage.write_termination = "\r"
            print(stage.write('REMRES')) 
            time.sleep(5) #Sleep for 5 seconds to initialize.
