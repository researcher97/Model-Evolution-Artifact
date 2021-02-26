import os
import csv
from collections import defaultdict
from util.common import *

ENABLE_PARAM_FILETR=True

LAYER_WISE=False

rightFileName='rq2param_filtered_by_rq1'
paramLabelFileName='default_param'

current_dir=os.getcwd()
root_dir=os.path.dirname(current_dir)
right=os.path.join(root_dir, "merge","merge_result", rightFileName+".csv")
paramLabelFile=os.path.join(root_dir, "merge","merge_from", paramLabelFileName+".csv")

out=open(os.path.join(current_dir, "processed_result", "api_change_kind_parent_change_kind_likelihood.csv"), "w")

rightKeyColumn=2
rightSubKeyColumn=3
apiChangeKindColumn=7
paramChangeKindColumn=5
typeColumn=8
impactcolumn=6

paramLabelData={}

def apiMatcher(apiName,paramId):
    global paramLabelData
    for p in paramLabelData.keys():
        if re.match(p, apiName)!=None:
            if paramId in paramLabelData[p]:
                return paramLabelData[p][paramId]
            if '' in paramLabelData[p]:
                return paramLabelData[p]['']

    return None

if ENABLE_PARAM_FILETR:
    with open(paramLabelFile, 'r') as input:
        reader = csv.reader(input)
        col = next(reader)
        for line in reader:
            apiName = convertToPythonRegex(clean(line[1]))
            paramId = clean(line[2])
            if apiName not in paramLabelData:
                paramLabelData[apiName] = {}
            if paramId not in paramLabelData[apiName]:
                paramLabelData[apiName][paramId] = line
fre={}
fre_all={}
with open(right, 'r') as input:
    reader=csv.reader(input)
    col=next(reader)
    if LAYER_WISE:
        out.write('Type,API Change Kind,Parameter Change Kind,Likelihood\n')
    else:
        out.write('API Change Kind,Parameter Change Kind,Likelihood\n')

    for line in reader:

        apiName = clean(line[rightKeyColumn])
        paramId = clean(line[rightSubKeyColumn])
        apiChange = clean(line[apiChangeKindColumn])
        paramChange = clean(line[paramChangeKindColumn])
        type = clean(line[typeColumn])
        val = int(clean(line[impactcolumn]))

        if apiChange=='':
            continue

        if ENABLE_PARAM_FILETR:
            leftLine=apiMatcher(apiName, paramId)
            if leftLine == None:
                continue

        if LAYER_WISE:
            if type not in fre:
                fre[type]={}
                fre_all[type]=0
            if apiChange not in fre[type]:
                fre[type][apiChange]={}

            if paramChange not in fre[type][apiChange]:
                fre[type][apiChange][paramChange]=0

            fre[type][apiChange][paramChange] +=val
            fre_all[type]+=val
        else:
            if apiChange not in fre:
                fre[apiChange] = {}
                fre_all=0

            if paramChange not in fre[apiChange]:
                fre[apiChange][paramChange] = 0

            fre[apiChange][paramChange] += val
            fre_all += val

    print(fre)
    print(fre_all)

    if LAYER_WISE:
        for typ in fre.keys():
            for apiChange in fre[typ].keys():
                for paramChange in fre[typ][apiChange].keys():
                    val=(fre[typ][apiChange][paramChange]/fre_all[typ])*100.0
                    out.write(typ+','+apiChange+','+paramChange+','+str(val)+'\n')
    else:
        for apiChange in fre.keys():
            for paramChange in fre[apiChange].keys():
                val = (fre[apiChange][paramChange] / fre_all) * 100.0
                out.write( apiChange + ',' + paramChange + ',' + str(val) + '\n')

    out.close()

