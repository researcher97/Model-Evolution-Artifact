import os
import csv
from collections import defaultdict
from scipy.stats import gmean
from util.common import *

minParamImpactCount=20
minParamRevisionCount=5
minParamProjectCount=2

minValImpactCount=30
minValRevisionCount=5
minValProjectCount=2

doFilter=False
skipRowIfKeyNotPrensent=True
leftData=defaultdict(list)

kinds=['MODIFIED', 'ADDED', 'DELETED', 'MODIFIED_DELETED']
# direction='added'
direction=''
kind='MODIFIED'

TIMED_MODE=False
TIME_SLOT=2
rightFileName=''

current_dir=None
root_dir=None
input_file=None
out=None
DEBUG=None

def setDirectory(rootDir=os.path.dirname(os.getcwd())):
    global current_dir, root_dir
    baseName='rq2_processing'
    current_dir=os.path.join(rootDir, baseName)
    root_dir = rootDir

def setGlobal(filterFlag=True,skipRowFlag=True,dir='',timeFlag=False,slot=0,changeKindIndex=0,debug=True, justTimedMode=False):
    global doFilter,skipRowIfKeyNotPrensent,direction,TIMED_MODE,TIME_SLOT,kind,rightFileName,input_file,out,DEBUG

    DEBUG=debug
    doFilter=filterFlag
    skipRowIfKeyNotPrensent=skipRowFlag
    direction=dir
    TIMED_MODE=timeFlag
    TIME_SLOT=slot
    kind=kinds[changeKindIndex]
    rightFileName = 'rq2param'
    if direction == 'added':
        rightFileName = 'rq2param' + '_added'
    if TIMED_MODE or justTimedMode:
        rightFileName += "_timed"

    input_file=os.path.join(root_dir, "boa_output_processing", "processed_data", rightFileName+".csv")
    if direction == 'added':
        out = open(
            os.path.join(current_dir, "processed_result", "param_" + direction + "_project_support_" + kind + ".csv"),
            "w")
    else:
        out = open(
            os.path.join(current_dir, "processed_result", "param_project_support_" + kind + ".csv"), "w")


def getLeftLine(layerApi):
    global leftData

    if layerApi in leftData:
        return leftData[layerApi]
    return ''

def calculateImpact(apiName,paramId,val, api_count, revision_set, all_revision_set):
    totalCount=0
    revisionCount=0
    revSet = revision_set[apiName][paramId]
    if val!=None:
        revSet=revSet[val]

    for projectName,revisionId in revSet:
        totalCount+=api_count[projectName][revisionId]
        revisionCount+=1
    revSup = (revisionCount / len(all_revision_set)) * 100.0
    # if doFilter:
    #     if revSup<0.01:
    #         return None

    impact=totalCount/revisionCount
    return impact,revSup,revisionCount


def mainFun():
    global doFilter, skipRowIfKeyNotPrensent, direction, TIMED_MODE, TIME_SLOT, kind, rightFileName, input_file, out, leftData,DEBUG

    grandFrequency=0
    coAdded=0
    laterAdded=0
    laterModified=0
    laterDeleted=0

    with open(input_file, 'r') as input:
        reader=csv.reader(input)
        cols=next(reader)

        frequency_aggregator_impact_param={}
        frequency_aggregator_project_param = defaultdict(set)
        frequency_aggregator_impact_val={}
        frequency_aggregator_project_val=defaultdict(set)

        api_count={}
        revision_set_param={}
        revision_set_val = {}

        all_revision_set=set()
        all_revision_kind_wise={}

        all_projects=set()
        tf_projects=set()
        keras_projects=set()
        torch_projects=set()

        out.write("Library,API Name,Param,Value,Param Project Support,Param Change Frequency,Param G-mean,"+
                  "Param Likelihood,Param Impact,Param Work,Param Revision Support"+
                  ",Val Project Support,Val Change Frequency,Val G-mean,"+
                  "Val Likelihood,Val Impact,Val Work,Val Revision Support"+
                  "\n")

        for line in reader:
            if anyEmpty(line, [0,1,2]):
                continue

            projectName=line[0].strip()
            revisionId = line[1].strip()
            apiName = line[2].strip()
            libName =getLibName(apiName)
            parChangeKind = line[7].strip()

            if libName=='':
                continue

            paramId = line[3].strip()
            val = line[4].strip()
            changekind = line[5].strip()
            impactCount = line[6].strip()
            if TIMED_MODE:
                timeSlot = int(line[8].strip())

                if timeSlot!=TIME_SLOT:
                    continue

            if parChangeKind.lower() != 'modified':
                continue

            if apiName not in revision_set_param:
                revision_set_param[apiName] = {}
                revision_set_val[apiName]={}
            if paramId not in revision_set_param[apiName]:
                revision_set_param[apiName][paramId] = set()
                revision_set_val[apiName][paramId]={}
            if val not in revision_set_val[apiName][paramId]:
                revision_set_val[apiName][paramId][val]=set()

            if projectName not in api_count:
                api_count[projectName] = {}
            if revisionId not in api_count[projectName]:
                api_count[projectName][revisionId] = 0

            api_count[projectName][revisionId] += int(impactCount)

            revision_set_param[apiName][paramId].add((projectName,revisionId))
            revision_set_val[apiName][paramId][val].add((projectName, revisionId))

            all_revision_set.add((projectName,revisionId))

            if changekind not in all_revision_kind_wise:
                all_revision_kind_wise[changekind]=set()
            all_revision_kind_wise[changekind].add((projectName,revisionId))

            grandFrequency+=int(impactCount)

            if changekind=='ADDED' and parChangeKind=='ADDED':
                coAdded+=int(impactCount)
            if changekind == 'ADDED' and parChangeKind == 'MODIFIED':
                laterAdded += int(impactCount)
            if changekind=='MODIFIED' and parChangeKind=='MODIFIED':
                laterModified+=int(impactCount)
            if changekind=='DELETED' and parChangeKind=='DELETED':
                laterDeleted+=int(impactCount)

            if kind=='MODIFIED_DELETED' and changekind=='ADDED':
                continue
            if kind!='MODIFIED_DELETED' and changekind != kind:
                continue

            if libName not in frequency_aggregator_impact_param:
                frequency_aggregator_impact_param[libName]={}
            if apiName not in frequency_aggregator_impact_param[libName]:
                frequency_aggregator_impact_param[libName][apiName]={}
            if paramId not in frequency_aggregator_impact_param[libName][apiName]:
                frequency_aggregator_impact_param[libName][apiName][paramId] = 0

            frequency_aggregator_impact_param[libName][apiName][paramId]+=int(impactCount)

            if libName not in frequency_aggregator_project_param:
                frequency_aggregator_project_param[libName]={}
            if apiName not in frequency_aggregator_project_param[libName]:
                frequency_aggregator_project_param[libName][apiName]={}
            if paramId not in frequency_aggregator_project_param[libName][apiName]:
                frequency_aggregator_project_param[libName][apiName][paramId]=set()

            frequency_aggregator_project_param[libName][apiName][paramId].add(projectName)

            if libName not in frequency_aggregator_impact_val:
                frequency_aggregator_impact_val[libName] = {}
            if apiName not in frequency_aggregator_impact_val[libName]:
                frequency_aggregator_impact_val[libName][apiName] = {}
            if paramId not in frequency_aggregator_impact_val[libName][apiName]:
                frequency_aggregator_impact_val[libName][apiName][paramId] = {}
            if val not in frequency_aggregator_impact_val[libName][apiName][paramId]:
                frequency_aggregator_impact_val[libName][apiName][paramId][val] = 0

            frequency_aggregator_impact_val[libName][apiName][paramId][val] += int(impactCount)

            if libName not in frequency_aggregator_project_val:
                frequency_aggregator_project_val[libName] = {}
            if apiName not in frequency_aggregator_project_val[libName]:
                frequency_aggregator_project_val[libName][apiName] = {}
            if paramId not in frequency_aggregator_project_val[libName][apiName]:
                frequency_aggregator_project_val[libName][apiName][paramId] = {}
            if val not in frequency_aggregator_project_val[libName][apiName][paramId]:
                frequency_aggregator_project_val[libName][apiName][paramId][val] = set()

            frequency_aggregator_project_val[libName][apiName][paramId][val].add(projectName)

            all_projects.add(projectName)
            if libName=="keras":
                keras_projects.add(projectName)
            if libName=="tensorflow":
                tf_projects.add(projectName)
            if libName=="torch":
                torch_projects.add(projectName)


        # frequency_aggregator=sorted(frequency_aggregator_impact.items(), key=lambda x: x[1], reverse=True)
        # frequency_aggregator = sorted(frequency_aggregator_impact.items(), key=lambda x: x[1], reverse=True)

        if DEBUG:
            print("total projects: ", len(all_projects))
            print("total keras projects: ", len(keras_projects))
            print("total tf projects: ", len(tf_projects))
            print("total torch projects: ", len(torch_projects))

        skipCount=0
        totalFrequency=0
        skippedForMinParamImpactCount=0
        skippedForMinRevCount=0
        skippedForMinProjectCount=0
        totalRowAdded=0
        skippedForMinValImpactCount=0
        skippedForMinValProjectCount=0
        skippedForMinValRevCount=0

        for libName in frequency_aggregator_impact_val.keys():
            for apiName in frequency_aggregator_impact_val[libName].keys():
                for paramId in frequency_aggregator_impact_val[libName][apiName].keys():

                    paramImpactCount=frequency_aggregator_impact_param[libName][apiName][paramId]
                    paramPCount=len(frequency_aggregator_project_param[libName][apiName][paramId])

                    impactParam, revSupportParam,revCountParam = calculateImpact(apiName, paramId, None, api_count, revision_set_param,
                                                                   all_revision_set)
                    likelihoodParam = paramImpactCount / grandFrequency
                    workParam=likelihoodParam*impactParam

                    if impactParam == None:
                        skipCount += 1
                        continue

                    if doFilter:
                        if paramImpactCount<minParamImpactCount:
                            skipCount+=1
                            skippedForMinParamImpactCount+=1
                            continue
                        if paramPCount<minParamProjectCount:
                            skipCount+=1
                            skippedForMinProjectCount+=1
                            continue
                        if revCountParam<minParamRevisionCount:
                            skipCount+=1
                            skippedForMinRevCount+=1
                            continue

                    totalFrequency+=paramImpactCount

                    valAddedFlag=False

                    for val in frequency_aggregator_impact_val[libName][apiName][paramId].keys():

                        valImpactCount = frequency_aggregator_impact_val[libName][apiName][paramId][val]
                        valPCount = len(frequency_aggregator_project_val[libName][apiName][paramId][val])

                        lib_support_param = 0.0
                        lib_support_val=0.0

                        if libName=="keras":
                            lib_support_param = (paramPCount / float(len(keras_projects))) * 100.0
                            lib_support_val = (valPCount / float(len(keras_projects))) * 100.0
                        if libName=="tensorflow":
                            lib_support_param = (paramPCount / float(len(tf_projects))) * 100.0
                            lib_support_val = (valPCount / float(len(tf_projects))) * 100.0
                        if libName == "torch":
                            lib_support_param = (paramPCount / float(len(torch_projects))) * 100.0
                            lib_support_val = (valPCount / float(len(torch_projects))) * 100.0

                        gmanParam=gmean([lib_support_param,paramImpactCount])
                        gmanVal = gmean([lib_support_val, valImpactCount])

                        # if doFilter:
                        #     if gman < 1 or lib_support < 0.1:
                        #         skipCount+=1
                        #         continue

                        impactVal, revSupportVal,revCountVal = calculateImpact(apiName, paramId, val, api_count, revision_set_val,
                                                                      all_revision_set)
                        likelihoodVal = valImpactCount / grandFrequency
                        workVal = likelihoodVal * impactVal

                        if doFilter:
                            if valImpactCount < minValImpactCount:
                                skipCount += 1
                                skippedForMinValImpactCount += 1
                                continue
                            if valPCount < minValProjectCount:
                                skipCount += 1
                                skippedForMinValProjectCount += 1
                                continue
                            if revCountVal < minValRevisionCount:
                                skipCount += 1
                                skippedForMinValRevCount += 1
                                continue

                        totalRowAdded+=1
                        valAddedFlag=True
                        out.write(libName + "," + apiName + "," +paramId+','+
                                  val+','+str(lib_support_param) + ',' + str(paramImpactCount) +","
                                  +str(gmanParam)+','+str(likelihoodParam)+
                                  ','+str(impactParam)+','+str(workParam)+','+str(revSupportParam)+','
                                  + str(lib_support_val) + ',' + str(valImpactCount) + ","
                                  + str(gmanVal) + ',' + str(likelihoodVal) +
                                  ',' + str(impactVal) + ',' + str(workVal) + ',' + str(revSupportVal) +"\n")

                    if valAddedFlag==False:
                        totalRowAdded += 1
                        out.write(libName + "," + apiName + "," + paramId + ',' +
                                  '' + ',' + str(lib_support_param) + ',' + str(paramImpactCount) + ","
                                  + str(gmanParam) + ',' + str(likelihoodParam) +
                                  ',' + str(impactParam) + ',' + str(workParam) + ',' + str(revSupportParam) + ','
                                  + str('') + ',' + str('') + ","
                                  + str('') + ',' + str('') +
                                  ',' + str('') + ',' + str('') + ',' + str('') + "\n")
        out.close()


        if kind=='MODIFIED_DELETED':
            overallKindImpact = totalFrequency / (len(all_revision_kind_wise['MODIFIED'])+len(all_revision_kind_wise['DELETED']))
        else:
            overallKindImpact = totalFrequency / len(all_revision_kind_wise[kind])
        # overallKindLikelihood = totalFrequency / totalUsage
        # overallKindWork = overallKindImpact * overallKindLikelihood

        # print("Overall Kind Likelihood: ", overallKindLikelihood)
        # print("Overall Kind Impact: ", overallKindImpact)
        # print("Overall Kind Work: ", overallKindWork)

        overallChangeKindLikelihood = totalFrequency / grandFrequency
        overallChangeKindWork = overallKindImpact * overallChangeKindLikelihood

        if DEBUG:
            print('change kinds: ', all_revision_kind_wise.keys())
            print("Overall Change Kind Likelihood: ", overallChangeKindLikelihood)
            print("Overall Change Kind Impact: ", overallKindImpact)
            print("Overall Change Kind Work: ", overallChangeKindWork)

            print("Total change frequency, Grand frequency: ", totalFrequency, grandFrequency)
            print("Total skipped api: ", skipCount)
            print("Total skipped for param count: ", skippedForMinParamImpactCount)
            print("Total skipped for project count: ", skippedForMinProjectCount)
            print("Total skipped for revision count: ", skippedForMinRevCount)
            print("Total skipped for val count: ", skippedForMinValImpactCount)
            print("Total skipped for val project count: ", skippedForMinValProjectCount)
            print("Total skipped for val revision count: ", skippedForMinValRevCount)
            print("Total row added: ", totalRowAdded)

            print('Co-intrdouction Likelihood: ', (coAdded/grandFrequency))
            print('Later introduced Likelihood: ', (laterAdded / grandFrequency))
            print('Later modified Likelihood: ', (laterModified / grandFrequency))
            print('Later deleted Likelihood: ', (laterDeleted / grandFrequency))

if __name__ == "__main__":
    setDirectory()
    for k in range(len(kinds)):
        setGlobal(filterFlag=True, skipRowFlag=True, dir='', timeFlag=False, slot=0, changeKindIndex=k, debug=True, justTimedMode=False)
        mainFun()