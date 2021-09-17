'''
A python tool to visualise and run threaded jobs
'''

# Imports
import os
import json
import threading
import time
import datetime
import functools

from JobLibrary import JobLibrary
from Utils import ExecVisLibrary
from Utils import VideoUtils

# Main Vars
THREADS_DATA = {}

# Thread Functions
def InitThreadData_2D(size):
    global THREADS_DATA
    THREADS_DATA = {"size": size, "logs": {}}
    for i in range(size[0]):
        for j in range(size[1]):
            THREADS_DATA["logs"][str(i) + "," + str(j)] = {"index": [i, j], "data": {}}

def ExtractThreadData_2D():
    global THREADS_DATA

    execData = []
    size = THREADS_DATA["size"]
    for i in range(size[0]):
        execRow = []
        for j in range(size[1]):
            execRow.append(THREADS_DATA["logs"][str(i) + "," + str(j)]["data"])
        execData.append(execRow)

    return execData

def ThreadRunner_Basic(job, index):
    global THREADS_DATA

    execData_Cell = {}
    # Before Start log data
    execData_Cell["start"] = BeforeLog_Basic(index, job)
    
    # Run Job
    execData_Cell["exec"] = job() # Runs Job and gets all stamped times during execution

    # After finish log exec data
    execData_Cell["end"] = AfterLog_Basic(execData_Cell["start"])
    # Update Thread Data with new exec data
    THREADS_DATA["logs"][','.join(list(map(str, index)))]["data"] = execData_Cell

# Logger Functions
def BeforeLog_Basic(index, func):
    log = {}
    log["func"] = func.func.__name__
    log["job_index"] = index
    log["start_time"] = time.time_ns()
    return log

def AfterLog_Basic(beforeLog):
    log = {}
    log["func"] = beforeLog["func"]
    log["job_index"] = beforeLog["job_index"]
    log["end_time"] = time.time_ns()
    log["exec_time"] = log["end_time"] - beforeLog["start_time"]
    return log

# Main Functions
def Run2DJob_Seq_Basic(job, size):
    '''
    Run a 2D job (2D set of functions) sequentially.
    '''
    execData2D = []

    # Start and execute all functions sequentially
    for i in range(len(job)):
        execData_Row = []
        for j in range(len(job[i])):
            execData_Cell = {}
            # Before Start log data
            execData_Cell["start"] = BeforeLog_Basic([i, j], job[i][j])

            # Run Job
            execData_Cell["exec"] = job[i][j]()

            # After finish log exec data
            execData_Cell["end"] = AfterLog_Basic(execData_Cell["start"])
            execData_Row.append(execData_Cell)
        execData2D.append(execData_Row)

    return execData2D

def Run2DJob_Threaded_Basic(job, size):
    '''
    Run a 2D job (2D set of functions) parallely in threaded fashion.
    '''
    execData2D = []

    # Init Thread Data
    THREADS = []
    InitThreadData_2D(size)
    for i in range(len(job)):
        for j in range(len(job[i])):
            th = threading.Thread(target=functools.partial(ThreadRunner_Basic, job[i][j], [i, j]))
            THREADS.append(th)

    # Start Threads
    for i in range(len(THREADS)):
        THREADS[i].start()
    
    # Wait for all threads finish
    for i in range(len(THREADS)):
        THREADS[i].join()

    # Extract Logs
    execData2D = ExtractThreadData_2D()

    return execData2D

# Driver Code
# # Params
# ExecGridShape = [10, 10]

# JobFunc = functools.partial(JobLibrary.Job_Wait, seconds=5.0)
# # JobInitFunc = functools.partial(JobLibrary.JobInit_Random, size=ExecGridShape, n_operands=100000, operand_type=int, valRange=[-10000, 10000])
# JobInitFunc = functools.partial(JobLibrary.JobInit_Assign, size=ExecGridShape, assignOperands=[])

# savePath_Data = 'ExecData/TestExec.json'
# savePath_GIF = 'ExecData/TestExec.gif'
# # Params

# # RunCode
# # Get initialised function grid
# print("Initialising Jobs...")
# JobGrid = JobInitFunc(JobFunc)
# # Run Jobs
# print("Running Jobs...")
# # ExecutionData = Run2DJob_Seq_Basic(JobGrid, ExecGridShape)
# ExecutionData = Run2DJob_Threaded_Basic(JobGrid, ExecGridShape)

# # Visualise Results
# print("Visualising Jobs...")
# AnalysisData = ExecVisLibrary.ExecVis_Basic(ExecutionData, "Test Vis", pixSize=[20, 20])
# I_HeatMap, event_Is, delayData = AnalysisData["heatMap"], AnalysisData["eventAnim"], AnalysisData["delayData"]

# # Save Results
# json.dump(ExecutionData, open(savePath_Data, 'w'))
# VideoUtils.SaveImageSeq(event_Is, savePath_GIF, size=(640, 480), fps=24)

# VideoUtils.ViewImage(I_HeatMap)
# VideoUtils.DisplayImageSequence(event_Is, delays=delayData, delayScale=0.5)