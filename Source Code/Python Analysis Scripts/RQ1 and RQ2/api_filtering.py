import os
import csv
from collections import defaultdict
from scipy.stats import gmean
from util.common import *

doFilter=True
skipRowIfKeyNotPrensent=True
kinds=['MODIFIED', 'ADDED', 'DELETED']
library='any'

leftData=defaultdict(list)
direct_change_data={}

DEBUG=None
kind='MODIFIED'

leftFileName='api_usage_all'
rightFileName='rq1_merged_change_kind_intact'
statementChangeFile='statement_changed'

current_dir=None
root_dir=None
left=None
input_file=None
statement_file=None
out=None

leftKeyColumn=0
leftCopyColumn=1

rightKeyColumn=1
rightCopyColumn='all'

def setDirectory(rootDir=os.path.dirname(os.getcwd())):
    global current_dir, root_dir
    baseName='rq1_processing'
    current_dir=os.path.join(rootDir, baseName)
    root_dir = rootDir

def setGlobal(filterFlag=True,skipRowFlag=True,dir='',timeFlag=False,slot=0,changeKindIndex=0,debug=True, lib='any'):
    global doFilter,skipRowIfKeyNotPrensent,direction,TIMED_MODE,TIME_SLOT,kind,rightFileName,input_file,out,DEBUG,leftFileName,left
    global leftData,library,statement_file,statementChangeFile,direct_change_data

    DEBUG=debug
    library=lib
    doFilter=filterFlag
    skipRowIfKeyNotPrensent=skipRowFlag
    direction=dir
    TIMED_MODE=timeFlag
    TIME_SLOT=slot
    kind=kinds[changeKindIndex]
    rightFileName = 'rq1_merged_change_kind_intact'
    if direction == 'added':
        rightFileName = 'rq1_merged' + '_added'
    if TIMED_MODE:
        rightFileName += "_timed"

    left = os.path.join(root_dir, "boa_output_processing", "processed_data", leftFileName + ".csv")
    input_file=os.path.join(root_dir, "boa_output_processing", "processed_data", rightFileName+".csv")
    statement_file=os.path.join(root_dir, "boa_output_processing", "processed_data", statementChangeFile+".csv")
    if direction == 'added':
        out = open(
            os.path.join(current_dir, "processed_result", "api_" + direction + "_project_support_" + kind + ".csv"),
            "w")
    else:
        out = open(
            os.path.join(current_dir, "processed_result", "api_project_support_" + kind + ".csv"), "w")

    with open(left, 'r') as input:
        reader=csv.reader(input)
        next(reader)
        for line in reader:
            if line[leftKeyColumn]=='' or line[leftKeyColumn]==None:
                continue
            leftData[clean(line[leftKeyColumn],False,True,False)]=line

    with open(statement_file, 'r') as input:
        reader=csv.reader(input)
        next(reader)
        for line in reader:
            projectName=line[0].strip()
            revId=line[1].strip()
            numChange=int(line[2].strip())
            if projectName not in direct_change_data:
                direct_change_data[projectName]={}
            direct_change_data[projectName][revId]=numChange

def getLeftLine(layerApi):
    global leftData
    if layerApi in leftData:
        return leftData[layerApi]
    return ''

def calculateImpact(apiName, api_count, revision_set, all_revision_set):
    global doFilter
    totalCount=0
    revisionCount=0

    for projectName,revisionId in revision_set[apiName]:
        totalCount+=api_count[projectName][revisionId]
        revisionCount+=1
    revSup = (revisionCount / len(all_revision_set)) * 100.0
    if doFilter:
        if revSup<0.01:
            return None

    impact=totalCount/revisionCount
    return impact,revSup

def calculateAvgDirectChange(apiName, api_count, revision_set, all_revision_set):
    global doFilter,direct_change_data
    totalCount=0
    revisionCount=0

    for projectName,revisionId in revision_set[apiName]:
        if projectName in direct_change_data and revisionId in direct_change_data[projectName]:
            totalCount+=direct_change_data[projectName][revisionId]
            revisionCount+=1
    revSup = (revisionCount / len(all_revision_set)) * 100.0
    if doFilter:
        if revSup<0.01:
            return None

    impact=totalCount/revisionCount
    return impact,revSup


def mainFun():
    global doFilter, skipRowIfKeyNotPrensent, direction, TIMED_MODE, TIME_SLOT, kind, rightFileName, input_file, out, DEBUG, leftFileName, left
    global leftData,library,direct_change_data

    grandFrequency=0
    grandUsage=0

    with open(input_file, 'r') as input:
        reader=csv.reader(input)
        next(reader)

        frequency_aggregator_impact={}
        frequency_aggregator_project = defaultdict(set)
        api_count={}
        revision_set={}
        all_revision_set=set()
        all_revision_kind_wise={}

        all_projects=set()
        tf_projects=set()
        keras_projects=set()
        torch_projects=set()

        out.write("Library,API Name,Project Support,Change Frequency,G-mean,Likelihood,Impact,Work,Usage Frequency,"
                  "Revision Support,Change Likelihood,Change Work,Average Statement Change\n")
        for line in reader:
            if line[0]==None or line[0]=="" or line[1]==None or line[1]=="" or line[2]==None or line[2]=="":
                continue

            projectName=line[0].strip()
            revisionId = line[1].strip()
            libName = line[2].strip()
            apiName = line[3].strip()
            changekind = line[4].strip()
            impactCount = line[5].strip()

            if library!='any' and getLibName(apiName)!=library:
                continue
            if TIMED_MODE:
                timeSlot = int(line[6].strip())

                if timeSlot!=TIME_SLOT:
                    continue


            if apiName not in revision_set:
                revision_set[apiName] = set()

            if projectName not in api_count:
                api_count[projectName] = {}
            if revisionId not in api_count[projectName]:
                api_count[projectName][revisionId] = 0

            api_count[projectName][revisionId] += int(impactCount)

            revision_set[apiName].add((projectName,revisionId))
            all_revision_set.add((projectName,revisionId))

            if changekind not in all_revision_kind_wise:
                all_revision_kind_wise[changekind]=set()
            all_revision_kind_wise[changekind].add((projectName,revisionId))

            grandFrequency+=int(impactCount)

            leftLine = getLeftLine(clean(apiName, False, True, False))

            if leftLine != '':
                grandUsage += float(leftLine[leftCopyColumn])

            if kind == 'MODIFIED' and (changekind == 'ADDED' or changekind == 'DELETED'):
                continue

            if kind != 'MODIFIED' and changekind != kind:
               continue

            if libName not in frequency_aggregator_impact:
                frequency_aggregator_impact[libName]={}

            if apiName not in frequency_aggregator_impact[libName]:
                frequency_aggregator_impact[libName][apiName]=0

            frequency_aggregator_impact[libName][apiName]+=int(impactCount)

            if libName not in frequency_aggregator_project:
                frequency_aggregator_project[libName]={}
            if apiName not in frequency_aggregator_project[libName]:
                frequency_aggregator_project[libName][apiName]=set()

            frequency_aggregator_project[libName][apiName].add(projectName)

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
        totalUsage=0
        totalImpact=0
        totalWork=0
        totalChaneWork=0
        totalRowAdded = 0
        totalDirectChange=0
        for libName in frequency_aggregator_impact.keys():
            for apiName in frequency_aggregator_impact[libName].keys():
                impactCount = frequency_aggregator_impact[libName][apiName]
                pCount = len(frequency_aggregator_project[libName][apiName])
                # overall_support=(pCount/float(len(all_projects)))*100.0

                lib_support = 0.0

                if libName=="keras":
                    lib_support = (pCount / float(len(keras_projects))) * 100.0
                if libName=="tensorflow":
                    lib_support = (pCount / float(len(tf_projects))) * 100.0
                if libName == "torch":
                    lib_support = (pCount / float(len(torch_projects))) * 100.0

                gman=gmean([lib_support,impactCount])

                if doFilter:
                    if gman < 1 or lib_support < 0.1:
                        skipCount+=1
                        continue

                leftLine = getLeftLine(clean(apiName, False, True, False))

                if leftLine == '':
                    if (skipRowIfKeyNotPrensent):
                        skipCount += 1
                        continue
                usageFrequency = float(leftLine[leftCopyColumn])
                liklihood = impactCount / usageFrequency
                try:
                    impact, revSupport=calculateImpact(apiName, api_count, revision_set, all_revision_set)
                    avgDirectChange, revSupport = calculateAvgDirectChange(apiName, api_count, revision_set, all_revision_set)
                except:
                    skipCount+=1
                    continue
                work=liklihood*avgDirectChange

                totalFrequency+=impactCount
                totalUsage+=usageFrequency
                totalWork+=work
                totalImpact+=impact
                totalDirectChange+=avgDirectChange

                changeLikelihood=impactCount/grandFrequency
                changeWork=changeLikelihood*avgDirectChange

                totalChaneWork+=changeWork

                totalRowAdded += 1
                out.write(libName + "," + apiName + "," + str(lib_support) + ',' + str(impactCount) +","
                          +str(gman)+','+str(liklihood)+
                          ','+str(impact)+','+str(work)+','+str(usageFrequency)+','+str(revSupport)+','
                          +str(changeLikelihood)+','+str(changeWork)+','+str(avgDirectChange)+"\n")
        out.close()

        if DEBUG:
            print("Total row added: ", totalRowAdded, kind, skipCount)

            # overallImpact=grandFrequency/len(all_revision_set)
            # overallLikelihood=grandFrequency/grandUsage
            # overallWork=overallImpact*overallLikelihood
            #
            # print("Overall Likelihood: ", overallLikelihood)
            # print("Overall Impact: ", overallImpact)
            # print("Overall Work: ", overallWork)

            overallKindImpact = totalFrequency / len(all_revision_kind_wise[kind])
            overallKindLikelihood = totalFrequency / totalUsage
            # overallKindWork = overallKindImpact * overallKindLikelihood

            print("Overall Kind Likelihood: ", overallKindLikelihood)
            print("Overall Kind Impact: ", overallKindImpact)
            # print("Overall Kind Work: ", overallKindWork)

            overallChangeKindLikelihood = totalFrequency / grandFrequency
            overallChangeKindImpact = totalDirectChange / totalRowAdded

            overallChangeKindWork = overallChangeKindImpact * overallChangeKindLikelihood

            # print("Overall Change Kind Likelihood: ", overallChangeKindLikelihood)
            # print("Overall Change Kind Impact: ", overallKindImpact)
            print("Overall Change Kind Work: ", overallChangeKindWork)

            # print("Overall Change Work: ", totalChaneWork)
            print("Total skipped api: ", skipCount)
            print('Grand Frequency', grandFrequency)

if __name__ == "__main__":
    setDirectory()
    for k in range(len(kinds)):
        print(kinds[k])
        setGlobal(filterFlag=True, skipRowFlag=True, dir='', timeFlag=False, slot=0, changeKindIndex=k, debug=True, lib='any')
        mainFun()