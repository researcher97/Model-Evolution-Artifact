import os
import csv
from collections import defaultdict
from util.common import *

libs=['keras','tensorflow','torch']
DO_LIBRARY_FILTER=False
TARGET_LIBRARY='torch'

LEFT_KIND='MODIFIED'
MIDDLE_KIND='ADDED'
RIGHT_KIND='DELETED'


ADD_TOTAL_COLUMN=True
ADD_USAGE_RATE=False

LIKELIHOOD_MODE='USAGE_LIKELIHOOD'

TARGET='work' #work or likelihood or frequency or impact
TO_PERCENT=False

GrandFrequency=1515829

skipRowIfKeyNotPrensent=True

DO_AVERAGE=False
NORMALIZE_WITHIN_COLUMN=False
NORMALIZE_GLOBAL=False

MULTIPLY_FACTOR = 1
leftFileName=None
middleFileName=None
rightFileName=None
current_dir=None
root_dir=None
left=None
middle=None
right=None
apiUsageAll=None

out=None

apiColumn=1
typeColumn=13
impactColumn=6
directChangeColumn=12
frequencyColumn=3
libColumn=0
DEBUG=True
apiUsageType=2
targetColumn=None


def setDirectory(rootDir=os.path.dirname(os.getcwd())):
    global current_dir, root_dir
    baseName='rq1_processing'
    current_dir=os.path.join(rootDir, baseName)
    root_dir = rootDir

def setGlobal(libraryFltr=False,targetLibIndex=0, trgt='likelihood', typColumn=13,normalizeGlobal=False,debug=False,
              likeMode='USAGE_LIKELIHOOD', normalizeWithin=False, toPercent=False, multiPlyFactor=10000):
    global DO_LIBRARY_FILTER,TARGET_LIBRARY,LEFT_KIND,RIGHT_KIND,MIDDLE_KIND,ADD_USAGE_RATE,ADD_TOTAL_COLUMN
    global LIKELIHOOD_MODE,USAGE_THRESHOLD,DO_AVERAGE,MULTIPLY_FACTOR,TO_PERCENT,NORMALIZE_GLOBAL
    global NORMALIZE_WITHIN_COLUMN,typeColumn,skipRowIfKeyNotPrensent,TARGET
    global leftFileName,rightFileName,middleFileName,left,middle,right,apiUsageAll,paramUsage,out
    global apiColumn,paramFrequencyColumn,paramImpactColumn,paramColumn,paramLikelihoodColumn,paramWorkColum
    global valFrequencyColumn,valLikelihoodColumn,valWorkColumn,libColumn,targetColumn,FallBackTargetColumn,DEBUG

    DEBUG=debug
    DO_LIBRARY_FILTER=libraryFltr
    TARGET_LIBRARY=libs[targetLibIndex]
    TARGET=trgt
    typeColumn=typColumn
    NORMALIZE_GLOBAL=normalizeGlobal

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
        DO_AVERAGE = False
        MULTIPLY_FACTOR = multiPlyFactor
        ADD_USAGE_RATE = True

    if TARGET == 'work' or TARGET=='impact':
        DO_AVERAGE = True

    if NORMALIZE_GLOBAL:
        TO_PERCENT = True

    leftFileName = 'api_project_support_' + LEFT_KIND
    middleFileName = 'api_project_support_' + MIDDLE_KIND
    rightFileName = 'api_project_support_' + RIGHT_KIND

    left = os.path.join(root_dir, 'merge', "merge_result", leftFileName + ".csv")
    middle = os.path.join(root_dir, 'merge', "merge_result", middleFileName + ".csv")
    right = os.path.join(root_dir, 'merge', "merge_result", rightFileName + ".csv")
    apiUsageAll = os.path.join(root_dir, "merge", "merge_result", "api_usage_all.csv")

    if DO_LIBRARY_FILTER:
        out = open(os.path.join(current_dir, "processed_result",
                                TARGET_LIBRARY+'_'+ '_' + TARGET + '_' + LEFT_KIND + '_' + MIDDLE_KIND + '_' + RIGHT_KIND + ".csv"),
                   "w")
    else:
        out = open(os.path.join(current_dir, "processed_result",
                             TARGET + '_' + LEFT_KIND + '_' + MIDDLE_KIND + '_' + RIGHT_KIND + ".csv"),
               "w")

    if TARGET == 'work':
        # targetColumn=directChangeColumn
        targetColumn=impactColumn

    if TARGET=='impact':
        targetColumn = impactColumn
    if TARGET == 'likelihood' or TARGET == 'frequency':
        targetColumn = frequencyColumn

def normalize(data, divideBy, percent=False):
    total=0.0
    for k in data:
        data[k]=data[k]/divideBy
        total+=data[k]
        if MULTIPLY_FACTOR !=None:
            data[k]=data[k]*MULTIPLY_FACTOR
        elif percent:
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
        total += data[k]

    return data,total

def getAllTypes(left,right):
    types=set()
    for k in left.keys():
        types.add(k)
    for k in right.keys():
        types.add(k)
    return types

def getApiUsageAllFrequency(normalized=True):
    global DO_LIBRARY_FILTER, TARGET_LIBRARY, LEFT_KIND, RIGHT_KIND, MIDDLE_KIND, ADD_USAGE_RATE, ADD_TOTAL_COLUMN
    global LIKELIHOOD_MODE, USAGE_THRESHOLD, DO_AVERAGE, MULTIPLY_FACTOR, TO_PERCENT, NORMALIZE_GLOBAL
    global NORMALIZE_WITHIN_COLUMN, typeColumn, skipRowIfKeyNotPrensent, TARGET
    global leftFileName, rightFileName, middleFileName, left, middle, right, apiUsageAll, paramUsage, out
    global apiColumn, paramFrequencyColumn, paramImpactColumn, paramColumn, paramLikelihoodColumn, paramWorkColum
    global valFrequencyColumn, valLikelihoodColumn, valWorkColumn, libColumn, targetColumn, FallBackTargetColumn, DEBUG
    apiUsageAllFrequency = {}
    total=0
    with open(apiUsageAll, 'r') as input:
        reader = csv.reader(input)
        next(reader)

        for line in reader:
            apiName = clean(line[0], False)
            val = float(clean(line[1], False))
            curType = clean(line[apiUsageType], False)
            if curType == '':
                continue
            if DO_LIBRARY_FILTER and getLibName(apiName)!=TARGET_LIBRARY:
                continue
            if curType not in apiUsageAllFrequency:
                apiUsageAllFrequency[curType] = 0

            apiUsageAllFrequency[curType] += val
            total+=val
        if normalized:
            for typ in apiUsageAllFrequency.keys():
                apiUsageAllFrequency[typ]= (apiUsageAllFrequency[typ]/total)*100.0

    return apiUsageAllFrequency

def getVal(filename, do_average=True, do_normalize=False):
    global DO_LIBRARY_FILTER, TARGET_LIBRARY, LEFT_KIND, RIGHT_KIND, MIDDLE_KIND, ADD_USAGE_RATE, ADD_TOTAL_COLUMN
    global LIKELIHOOD_MODE, USAGE_THRESHOLD, DO_AVERAGE, MULTIPLY_FACTOR, TO_PERCENT, NORMALIZE_GLOBAL
    global NORMALIZE_WITHIN_COLUMN, typeColumn, skipRowIfKeyNotPrensent, TARGET
    global leftFileName, rightFileName, middleFileName, left, middle, right, apiUsageAll, paramUsage, out
    global apiColumn, paramFrequencyColumn, paramImpactColumn, paramColumn, paramLikelihoodColumn, paramWorkColum
    global valFrequencyColumn, valLikelihoodColumn, valWorkColumn, libColumn, targetColumn, FallBackTargetColumn, DEBUG
    summation={}
    totalkey={}
    col=None
    totalSum = 0
    alreadyTaken={}

    with open(filename, 'r') as input:
        reader=csv.reader(input)
        col=next(reader)

        for line in reader:

            if DO_LIBRARY_FILTER and line[libColumn].strip()!=TARGET_LIBRARY:
                continue

            curType = clean(line[typeColumn], False)
            apiName=clean(line[apiColumn], False)

            if skipRowIfKeyNotPrensent and curType=='':
                continue

            val = float(clean(line[targetColumn], False))

            alreadyTaken[apiName]=True

            if curType not in summation:
               summation[curType]=0
               totalkey[curType]=0
            summation[curType]+=val
            totalSum += val
            totalkey[curType]+=1


    apiUsageAllFrequency={}
    with open(apiUsageAll, 'r') as input:
        reader = csv.reader(input)
        next(reader)

        for line in reader:
            apiName = clean(line[0], False)
            val = float(clean(line[1], False))
            curType = clean(line[apiUsageType], False)
            if apiName not in alreadyTaken or curType=='':
                continue
            if curType not in apiUsageAllFrequency:
                apiUsageAllFrequency[curType]=0

            apiUsageAllFrequency[curType] +=val

    if do_average:
        for curType in summation.keys():
            summation[curType]=summation[curType]/totalkey[curType]


    if do_normalize:
        for curType in summation.keys():
            summation[curType]=(summation[curType]/totalSum)
    return totalSum,summation,col,apiUsageAllFrequency

def mainFun():
    global DO_LIBRARY_FILTER, TARGET_LIBRARY, LEFT_KIND, RIGHT_KIND, MIDDLE_KIND, ADD_USAGE_RATE, ADD_TOTAL_COLUMN
    global LIKELIHOOD_MODE, USAGE_THRESHOLD, DO_AVERAGE, MULTIPLY_FACTOR, TO_PERCENT, NORMALIZE_GLOBAL
    global NORMALIZE_WITHIN_COLUMN, typeColumn, skipRowIfKeyNotPrensent, TARGET
    global leftFileName, rightFileName, middleFileName, left, middle, right, apiUsageAll, paramUsage, out
    global apiColumn, paramFrequencyColumn, paramImpactColumn, paramColumn, paramLikelihoodColumn, paramWorkColum
    global valFrequencyColumn, valLikelihoodColumn, valWorkColumn, libColumn, targetColumn, FallBackTargetColumn, DEBUG
    leftTotal,leftSummation,leftCol,leftApiUsageAllFrequency=getVal(left, DO_AVERAGE, NORMALIZE_WITHIN_COLUMN)
    middleTotal,middleSummation,middleCol,middleApiUsageAllFrequency=getVal(middle, DO_AVERAGE, NORMALIZE_WITHIN_COLUMN)
    rightTotal,rightSummation,rightCol,rightApiUsageAllFrequency=getVal(right, DO_AVERAGE, NORMALIZE_WITHIN_COLUMN)
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
        targetColumn=frequencyColumn
        _, leftLikelihood, leftCol,leftApiUsageAllFrequency = getVal(left, False, False)
        _, middleLikelihood, middleCol, middleApiUsageAllFrequency = getVal(middle, False, False)
        _, rightLikelihood, rightCol,rightApiUsageAllFrequency = getVal(right, False, False)
        if LIKELIHOOD_MODE == 'USAGE_LIKELIHOOD':
            leftLikelihood, _ = normalizeUsageLikelihood(leftLikelihood, leftApiUsageAllFrequency, False)
            middleLikelihood, _ = normalizeUsageLikelihood(middleLikelihood, middleApiUsageAllFrequency, False)
            rightLikelihood, _ = normalizeUsageLikelihood(rightLikelihood, rightApiUsageAllFrequency, False)
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
                middleSummation[k]=middleSummation[k]*middleLikelihood[k]
                middleTotal += middleSummation[k]
                totalSummation[k] += middleSummation[k]
        grandTotal=leftTotal+rightTotal+middleTotal

    if TARGET=='likelihood':
        if LIKELIHOOD_MODE == 'USAGE_LIKELIHOOD':
            leftSummation, leftTotal = normalizeUsageLikelihood(leftSummation, leftApiUsageAllFrequency, TO_PERCENT)
            middleSummation, middleTotal = normalizeUsageLikelihood(middleSummation, middleApiUsageAllFrequency, TO_PERCENT)
            rightSummation, rightTotal = normalizeUsageLikelihood(rightSummation, rightApiUsageAllFrequency, TO_PERCENT)
        else:
            leftSummation, leftTotal = normalize(leftSummation, GrandFrequency, False)
            middleSummation, middleTotal = normalize(middleSummation, GrandFrequency, False)
            rightSummation, rightTotal = normalize(rightSummation, GrandFrequency, False)

        grandTotal=leftTotal+rightTotal+middleTotal
        if ADD_USAGE_RATE:
            allGrandUsages=getApiUsageAllFrequency()

    if NORMALIZE_GLOBAL:
        leftSummation,_=normalize(leftSummation, grandTotal, TO_PERCENT)
        middleSummation, _ = normalize(middleSummation, grandTotal, TO_PERCENT)
        rightSummation,_ = normalize(rightSummation, grandTotal, TO_PERCENT)
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
            out.write(','+str(middleSummation[k]))
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
            out.write(','+str(allGrandUsages[k])+'%')
        out.write('\n')

    out.close()

    return leftSummation,middleSummation,rightSummation


if __name__ == "__main__":
    setDirectory()
    if DO_LIBRARY_FILTER==False:
        setGlobal(libraryFltr=False, trgt='likelihood',multiPlyFactor=None, toPercent=True)
        mainFun()
        setGlobal(libraryFltr=False, trgt='frequency')
        mainFun()
        setGlobal(libraryFltr=False, trgt='impact')
        mainFun()
        setGlobal(libraryFltr=False, trgt='work', debug=True, normalizeGlobal=False)
        mainFun()

    if DO_LIBRARY_FILTER:
        for k in range(len(libs)):
            # setGlobal(libraryFltr=True,targetLibIndex=k, trgt='frequency', debug=True)
            # # setGlobal(libraryFltr=True,targetLibIndex=k, trgt='likelihood', debug=True)
            # mainFun()
            #
            # setGlobal(libraryFltr=True,targetLibIndex=k, trgt='likelihood', debug=True)
            # mainFun()

            setGlobal(libraryFltr=True,targetLibIndex=k, trgt='work', debug=True, normalizeGlobal=False)
            mainFun()



