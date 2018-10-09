import tkinter as tk
import nidaqmx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import wavegenerator
from matplotlib import style
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import measure

style.use("ggplot")

class GUI:
    def __init__ (self, master):
        self.master = master #Defining the root window
        
        #Creating the containers
        frame = tk.Frame(master, borderwidth=2, relief="groove")
        systemFrame = tk.Frame(master, borderwidth=2, relief="groove")
        
        #Defining the labels
        fontName = 'Helvetica 10'
        self.waveform = tk.StringVar()
        
        self.sRateLabel = tk.Label(frame, text="Sample rate", font = fontName)
        self.imAngleLabel = tk.Label(frame, text="Image angle", font = fontName)
        self.VxMaxLabel = tk.Label(frame, text="Max voltage x", font = fontName)
        self.VxMinLabel = tk.Label(frame, text="Min voltage x", font = fontName)
        self.VyMaxLabel = tk.Label(frame, text="Max voltage y", font = fontName)
        self.VyMinLabel = tk.Label(frame, text="Min voltage y", font = fontName)
        self.xPixelsLabel = tk.Label(frame, text="Pixels in x", font = fontName)
        self.yPixelsLabel = tk.Label(frame, text="Pixels in y", font = fontName)
        
        self.sawtoothRadio = tk.Radiobutton(frame, text='Sawtooth', 
                                                        variable=self.waveform, value="sawtooth")
        self.triangleRadio = tk.Radiobutton(frame, text='Triangle', 
                                                        variable=self.waveform, value="triangle")
        self.triangleRadio.select()
        self.calibrateButton = tk.Button(frame, text="Calibrate (x)", font=fontName, command=self.calibrate)
        self.startButton = tk.Button(frame, text="Start Measurement", font=fontName, command=self.measure)
        
        #For choosing which device
        self.devVar = tk.StringVar()
        
        system = nidaqmx.system.System.local()
        devices = np.array([])
        for device in system.devices: #Looping over all the devices and adding them to an array
            devices = np.append(devices, device.name)
            
        self.devMenu = tk.OptionMenu(systemFrame, self.devVar, *devices) #Adding all the devices from the array to the menu
        self.devVar.set(system.devices[1].name) #Setting the default to the # device
        
        #For the analog input and ouput channels
        #For the analog input
        device = nidaqmx.system.device.Device(self.devVar.get())
        self.aiVar = tk.StringVar()
        self.aoVarX = tk.StringVar()
        self.aoVarY = tk.StringVar()
        
        aiDevice = np.array([])
        for ai in device.ai_physical_chans: #Looping over all the input channels and adding them to an array
            aiDevice = np.append(aiDevice, ai.name)
        self.aiMenu = tk.OptionMenu(systemFrame, self.aiVar, *aiDevice)  #Adding all the ai from the array to the menu
        self.aiVar.set(device.ai_physical_chans[0].name) #Setting the default
        
        #For the analog output
        aoDevice = np.array([])
        for ao in device.ao_physical_chans:
            aoDevice = np.append(aoDevice, ao.name)
            
        self.aoMenuX = tk.OptionMenu(systemFrame, self.aoVarX, *aoDevice)
        self.aoVarX.set(device.ao_physical_chans[0].name)
        
        self.aoMenuY = tk.OptionMenu(systemFrame, self.aoVarY, *aoDevice)
        self.aoVarY.set(device.ao_physical_chans[1].name)
        
        #Structuring the system menu
        self.devMenuLabel = tk.Label(systemFrame, text = "Device", font = fontName).grid(row = 0, column = 0)
        self.aiMenuLabel = tk.Label(systemFrame, text = "ai channel", font = fontName).grid(row = 0, column = 1)
        self.aoMenuXLabel = tk.Label(systemFrame, text = "ao channel x", font = fontName).grid(row = 0, column = 2)
        self.aoMenuYLabel = tk.Label(systemFrame, text = "ao channel y", font = fontName).grid(row = 0, column = 3)
        
        self.devMenu.grid(row=1, column=0) 
        self.aiMenu.grid(row=1, column=1)
        self.aoMenuX.grid(row=1, column=2)
        self.aoMenuY.grid(row=1, column=3)
         
        #Defining the entries
        self.sRateEntry = tk.Entry(frame)
        self.sRateEntry.insert(0, 10000)
        self.imAngleEntry = tk.Entry(frame)
        self.imAngleEntry.insert(0,0)
        self.VxMaxEntry = tk.Entry(frame)
        self.VxMaxEntry.insert(0,5)
        self.VxMinEntry = tk.Entry(frame)
        self.VxMinEntry.insert(0,0)
        self.VyMaxEntry = tk.Entry(frame)
        self.VyMaxEntry.insert(0,5)
        self.VyMinEntry = tk.Entry(frame)
        self.VyMinEntry.insert(0,0) 
        self.xPixelEntry = tk.Entry(frame)
        self.xPixelEntry.insert(0,1024)
        self.yPixelEntry = tk.Entry(frame)
        self.yPixelEntry.insert(0, 512)
        
        #Structuring the GUI
        self.sRateLabel.grid(row=1, column=0, sticky='w')
        self.imAngleLabel.grid(row=2, column=0, sticky='w')
        self.VxMinLabel.grid(row=3, column=0, sticky='w')
        self.VxMaxLabel.grid(row=4, column=0, sticky='w')
        self.VyMinLabel.grid(row=5, column=0, sticky='w')
        self.VyMaxLabel.grid(row=6, column=0, sticky='w')
        self.xPixelsLabel.grid(row=7, column=0, sticky='w')
        self.yPixelsLabel.grid(row=8, column=0, sticky='w')
        
        self.sawtoothRadio.grid(row=9, column=0)
        self.triangleRadio.grid(row=9, column=1)
        
        self.sRateEntry.grid(row=1, column=1, sticky='w')
        self.imAngleEntry.grid(row=2, column=1, sticky='w')
        self.VxMinEntry.grid(row=3, column=1, sticky='w')
        self.VxMaxEntry.grid(row=4, column=1, sticky='w')
        self.VyMinEntry.grid(row=5, column=1, sticky='w')
        self.VyMaxEntry.grid(row=6, column=1, sticky='w')
        self.xPixelEntry.grid(row=7, column=1, sticky='w')
        self.yPixelEntry.grid(row=8, column=1, sticky='w')
        
        self.calibrateButton.grid(row=10, column=1)
        self.startButton.grid(row=10, column=0)
        
        frame.grid(row=1, column = 0)
        systemFrame.grid(row = 0, column = 0)
        #--------For the live plotting--------------
        right_frame = tk.Frame(self.master)
        fig = Figure(figsize=(5,5), dpi=100) #We need a figure to put the plot on the canvas
        self.ax = fig.add_subplot(111) #111 means there is only 1 graph
        self.plot1 = self.ax.plot()
        right_frame.grid(column = 1, rowspan = 2, row = 0)
        self.canvas = FigureCanvasTkAgg(fig, right_frame) #Add the figure to the canvas (needed for starting the animation)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand = True)
        self.canvas._tkcanvas.pack(side=tk.BOTTOM)
        
        self.ani = animation.FuncAnimation(fig, self.draw_graph, interval=400) #Starting the animation to enable live viewing
     
    def draw_graph(self, right_frame):
        #Plotting the graph
        if self.waveform.get() == "sawtooth":
            sawtooth = True
        else:
            sawtooth = False
            
        try:#Try to get the values   
            self.onelineXValues, extendedyArray, self.lineSizeTriangle = wavegenerator.previewSawtooth(int(self.sRateEntry.get()),
                                    float(self.imAngleEntry.get()),
                                    float(self.VxMaxEntry.get()),
                                    float(self.VyMaxEntry.get()),
                                    float(self.VyMinEntry.get()),
                                    float(self.VxMinEntry.get()),
                                    int(self.xPixelEntry.get()),
                                    int(self.yPixelEntry.get()),
                                    sawtooth)
        except: #If not all values are filled in the default values are used
            print("Using default")
            self.onelineXValues, extendedyArray, self.lineSizeTriangle = wavegenerator.previewSawtooth()
         
        doublexValues = np.append(self.onelineXValues, self.onelineXValues)   
        self.tValues = np.arange(doublexValues.size) 
        self.ax.clear()
        self.ax.plot(self.tValues, doublexValues)
        
    def calibrate(self):
        #Plotting the graph
        if self.waveform.get() == "sawtooth":
            sawtooth = True
        else:
            sawtooth = False
         
        sRate = int(self.sRateEntry.get())   
        
        try:#Try to get the values   
            xValues, yValues = wavegenerator.genSawtooth(int(self.sRateEntry.get()),
                                    float(self.imAngleEntry.get()),
                                    float(self.VxMaxEntry.get()),
                                    float(self.VyMaxEntry.get()),
                                    float(self.VyMinEntry.get()),
                                    float(self.VxMinEntry.get()),
                                    int(self.xPixelEntry.get()),
                                    int(self.yPixelEntry.get()),
                                    sawtooth)
        except: #If not all values are filled in the default values are used
            xValues, yValues = wavegenerator.genSawtooth()
         
        outputData, inputData = measure.calibrate(sRate, self.aiVar.get(), 
                                                  self.aoVarX.get(), xValues)
        
        tValues = np.arange(inputData.size)    
        #Plotting the data (feedback)
        plt.plot(tValues, outputData, 'b', tValues, inputData, 'r')
        plt.show()
   
    def measure(self):
        #Measuring
        if self.waveform.get() == "sawtooth":
            #Getting the x and y output
            try:#Try to get the values   
                xValues, yValues = wavegenerator.genSawtooth(int(self.sRateEntry.get()),
                                        float(self.imAngleEntry.get()),
                                        float(self.VxMaxEntry.get()),
                                        float(self.VyMaxEntry.get()),
                                        float(self.VyMinEntry.get()),
                                        float(self.VxMinEntry.get()),
                                        int(self.xPixelEntry.get()),
                                        int(self.yPixelEntry.get()),
                                        True)
            except: #If not all values are filled in the default values are used
                print("using default")
                xValues, yValues = wavegenerator.genSawtooth()
                
            exPixels = self.onelineXValues.size-int(self.xPixelEntry.get())
            measure.sawtooth(self.aiVar.get(),
                             self.aoVarX.get(),
                             self.aoVarY.get(),
                             int(self.sRateEntry.get()),
                             float(self.imAngleEntry.get()),
                             xValues,
                             yValues,
                             int(self.xPixelEntry.get()),
                             int(self.yPixelEntry.get()),
                             exPixels)
        else:
            sawtooth = False
            
            #Getting the x and y output
            try:#Try to get the values   
                xValues, yValues = wavegenerator.genSawtooth(int(self.sRateEntry.get()),
                                        float(self.imAngleEntry.get()),
                                        float(self.VxMaxEntry.get()),
                                        float(self.VyMaxEntry.get()),
                                        float(self.VyMinEntry.get()),
                                        float(self.VxMinEntry.get()),
                                        int(self.xPixelEntry.get()),
                                        int(self.yPixelEntry.get()),
                                        False)
            except: #If not all values are filled in the default values are used
                print("using default")
                xValues, yValues = wavegenerator.genSawtooth()
            
            exPixels = self.lineSizeTriangle-int(self.xPixelEntry.get())
            measure.triangle(self.aiVar.get(),
                             self.aoVarX.get(),
                             self.aoVarY.get(),
                             int(self.sRateEntry.get()),
                             float(self.imAngleEntry.get()),
                             xValues,
                             yValues,
                             int(self.xPixelEntry.get()),
                             int(self.yPixelEntry.get()),
                             exPixels)
            
            
#From: https://gist.github.com/chappers/bd910bfb0ed73c509802
#Help from: https://stackoverflow.com/questions/42599836/embedding-matplotlib-canvas-into-tkinter-gui-plot-is-not-showing-up-but-no-er/42600436#42600436
#And https://stackoverflow.com/questions/42815385/python-error-using-animation-funcanimation/42834862#42834862

root = tk.Tk()
newWindow = GUI(root)
root.mainloop()
"""

"""