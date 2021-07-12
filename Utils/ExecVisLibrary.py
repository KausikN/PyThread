'''
Execution Data Visulaiser Library
'''

# Imports
import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

# Utils Vars
figsize = (6.4, 4.8)
dpi = 100.0
fig = Figure(figsize=figsize, dpi=dpi)
canvas = FigureCanvasAgg(fig)

# Utils Functions
def PlotExecHeatMap(ExecTimesGrid, title=""):
    fig.clear(True)
    ax = fig.add_subplot(111)

    
    ax = sns.heatmap(ExecTimesGrid, ax=ax)
    plt.title(title)
    # plt.show()

    canvas.draw()
    buf = canvas.buffer_rgba()
    I_Heatmap = np.asarray(buf)

    return I_Heatmap

# Main Functions
def ExecVis_Basic(data, title, pixSize=[1, 1], displayData=True):
    '''Basic Execution Data Visualiser'''
    # Generate Plot Data
    data = np.array(data)
    # Exec Times Analysis
    dataFlat = np.reshape(data, np.product(data.shape))
    exec_times = []
    start_times = []
    end_times = []
    for d in dataFlat:
        exec_times.append(d["end"]["exec_time"] / 1e9)
        start_times.append(d["start"]["start_time"] / 1e9)
        end_times.append(d["end"]["end_time"] / 1e9)

    execAnalysis = {
        "total": np.sum(exec_times),
        "min": np.min(exec_times),
        "max": np.max(exec_times),
        "mean": np.mean(exec_times),
        "std": np.std(exec_times)
    }
    overallAnalysis = {
        "Start": np.min(start_times),
        "End": np.max(end_times),
        "TAT": (np.max(end_times) - np.min(start_times)), # Turn Around Time
        "TAT_per_job": (np.max(end_times) - np.min(start_times)) / len(start_times), # TAT per job
        "WT": (np.max(end_times) - np.min(start_times)) - np.sum(exec_times), # Waiting Time
    }

    FunctionName = dataFlat[0]["start"]["func"] if len(dataFlat) > 0 else "None"
    JobSize = data.shape
    JobSizeFlat = np.product(JobSize)

    # Display Data
    if displayData:
        print("----- EXEC DATA ---------------------------------------------")
        print("Function Name  :", FunctionName)
        print("Job Size       :", JobSize)
        print()
        print("-- Overall Analysis ---------------")
        print("Started  :", overallAnalysis["Start"])
        print("Ended    :", overallAnalysis["End"])
        print()
        print("Total Turn Around Time (TAT)        :", overallAnalysis["TAT"])
        print("Turn Around Time per Job (TAT/job)  :", overallAnalysis["TAT_per_job"])
        print("Total Waiting Time (WT)             :", overallAnalysis["WT"])
        print()
        print("-- Execution Analysis -------------")
        print("Total Execution Time                 :", execAnalysis["total"])
        print("Min Execution Time                   :", execAnalysis["min"])
        print("Max Execution Time                   :", execAnalysis["max"])
        print("Mean Execution Time                  :", execAnalysis["mean"])
        print("Standard Deviation of Execution Time :", execAnalysis["std"])


    # Plot Exec Times
    ExecTimesGrid = np.reshape(exec_times, JobSize)
    I_HeatMap = PlotExecHeatMap(ExecTimesGrid, title)

    # Plot Finish Animation - only for 2D data
    if len(JobSize) == 2:
        StartTimesGrid = np.reshape(start_times, JobSize)
        EndTimesGrid = np.reshape(end_times, JobSize)
        timesData = []
        namesData = []
        for i in range(JobSize[0]):
            for j in range(JobSize[1]):
                timesData.extend([StartTimesGrid[i][j], EndTimesGrid[i][j]])
                namesData.extend(["B_" + str(i) + "_" + str(j), "E_" + str(i) + "_" + str(j)])

        zipped_lists = zip(timesData, namesData)
        sorted_pairs = sorted(zipped_lists, reverse=False)
        tuples = zip(*sorted_pairs)
        timesData_Sorted, namesData_Sorted = [ list(t) for t in  tuples]

        eventOrder = []
        for n in namesData_Sorted:
            spl = n.split("_")
            eventOrder.append([spl[0], int(spl[1]), int(spl[2])])

        delayData = []
        for i in range(1, len(timesData_Sorted)):
            delayData.append(timesData_Sorted[i] - timesData_Sorted[i-1])
        delayData.append(0.0)

        # Generate Images
        I_Size = np.array(JobSize) * np.array(pixSize)
        I_event = np.zeros(I_Size)
        event_Is = [np.copy(I_event)]
        for i in range(len(eventOrder)):
            event = eventOrder[i]
            delay = delayData[i]
            if event[0] == "B":
                I_event[event[1]*pixSize[0]:(event[1]+1)*pixSize[0] - 1, event[2]*pixSize[1]:(event[2]+1)*pixSize[1] - 1] = 0.5
            elif event[0] == "E":
                I_event[event[1]*pixSize[0]:(event[1]+1)*pixSize[0] - 1, event[2]*pixSize[1]:(event[2]+1)*pixSize[1] - 1] = 1.0
            if delay > 0.0 or i == (len(eventOrder)-1):
                event_Is.append(np.copy(I_event))
        
        # Show Animation
        # DisplayImageSequence(event_Is, delayData, delayScale)

        # Analysis Data
        AnalysisData = {
            "func": FunctionName,
            "size": JobSize,
            "eventOrder": eventOrder,
            "eventTimes": timesData_Sorted,
            "delayData": delayData,
            "execAnalysis": execAnalysis,
            "overallAnalysis": overallAnalysis,
            "eventAnim": event_Is,
            "heatMap": I_HeatMap
        }

        return AnalysisData

# Driver Code