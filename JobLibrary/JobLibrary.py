'''
Library for a variety of job functions
'''

# Imports
import functools
import numpy as np
import random
import time

# Main Vars
OPERAND_TYPES = [int, float, str]

# Job Initialisers
def JobInit_Random(JobFunc, size=[1, 1], n_operands=2, operand_type=int, valRange=[-100, 100]):
    flatSize = np.product(size)
    GeneratedVals = []
    if operand_type == int:
        valRange = [int(valRange[0]), int(valRange[1])]
        GeneratedVals = np.random.randint(valRange[0], valRange[1], (flatSize, n_operands))
    elif operand_type == float:
        GeneratedVals = np.random.uniform(valRange[0], valRange[1], (flatSize, n_operands))
    elif operand_type == str:
        alphabets = "abcdefghijklmnopqrstuvxyz".split()
        GeneratedVals = np.random.choice(alphabets, (flatSize, n_operands))
    else:
        alphabets = "abcdefghijklmnopqrstuvxyz".split()
        GeneratedVals = np.random.choice(alphabets, (flatSize, n_operands))
    
    ParamedFuncs = []
    for i in range(flatSize):
        params = list(GeneratedVals[i])
        ParamedFuncs.append(functools.partial(JobFunc, *params))
    ParamedFuncs = list(np.reshape(ParamedFuncs, size))

    return ParamedFuncs

def JobInit_Assign(JobFunc, size=[1, 1], assignOperands=[]):
    flatSize = np.product(size)
    
    ParamedFuncs = []
    for i in range(flatSize):
        params = list(assignOperands)
        ParamedFuncs.append(functools.partial(JobFunc, *params))
    ParamedFuncs = list(np.reshape(ParamedFuncs, size))

    return ParamedFuncs

# Job Functions
def Job_Add(*operands):
    timeStamps = []
    sum = 0

    timeStamps.append(time.time_ns())
    if len(operands) > 0:
        sum = operands[0]
        for operand in operands[1:]:
            sum += operand
            timeStamps.append(time.time_ns())
    timeStamps.append(time.time_ns())

    output = {
        "sum": sum,
        "time_stamps": timeStamps
    }
    return output

def Job_Multiply(*operands):
    timeStamps = []
    product = 0

    timeStamps.append(time.time_ns())
    if len(operands) > 0:
        product = operands[0]
        for operand in operands[1:]:
            product *= operand
            timeStamps.append(time.time_ns())
    timeStamps.append(time.time_ns())

    output = {
        "product": product,
        "time_stamps": timeStamps
    }
    return output

def Job_GenerateRandom_Looped(*operands, valRange=[-100, 100]):
    timeStamps = []
    genRand = []

    timeStamps.append(time.time_ns())
    genSize = np.array(operands)
    genSizeFlat = np.product(genSize)
    for i in range(genSizeFlat):
        genRand.append(random.randint(valRange[0], valRange[1]))
        timeStamps.append(time.time_ns())
    genRand = np.reshape(genRand, genSize)
    timeStamps.append(time.time_ns())

    output = {
        "random_value": genRand,
        "time_stamps": timeStamps
    }
    return output

def Job_GenerateRandom_Numpy(*operands, valRange=[-100, 100]):
    timeStamps = []
    genRand = []

    timeStamps.append(time.time_ns())
    genSize = np.array(operands)
    genRand = np.random.randint(valRange[0], valRange[1], genSize)
    timeStamps.append(time.time_ns())

    output = {
        "random_value": genRand,
        "time_stamps": timeStamps
    }
    return output

def Job_Wait(*operands, seconds=1.0):
    timeStamps = []

    timeStamps.append(time.time_ns())
    time.sleep(seconds)
    timeStamps.append(time.time_ns())

    output = {
        "time_stamps": timeStamps
    }
    return output

# Driver Code