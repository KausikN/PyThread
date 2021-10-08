"""
Stream lit GUI for hosting PyThread
"""

# Imports
import os
import cv2
import pickle
import functools
import numpy as np
import streamlit as st
import json

import PyThread
from Utils import ParserUtils
from Utils import ExecVisLibrary
from Utils import VideoUtils

# Main Vars
config = json.load(open('./StreamLitGUI/UIConfig.json', 'r'))

# Main Functions
def main():
    # Create Sidebar
    selected_box = st.sidebar.selectbox(
    'Choose one of the following',
        tuple(
            [config['PROJECT_NAME']] + 
            config['PROJECT_MODES']
        )
    )
    
    if selected_box == config['PROJECT_NAME']:
        HomePage()
    else:
        correspondingFuncName = selected_box.replace(' ', '_').lower()
        if correspondingFuncName in globals().keys():
            globals()[correspondingFuncName]()
 

def HomePage():
    st.title(config['PROJECT_NAME'])
    st.markdown('Github Repo: ' + "[" + config['PROJECT_LINK'] + "](" + config['PROJECT_LINK'] + ")")
    st.markdown(config['PROJECT_DESC'])

    # st.write(open(config['PROJECT_README'], 'r').read())

#############################################################################################################################
# Repo Based Vars
DEFAULT_SAVEPATH_GIF = 'ExecData/ExampleExec.gif'
DEFAULT_SAVEPATH_JSON = 'ExecData/ExampleExec.json'

AVAILABLEJOBS_PATH = 'StreamLitGUI/AvailableJobs.json'
AVAILABLEJOBSINITS_PATH = 'StreamLitGUI/AvailableJobInits.json'
DEFAULT_CODE_PACKAGE = 'StreamLitGUI/CacheData/'

JOB_SHAPE_INDICATORIMAGE_BLOCKSIZE = [20, 20]

EXECUTION_MODES = {
    'Threaded': PyThread.Run2DJob_Threaded_Basic,
    "Sequential": PyThread.Run2DJob_Seq_Basic
}

# Util Vars
AVAILABLE_JOBS = []
AVAILABLE_JOBINITS = []
TYPE_MAP = {
    "bool": bool,
    "int": int,
    "float": float,
    "str": str,
    "list": ParserUtils.ListParser,
    "obj": functools.partial(ParserUtils.ObjectParser, tempSavePath=DEFAULT_CODE_PACKAGE),
    "choice": ParserUtils.ChoiceParser
}
CHOICES_QUICK_MAP = {
    "int": int,
    "float": float,
    "bool": bool,
    "str": str
}

# Util Functions
def Hex_to_RGB(val):
    val = val.lstrip('#')
    lv = len(val)
    return tuple(int(val[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def RGB_to_Hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

@st.cache
def GenerateJobShapeIndicatorImage(JobShape):
    pixSize = JOB_SHAPE_INDICATORIMAGE_BLOCKSIZE
    I_ind_Size = np.array(JobShape) * np.array(pixSize)
    I_ind = np.zeros(I_ind_Size, dtype=np.uint8)
    for i in range(0, JobShape[0]):
        for j in range(0, JobShape[1]):
            I_ind[i*pixSize[0]:(i+1)*pixSize[0] - 1, j*pixSize[1]:(j+1)*pixSize[1] - 1] = 255
    return I_ind

def LoadAvailableData():
    global AVAILABLE_JOBS
    global AVAILABLE_JOBINITS
    AVAILABLE_JOBS = json.load(open(AVAILABLEJOBS_PATH, 'r'))["jobs"]
    AVAILABLE_JOBINITS = json.load(open(AVAILABLEJOBSINITS_PATH, 'r'))["jobinits"]

def GetNames(data):
    names = []
    for d in data:
        names.append(d["name"])
    return names

# Main Functions
def GetFunctions(JobsCodeText):
    ImportsCode = '''
import cv2
import functools
import numpy as np
import pickle

from JobLibrary import JobLibrary

'''
    SavePickleCode = '''
pickle.dump({JobObj}, open('{DEFAULT_CODE_PACKAGE}' + '/{JobObj}.p', 'wb'))
'''

    VarName = 'JobFunc'
    JobsCode = ImportsCode + VarName + " = " + JobsCodeText + SavePickleCode.format(DEFAULT_CODE_PACKAGE=DEFAULT_CODE_PACKAGE, JobObj=VarName)
    exec(JobsCode, globals())
    JobFuncs = pickle.load(open(os.path.join(DEFAULT_CODE_PACKAGE, VarName + ".p"), 'rb'))
    
    return JobFuncs

# UI Functions
def UI_JobShape():
    col1, col2 = st.columns(2)
    USERINPUT_ThreadsCount_X = col2.slider("N Job Columns (X)", 1, 15, 1, 1)
    USERINPUT_ThreadsCount_Y = col2.slider("N Job Rows (Y)", 1, 15, 1, 1)
    JobShape = [USERINPUT_ThreadsCount_Y, USERINPUT_ThreadsCount_X]
    I_JobShapeIndicator = GenerateJobShapeIndicatorImage(JobShape)
    col1.image(I_JobShapeIndicator, caption='Job Shape ' + str(JobShape), use_column_width=False)
    return JobShape

####################################################################################################################
def UI_Param(p, col=st, key=""):
    # Parse type
    inp = None
    if p["type"] == "bool":
        inp = col.checkbox(p["name"], p["default"], key=p["name"] + "_" + key)
    elif p["type"] == "int":
        inp = col.slider(p["name"], p["min"], p["max"], p["default"], p["step"], key=p["name"] + "_" + key)
    elif p["type"] == "float":
        inp = col.slider(p["name"], p["min"], p["max"], p["default"], p["step"], key=p["name"] + "_" + key)
    elif p["type"] == "str":
        inp = col.text_input(p["name"], p["default"], key=p["name"] + "_" + key)
    elif p["type"].startswith("list"):
        inp = col.text_area(p["name"], '\n'.join(list(map(str, p["default"]))), key=p["name"] + "_" + key)
        typeSplit = p["type"].split(":")
        inp = TYPE_MAP[typeSplit[0]](inp, TYPE_MAP[typeSplit[1]])
    elif p["type"].startswith("choice"):
        choice = col.selectbox(p["name"], p["choices"], p["choices"].index(p["default"]), key=p["name"] + "_" + key)
        if choice in CHOICES_QUICK_MAP.keys():
            inp = CHOICES_QUICK_MAP[choice]
        else:
            typeSplit = p["type"].split(":")
            inp = TYPE_MAP[typeSplit[0]](inp, TYPE_MAP[typeSplit[1]])

    return inp

def UI_Params(paramsData, col=st, key=""):
    ParamsInputs = {}
    for p in paramsData:
        inp = UI_Param(p, col, key)
        ParamsInputs[p["name"]] = inp
    return ParamsInputs
####################################################################################################################
def UI_JobDataSelector(AvailableJobsNames, key=""):
    col1, col2 = st.columns(2)
    USERINPUT_JobName = col1.selectbox("", AvailableJobsNames, key="J_" + key)
    USERINPUT_JobIndex = AvailableJobsNames.index(USERINPUT_JobName)
    USERINPUT_JobData = AVAILABLE_JOBS[USERINPUT_JobIndex]
    ParamsInputs = UI_Params(USERINPUT_JobData["params"], col=col2, key=key)
    USERINPUT_JobCode = USERINPUT_JobData["name"] # Params are applied later
    return USERINPUT_JobCode, ParamsInputs

def UI_JobSelect(AvailableJobsNames):
    USERINPUT_JobCode, ParamsInputs = UI_JobDataSelector(AvailableJobsNames, "JobKey_")
    USERINPUT_JobCode_Parsed = ParserUtils.ParseJobsText(USERINPUT_JobCode)
    JobFuncs = GetFunctions(USERINPUT_JobCode_Parsed)
    JobFunc = functools.partial(JobFuncs[0].func, **ParamsInputs)
    return JobFunc
####################################################################################################################
def UI_JobInitDataSelector(AvailableJobInitsNames, key=""):
    col1, col2 = st.columns(2)
    USERINPUT_JobInitName = col1.selectbox("", AvailableJobInitsNames, key="J_" + key)
    USERINPUT_JobInitIndex = AvailableJobInitsNames.index(USERINPUT_JobInitName)
    USERINPUT_JobInitData = AVAILABLE_JOBINITS[USERINPUT_JobInitIndex]
    ParamsInputs = UI_Params(USERINPUT_JobInitData["params"], col=col2, key=key)
    USERINPUT_JobInitCode = USERINPUT_JobInitData["name"] # Params are applied later
    return USERINPUT_JobInitCode, ParamsInputs

def UI_JobInitSelect(AvailableJobInitsNames):
    USERINPUT_JobInitCode, ParamsInputs = UI_JobInitDataSelector(AvailableJobInitsNames, "JobKeyInit_")
    USERINPUT_JobInitCode_Parsed = ParserUtils.ParseJobInitsText(USERINPUT_JobInitCode)
    JobInitFuncs = GetFunctions(USERINPUT_JobInitCode_Parsed)
    JobInitFunc = functools.partial(JobInitFuncs[0].func, **ParamsInputs)
    return JobInitFunc
####################################################################################################################
def UI_ExecModeSelect():
    USERINPUT_ExecModeName = st.selectbox("Select Execution Mode", list(EXECUTION_MODES.keys()))
    USERINPUT_ExecMode = EXECUTION_MODES[USERINPUT_ExecModeName]
    return USERINPUT_ExecMode

def UI_KeyValuePairDisplay(key, value):
    col1, col2 = st.columns([1, 2])
    col1.markdown(key)
    col2.markdown("```\n" + str(value))

def UI_ExecVisualise(ExecutionData):
    AnalysisData = ExecVisLibrary.ExecVis_Basic(ExecutionData, "Vis", pixSize=JOB_SHAPE_INDICATORIMAGE_BLOCKSIZE, animationPad=5, displayData=False)
    
    st.markdown("# Analysis")
    st.markdown("## Basic Analysis")
    UI_KeyValuePairDisplay("Function Name:", AnalysisData["func"])
    UI_KeyValuePairDisplay("Job Size:", AnalysisData["size"])

    st.markdown("## Overall Analysis")
    overallAnalysis = AnalysisData["overallAnalysis"]
    UI_KeyValuePairDisplay("Started:", overallAnalysis["Start"])
    UI_KeyValuePairDisplay("Ended:", overallAnalysis["End"])
    UI_KeyValuePairDisplay("Total Turn Around Time (TAT):", overallAnalysis["TAT"])
    UI_KeyValuePairDisplay("Turn Around Time per Job (TAT/job):", overallAnalysis["TAT_per_job"])
    UI_KeyValuePairDisplay("Total Waiting Time (WT):", overallAnalysis["WT"])

    st.markdown("## Execution Analysis")
    execAnalysis = AnalysisData["execAnalysis"]
    UI_KeyValuePairDisplay("Total Execution Time:", execAnalysis["total"])
    UI_KeyValuePairDisplay("Min Execution Time:", execAnalysis["min"])
    UI_KeyValuePairDisplay("Max Execution Time:", execAnalysis["max"])
    UI_KeyValuePairDisplay("Mean Execution Time:", execAnalysis["mean"])
    UI_KeyValuePairDisplay("Standard Deviation of Execution Time:", execAnalysis["std"])

    st.markdown("## Execution Heatmap")
    I_HeatMap = AnalysisData["heatMap"]
    st.image(I_HeatMap, caption="Execution Time HeatMap", use_column_width=True)
    I_ExecutionMap = AnalysisData["executionMap"]
    st.image(I_ExecutionMap, caption="Execution Map", use_column_width=True)

    st.markdown("## Execution Animation")
    event_Is = AnalysisData["eventAnim"]
    VideoUtils.SaveImageSeq(event_Is, DEFAULT_SAVEPATH_GIF, size=(640, 480), fps=24)
    st.image(DEFAULT_SAVEPATH_GIF, caption="Execution Animation", use_column_width=True)

# Repo Based Functions
def exec_vis():
    # Title
    st.header("Execution Visualiser")

    LoadAvailableData()
    AvailableJobsNames = GetNames(AVAILABLE_JOBS)
    AvailableJobInitsNames = GetNames(AVAILABLE_JOBINITS)

    # Load Inputs
    st.markdown("## Specify Execution Mode")
    USERINPUT_ExecMode = UI_ExecModeSelect()

    st.markdown("## Specify Job Size")
    USERINPUT_JobShape = UI_JobShape()

    st.markdown("## Specify Job")
    USERINPUT_Job = UI_JobSelect(AvailableJobsNames)

    st.markdown("## Specify Job Initializer")
    USERINPUT_JobInit = UI_JobInitSelect(AvailableJobInitsNames)

    # Process Inputs
    JobFunc = USERINPUT_Job
    JobInitFunc = functools.partial(USERINPUT_JobInit, JobFunc=JobFunc, size=USERINPUT_JobShape)

    # Display Outputs
    if st.button("Execute"):
        print("Initialising Jobs...")
        JobGrid = JobInitFunc()
        print("Running Jobs...")
        ExecutionData = USERINPUT_ExecMode(JobGrid, USERINPUT_JobShape)
        print("Visualising Jobs...")
        UI_ExecVisualise(ExecutionData)
    
#############################################################################################################################
# Driver Code
if __name__ == "__main__":
    main()