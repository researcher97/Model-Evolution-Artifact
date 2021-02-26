import os
import csv
from collections import defaultdict
from util.common import *

libs=['keras','tensorflow','torch']
DO_LIBRARY_FILTER=False
TARGET_LIBRARY='keras'

LEFT_KIND='MODIFIED'
MIDDLE_KIND='ADDED'
RIGHT_KIND='DELETED'

ANALYSIS_MODE='PARAM' #PARAM or VAL
ADD_TOTAL_COLUMN=True
ADD_USAGE_RATE=False

LIKELIHOOD_MODE='USAGE_LIKELIHOOD'
USAGE_THRESHOLD=5

# TARGET='work' #work or likelihood
# TARGET='likelihood'
TARGET='frequency'
TO_PERCENT=False
GrandFrequency=2071132
skipRowIfKeyNotPrensent=True
DO_AVERAGE=False
NORMALIZE_WITHIN_COLUMN=False
NORMALIZE_GLOBAL=False
MULTIPLY_FACTOR = None


leftFileName=None
middleFileName=None
rightFileName=None


current_dir=None
root_dir=None

left=None
middle=None
right=None
apiUsageAll=None
paramUsage=None


out=None

apiColumn=1
paramColumn=2
typeColumn=18 #normally, 18
paramWorkColum=9
valWorkColumn=16
paramLikelihoodColumn=7
paramImpactColumn=8
valLikelihoodColumn=14
paramFrequencyColumn=5
valFrequencyColumn=12
libColumn=0
targetColumn=None
FallBackTargetColumn=None
DEBUG=None
VALUE_DIRECTORY_AS_DATA=False

def setDirectory(rootDir=os.path.dirname(os.getcwd())):
    global current_dir, root_dir
    baseName='rq2_processing'
    current_dir=os.path.join(rootDir, baseName)
    root_dir = rootDir
def setGlobal(libraryFltr=False,targetLibIndex=0, trgt='likelihood', typColumn=18,normalizeGlobal=False,debug=False,
              likeMode='USAGE_LIKELIHOOD', normalizeWithin=False, toPercent=False,valueDir=False, multFactor=10000):
    global DO_LIBRARY_FILTER,TARGET_LIBRARY,LEFT_KIND,RIGHT_KIND,MIDDLE_KIND,ADD_USAGE_RATE,ADD_TOTAL_COLUMN
    global ANALYSIS_MODE,LIKELIHOOD_MODE,USAGE_THRESHOLD,DO_AVERAGE,MULTIPLY_FACTOR,TO_PERCENT,NORMALIZE_GLOBAL
    global NORMALIZE_WITHIN_COLUMN,typeColumn,skipRowIfKeyNotPrensent,TARGET
    global leftFileName,rightFileName,middleFileName,left,middle,right,apiUsageAll,paramUsage,out
    global apiColumn,paramFrequencyColumn,paramImpactColumn,paramColumn,paramLikelihoodColumn,paramWorkColum
    global valFrequencyColumn,valLikelihoodColumn,valWorkColumn,libColumn,targetColumn,FallBackTargetColumn,DEBUG,VALUE_DIRECTORY_AS_DATA

    DEBUG=debug
    DO_LIBRARY_FILTER=libraryFltr
    TARGET_LIBRARY=libs[targetLibIndex]
    TARGET=trgt
    typeColumn=typColumn
    NORMALIZE_GLOBAL=normalizeGlobal
    VALUE_DIRECTORY_AS_DATA=valueDir

    ANALYSIS_MODE = 'PARAM'  # PARAM or VAL
    ADD_TOTAL_COLUMN = True
    ADD_USAGE_RATE = False
    LIKELIHOOD_MODE = likeMode
    TO_PERCENT = toPercent
    skipRowIfKeyNotPrensent = True
    DO_AVERAGE = False
    NORMALIZE_WITHIN_COLUMN = normalizeWithin
    MULTIPLY_FACTOR = 1

    if TARGET == 'likelihood':
        NORMALIZE_WITHIN_COLUMN = False
        MULTIPLY_FACTOR = multFactor
        DO_AVERAGE = False
        ADD_USAGE_RATE = True

    if TARGET == 'work':
        DO_AVERAGE = True

    if NORMALIZE_GLOBAL:
        TO_PERCENT = True

    leftFileName = 'param_project_support_' + LEFT_KIND
    middleFileName = 'param_project_support_' + MIDDLE_KIND
    rightFileName = 'param_project_support_' + RIGHT_KIND

    if VALUE_DIRECTORY_AS_DATA==False:
        left = os.path.join(root_dir, 'merge', "merge_result", leftFileName + ".csv")
        middle = os.path.join(root_dir, 'merge', "merge_result", middleFileName + ".csv")
        right = os.path.join(root_dir, 'merge', "merge_result", rightFileName + ".csv")
    else:
        left = os.path.join(root_dir, 'value_processing', "result", leftFileName + ".csv")
        middle = os.path.join(root_dir, 'value_processing', "result", middleFileName + ".csv")
        right = os.path.join(root_dir, 'value_processing', "result", rightFileName + ".csv")
    apiUsageAll = os.path.join(root_dir, "boa_output_processing", "processed_data", "api_usage_all.csv")
    paramUsage = os.path.join(root_dir, 'merge', "merge_result", "param_usage.csv")

    if DO_LIBRARY_FILTER:
        out = open(os.path.join(current_dir, "processed_result",
                                TARGET_LIBRARY+'_'+ANALYSIS_MODE + '_' + TARGET + '_' + LEFT_KIND + '_' + MIDDLE_KIND + '_' + RIGHT_KIND + ".csv"),
                   "w")
    else:
        out = open(os.path.join(current_dir, "processed_result",
                            ANALYSIS_MODE + '_' + TARGET + '_' + LEFT_KIND + '_' + MIDDLE_KIND + '_' + RIGHT_KIND + ".csv"),
               "w")
    if TARGET == 'work' and ANALYSIS_MODE == 'PARAM':
        targetColumn = paramImpactColumn
    if TARGET == 'work' and ANALYSIS_MODE == 'VAL':
        targetColumn = valWorkColumn
    if TARGET == 'likelihood' and ANALYSIS_MODE == 'PARAM':
        targetColumn = paramFrequencyColumn
    if TARGET == 'likelihood' and ANALYSIS_MODE == 'VAL':
        targetColumn = valFrequencyColumn
        FallBackTargetColumn = paramFrequencyColumn
    if TARGET == 'frequency' and ANALYSIS_MODE == 'PARAM':
        targetColumn = paramFrequencyColumn
    if TARGET == 'frequency' and ANALYSIS_MODE == 'VAL':
        targetColumn = valFrequencyColumn
        FallBackTargetColumn = paramFrequencyColumn


def normalize(data, divideBy, percent=False):
    total=0.0
    for k in data:
        data[k]=data[k]/divideBy
        total+=data[k]
        if percent:
            data[k]=data[k]*100.0
    if TO_PERCENT:
        total*=100.0
    return data,total

def normalizeUsageLikelihood(data, likelihoods, percent=False):
    total=0.0
    for k in data:
        data[k]=data[k]/likelihoods[k]
        if MULTIPLY_FACTOR !=None:
            data[k]=data[k]*MULTIPLY_FACTOR
        elif percent:
            data[k]=data[k]*100.0
        total+=data[k]

    return data,total

def normalizeWithin(data):
    total=0
    for curType in data.keys():
        total+=data[curType]
    for curType in data.keys():
        data[curType]=(data[curType]/total)*100.0
    return data

def getAllTypes(left,right):
    types=set()
    for k in left.keys():
        types.add(k)
    for k in right.keys():
        types.add(k)
    return types

def getApiUsageAllFrequencyByParamType():
    global DO_LIBRARY_FILTER, TARGET_LIBRARY, LEFT_KIND, RIGHT_KIND, MIDDLE_KIND, ADD_USAGE_RATE, ADD_TOTAL_COLUMN
    global ANALYSIS_MODE, LIKELIHOOD_MODE, USAGE_THRESHOLD, DO_AVERAGE, MULTIPLY_FACTOR, TO_PERCENT, NORMALIZE_GLOBAL
    global NORMALIZE_WITHIN_COLUMN, typeColumn, skipRowIfKeyNotPrensent, TARGET
    global leftFileName, rightFileName, middleFileName, left, middle, right, apiUsageAll, paramUsage, out
    global apiColumn, paramFrequencyColumn, paramImpactColumn, paramColumn, paramLikelihoodColumn, paramWorkColum
    global valFrequencyColumn, valLikelihoodColumn, valWorkColumn, libColumn, targetColumn, FallBackTargetColumn,DEBUG

    apiUsageAllFrequency = {}

    api_type_mapping={}
    with open(paramUsage, 'r') as input:
        reader = csv.reader(input)
        next(reader)

        for line in reader:
            apiName = clean(line[0], False)
            curType = clean(line[4], False)
            if curType == '':
                continue
            if apiName not in api_type_mapping:
                api_type_mapping[apiName] = set()

            api_type_mapping[apiName].add(curType)


    with open(apiUsageAll, 'r') as input:
        reader = csv.reader(input)
        next(reader)

        for line in reader:
            apiName = clean(line[0], False)
            val = float(clean(line[1], False))

            if DO_LIBRARY_FILTER and getLibName(apiName)!=TARGET_LIBRARY:
                continue
            if apiName not in api_type_mapping:
                continue

            for curType in api_type_mapping[apiName]:
                if curType not in apiUsageAllFrequency:
                    apiUsageAllFrequency[curType] = 0

                apiUsageAllFrequency[curType] += val


    return apiUsageAllFrequency

def getVal(filename, do_average=True, do_normalize=False):
    global DO_LIBRARY_FILTER, TARGET_LIBRARY, LEFT_KIND, RIGHT_KIND, MIDDLE_KIND, ADD_USAGE_RATE, ADD_TOTAL_COLUMN
    global ANALYSIS_MODE, LIKELIHOOD_MODE, USAGE_THRESHOLD, DO_AVERAGE, MULTIPLY_FACTOR, TO_PERCENT, NORMALIZE_GLOBAL
    global NORMALIZE_WITHIN_COLUMN, typeColumn, skipRowIfKeyNotPrensent, TARGET
    global leftFileName, rightFileName, middleFileName, left, middle, right, apiUsageAll, paramUsage, out
    global apiColumn, paramFrequencyColumn, paramImpactColumn, paramColumn, paramLikelihoodColumn, paramWorkColum
    global valFrequencyColumn, valLikelihoodColumn, valWorkColumn, libColumn, targetColumn, FallBackTargetColumn

    summation={}
    totalkey={}
    col=None
    totalSum = 0
    alreadyTaken={}

    type_has_api = {}

    with open(filename, 'r') as input:
        reader=csv.reader(input)
        col=next(reader)

        for line in reader:

            if DO_LIBRARY_FILTER and line[libColumn].strip()!=TARGET_LIBRARY:
                continue

            curType = clean(line[typeColumn], False)
            apiName=clean(line[apiColumn], False)
            paramId=clean(line[paramColumn], False)

            if ANALYSIS_MODE=='PARAM':
                if apiName in alreadyTaken and paramId in alreadyTaken[apiName]:
                    continue

            if skipRowIfKeyNotPrensent and curType=='':
                continue

            try:
                val = float(clean(line[targetColumn], False))
            except:
                val=float(clean(line[FallBackTargetColumn], False))

            if apiName not in alreadyTaken:
                alreadyTaken[apiName]={}
            alreadyTaken[apiName][paramId]=True

            if curType not in summation:
               summation[curType]=0
               totalkey[curType]=0
               # type_has_api[curType]=set()

            summation[curType]+=val
            totalSum += val
            totalkey[curType]+=1
            # type_has_api[curType].add(apiName)

    # apiUsageAllFrequency = {}
    # with open(apiUsageAll, 'r') as input:
    #     reader = csv.reader(input)
    #     next(reader)
    #
    #     for line in reader:
    #         apiName = clean(line[0], False)
    #         val = float(clean(line[1], False))
    #
    #         for curType in type_has_api.keys():
    #             if apiName in type_has_api[curType]:
    #                 if curType not in apiUsageAllFrequency:
    #                     apiUsageAllFrequency[curType] = 0
    #
    #                 apiUsageAllFrequency[curType] += val

    if do_average:
        for curType in summation.keys():
            summation[curType]=summation[curType]/totalkey[curType]


    if do_normalize:
        for curType in summation.keys():
            summation[curType]=(summation[curType]/totalSum)
            if TO_PERCENT:
                summation[curType]=summation[curType]*100.0

    return totalSum,summation,col

def mainFun():
    global DO_LIBRARY_FILTER, TARGET_LIBRARY, LEFT_KIND, RIGHT_KIND, MIDDLE_KIND, ADD_USAGE_RATE, ADD_TOTAL_COLUMN
    global ANALYSIS_MODE, LIKELIHOOD_MODE, USAGE_THRESHOLD, DO_AVERAGE, MULTIPLY_FACTOR, TO_PERCENT, NORMALIZE_GLOBAL
    global NORMALIZE_WITHIN_COLUMN, typeColumn, skipRowIfKeyNotPrensent, TARGET
    global leftFileName, rightFileName, middleFileName, left, middle, right, apiUsageAll, paramUsage, out
    global apiColumn, paramFrequencyColumn, paramImpactColumn, paramColumn, paramLikelihoodColumn, paramWorkColum
    global valFrequencyColumn, valLikelihoodColumn, valWorkColumn, libColumn, targetColumn, FallBackTargetColumn

    leftTotal,leftSummation,leftCol=getVal(left, DO_AVERAGE, NORMALIZE_WITHIN_COLUMN)
    middleTotal,middleSummation,middleCol=getVal(middle, DO_AVERAGE, NORMALIZE_WITHIN_COLUMN)
    rightTotal,rightSummation,rightCol=getVal(right, DO_AVERAGE, NORMALIZE_WITHIN_COLUMN)
    types=getAllTypes(leftSummation, rightSummation)

    grandTotal=leftTotal+rightTotal+middleTotal

    totalSummation={}
    if ADD_TOTAL_COLUMN:
        for k in types:
            totalSummation[k] =0
            if k in leftSummation:
                totalSummation[k]=leftSummation[k]
            if k in rightSummation:
                totalSummation[k] += rightSummation[k]
            if k in middleSummation:
                totalSummation[k] += middleSummation[k]

    if TARGET=='work':
        targetColumn=paramFrequencyColumn
        _, leftLikelihood, leftCol= getVal(left, False, False)
        _, middleLikelihood, middleCol = getVal(middle, False, False)
        _, rightLikelihood, rightCol = getVal(right, False, False)

        if LIKELIHOOD_MODE == 'USAGE_LIKELIHOOD':
            grandApiUsageFrequency=getApiUsageAllFrequencyByParamType()
            leftLikelihood, _ = normalizeUsageLikelihood(leftLikelihood, grandApiUsageFrequency, False)
            middleLikelihood, _ = normalizeUsageLikelihood(middleLikelihood, grandApiUsageFrequency, False)
            rightLikelihood, _ = normalizeUsageLikelihood(rightLikelihood, grandApiUsageFrequency, False)
        else:
            leftLikelihood, _ = normalize(leftLikelihood, GrandFrequency, False)
            middleLikelihood, _ = normalize(middleLikelihood, GrandFrequency, False)
            rightLikelihood, _ = normalize(rightLikelihood, GrandFrequency, False)

        leftTotal=0
        rightTotal=0
        middleTotal=0
        for k in types:
            totalSummation[k]=0
            if k in leftLikelihood and k in leftSummation:
                leftSummation[k]=leftSummation[k]*leftLikelihood[k]
                leftTotal+=leftSummation[k]
                totalSummation[k] = leftSummation[k]
            if k in rightLikelihood and k in rightSummation:
                rightSummation[k]=rightSummation[k]*rightLikelihood[k]
                rightTotal += rightSummation[k]
                totalSummation[k] += rightSummation[k]
            if k in middleLikelihood and k in middleSummation:
                middleSummation[k] = middleSummation[k] * middleLikelihood[k]
                middleTotal += middleSummation[k]
                totalSummation[k] += middleSummation[k]
        grandTotal=leftTotal+rightTotal+middleTotal

    if TARGET=='likelihood':
        if LIKELIHOOD_MODE == 'USAGE_LIKELIHOOD':
            grandApiUsageFrequency=getApiUsageAllFrequencyByParamType()
            leftSummation, leftTotal = normalizeUsageLikelihood(leftSummation, grandApiUsageFrequency, False)
            middleSummation, middleTotal = normalizeUsageLikelihood(middleSummation, grandApiUsageFrequency, False)
            rightSummation, rightTotal=  normalizeUsageLikelihood(rightSummation, grandApiUsageFrequency, False)
        else:
            leftSummation, leftTotal = normalize(leftSummation, GrandFrequency, False)
            middleSummation, middleTotal = normalize(middleSummation, GrandFrequency, False)
            rightSummation, rightTotal = normalize(rightSummation, GrandFrequency, False)

        grandTotal=leftTotal+rightTotal+middleTotal
        grandApiUsageFrequency=normalizeWithin(grandApiUsageFrequency)



    if NORMALIZE_GLOBAL:
        leftSummation,_=normalize(leftSummation, grandTotal, TO_PERCENT)
        rightSummation,_ = normalize(rightSummation, grandTotal, TO_PERCENT)
        middleSummation, _ = normalize(middleSummation, grandTotal, TO_PERCENT)
        totalSummation,_ = normalize(totalSummation, grandTotal, TO_PERCENT)



    out.write(leftCol[typeColumn]+','+LEFT_KIND+','+MIDDLE_KIND+','+RIGHT_KIND)
    if ADD_TOTAL_COLUMN:
        out.write(',Total')
    if ADD_USAGE_RATE:
        out.write(',Usage Rate')
    out.write('\n')

    for k in types:

        out.write(k)
        if k in leftSummation:
            out.write(','+str(leftSummation[k]))
        else:
            out.write(',0')

        if TO_PERCENT:
            out.write('%')

        if k in middleSummation:
            out.write(',' + str(middleSummation[k]))
        else:
            out.write(',0')
        if TO_PERCENT:
            out.write('%')


        if k in rightSummation:
            out.write(','+str(rightSummation[k]))
        else:
            out.write(',0')
        if TO_PERCENT:
            out.write('%')
        out.write(',' + str(totalSummation[k]))
        if TO_PERCENT:
            out.write('%')

        if ADD_USAGE_RATE:
            out.write(','+str(grandApiUsageFrequency[k])+'%')

        out.write('\n')

    out.close()

    return leftSummation,middleSummation,rightSummation



if __name__ == "__main__":
    setDirectory()
    if DO_LIBRARY_FILTER==False:
        # setGlobal(libraryFltr=False, trgt='likelihood', valueDir=True)
        # mainFun()
        # setGlobal(libraryFltr=False, trgt='frequency', debug=True,valueDir=True)
        # mainFun()

        setGlobal(libraryFltr=False, trgt='likelihood',normalizeGlobal=False, toPercent=False)
        mainFun()
        setGlobal(libraryFltr=False, trgt='frequency', debug=True, normalizeGlobal=True)
        mainFun()
        # setGlobal(libraryFltr=False, trgt='work', debug=True, normalizeGlobal=True, likeMode='CHANGE_LIKELIHOOD')
        # mainFun()

    if DO_LIBRARY_FILTER:
        for k in range(len(libs)):
            setGlobal(libraryFltr=True,targetLibIndex=k, trgt='frequency', debug=True, normalizeGlobal=False)
            # setGlobal(libraryFltr=True,targetLibIndex=k, trgt='likelihood', debug=True)
            mainFun()

            setGlobal(libraryFltr=True,targetLibIndex=k, trgt='likelihood', debug=True, normalizeGlobal=True)
            mainFun()


