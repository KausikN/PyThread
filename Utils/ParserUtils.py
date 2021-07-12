'''
Parser Utils for Streamlit UI
'''

# Imports
import os
import pickle
import numpy as np

# Main Vars
LIST_SEPARATORS = [',', ';', '\n']

# Main Functions
def ParseJobsText(JobsText):
    Jobs = JobsText.split("\n")
    JobsData = ["functools.partial(JobLibrary.Job_" + j + ")" for j in Jobs]
    ParsedJobsText = "[" + ",".join(JobsData) + "]\n"
    return ParsedJobsText

def ParseJobInitsText(JobInitsText):
    JobInits = JobInitsText.split("\n")
    JobInitsData = ["functools.partial(JobLibrary.JobInit_" + j + ")" for j in JobInits]
    ParsedJobInitsText = "[" + ",".join(JobInitsData) + "]\n"
    return ParsedJobInitsText

# Specific Type Parsers
def ListParser(data, data_type=str):
    parsed_data = []
    for r in LIST_SEPARATORS:
        data = data.replace(r, ';')
    parsed_data = list(map(data_type, data.split(';')))
    return parsed_data

def ChoiceParser(data, data_type=str):
    parsed_data = data_type(data)
    return parsed_data

def ObjectParser(data, tempSavePath="StreamLitGUI/CacheData/"):
    varName = 'obj'
    importCode = """import pickle"""
    dataCode = "Data = " + str(data)
    saverCode = """pickle.dump(Data, "{saveDir}{saveName}.p")""".format(saveDir=tempSavePath, saveName=varName)
    finalCode = importCode + "\n" + dataCode + "\n" + saverCode
    exec(finalCode, globals())
    parsed_data = pickle.load(open(os.path.join(tempSavePath, varName + ".p"), 'rb'))
    return parsed_data

# Driver Code