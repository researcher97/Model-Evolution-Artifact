import os
import csv
from collections import defaultdict
from util.common import *
import re

leftData=defaultdict(list)


exlude=['keras.applications.mobilenet.depthwiseconv2d']

def normalizeKernelValue(val):
    # for c in val:
    #     if c.isalpha():
    #        return c

    if val.startswith('2'):
        val = '2'
    if val.startswith('3'):
        val = '3'
    if val.startswith('5'):
        val = '5'
    if val.startswith('1'):
        val = '1'
    if val.startswith('7'):
        val = '7'
    if val.startswith('4'):
        val = '4'
    return val
def isNumber(val):
    try:
        val=float(val)
    except:
        return False
    return True


leftFileName='default_param'
rightFileName='param_usage'
apiUsageFile='api_usage'


current_dir=os.getcwd()
root_dir=os.path.dirname(current_dir)
left=os.path.join(root_dir, 'merge',"merge_from", leftFileName+".csv")
right=os.path.join(root_dir, "boa_output_processing", "processed_data", rightFileName+".csv")
apiUsageFile=os.path.join(root_dir, "boa_output_processing", "processed_data", apiUsageFile+".csv")

out1=open(os.path.join(current_dir, "processed_result", "flip_rate_api.csv"), "w")
out2=open(os.path.join(current_dir, "processed_result", "flip_rate_param.csv"), "w")


patterns={}
with open(left, 'r') as input:
    reader=csv.reader(input)
    next(reader)


    for line in reader:
        apiPattern=clean(line[1], True, True, False, False)
        paramId=clean(line[2], True, True)
        val = clean(line[3], True, True, True, False)
        label = clean(line[4], True, True, False)

        apiPattern=apiPattern.split(',')
        for p in apiPattern:
            p=convertToPythonRegex(p)
            if p not in patterns:
                patterns[p]={}
            if paramId not in patterns[p]:
                patterns[p][paramId]={}
            if label not in patterns[p][paramId]:
                patterns[p][paramId][label]={}
            patterns[p][paramId][label]=val


fre={}
fre_param={}

with open(right, 'r') as input:
    reader=csv.reader(input)
    col=next(reader)


    for line in reader:

        apiName=clean(line[0], True, True, False, False)
        paramId = clean(line[1], True, True)
        val = clean(line[2], True, True, True, False)
        useFrequency=float(clean(line[3]))

        targetIndex=apiMatcher(patterns, apiName)
        if targetIndex==None:
            continue
        if paramId not in patterns[targetIndex]:
            continue

        label=list(patterns[targetIndex][paramId].keys())[0]

        if paramId == 'pool_size' or paramId=='atrous_rate':
            val=normalizeKernelValue(val)

        if apiName not in fre:
            fre[apiName]={}
        if paramId not in fre[apiName]:
            fre[apiName][paramId]={}
        if 'Other' not in fre[apiName][paramId]:
            fre[apiName][paramId]['Other'] =0
        if 'Default' not in fre[apiName][paramId]:
            fre[apiName][paramId]['Default'] =0
        if 'Empty' not in fre[apiName][paramId]:
            fre[apiName][paramId]['Empty'] =0

        if paramId not in fre_param:
            fre_param[paramId]={}
        if label not in fre_param[paramId]:
            fre_param[paramId][label]={}

        if 'Other' not in fre_param[paramId][label]:
            fre_param[paramId][label]['Other'] =0
        if 'Default' not in fre_param[paramId][label]:
            fre_param[paramId][label]['Default'] =0
        if 'Empty' not in fre_param[paramId][label]:
            fre_param[paramId][label]['Empty'] =0

        if val=='':
            fre[apiName][paramId]['Empty']+=useFrequency
            fre[apiName][paramId]['Other'] += useFrequency
            fre_param[paramId][label]['Empty'] += useFrequency
            fre_param[paramId][label]['Other'] += useFrequency

        if isNumber(val) and isNumber(patterns[targetIndex][paramId])==False:
            fre[apiName][paramId]['Other']+=useFrequency
            fre_param[paramId][label]['Other'] += useFrequency

        elif isNumber(val):
            val=float(val)
            if val==float(patterns[targetIndex][paramId]):
                fre[apiName][paramId]['Default']+=useFrequency
                fre_param[paramId][label]['Default']+=useFrequency
            else:
                fre[apiName][paramId]['Other'] += useFrequency
                fre_param[paramId][label]['Other'] += useFrequency
        elif val==patterns[targetIndex][paramId]:
            fre[apiName][paramId]['Default'] += useFrequency
            fre_param[paramId][label]['Default'] += useFrequency
        else:
            fre[apiName][paramId]['Other'] += useFrequency
            fre_param[paramId][label]['Other'] += useFrequency


flipRateHigher=0
total=0
jhamela=0
out1.write('API Name,Parameter ID,Default Rate,Flip Rate\n')
with open(apiUsageFile, 'r') as input:
    reader=csv.reader(input)
    next(reader)


    for line in reader:
        apiName=clean(line[0], True, True, False, False)
        useFrequency=float(clean(line[1]))

        if apiName not in fre or useFrequency<20:
            continue

        for paramId in fre[apiName]:
            if fre[apiName][paramId]['Empty']==fre[apiName][paramId]['Other'] and fre[apiName][paramId]['Default']==0:
                continue

            flipPercentage=(fre[apiName][paramId]['Other']/useFrequency)*100.0
            if flipPercentage>100.0:
                jhamela+=1
                continue
            # if flipPercentage==100.0:
            #     continue

            defaultPercentage=100.0-flipPercentage
            total+=1
            if flipPercentage>defaultPercentage:
                flipRateHigher+=1
            out1.write(apiName+','+paramId+','+str(defaultPercentage)+','+str(flipPercentage)+'\n')

out1.close()
overallFlipRate=(flipRateHigher/total)*100.0
print('Overall Flip Rate(API): ', overallFlipRate)
print('Jhamela(API)', jhamela)

flipRateHigher=0
total=0
jhamela=0
api_param={}
out2.write('Label,Parameter ID,Default Rate,Flip Rate\n')
with open(apiUsageFile, 'r') as input:
    reader=csv.reader(input)
    next(reader)


    for line in reader:
        apiName=clean(line[0], True, True, False, False)
        useFrequency=float(clean(line[1]))

        targetIndex = apiMatcher(patterns, apiName)
        if targetIndex == None:
            continue


        # if apiName not in fre or useFrequency < 20:
        #     continue

        for paramId in patterns[targetIndex]:
            label = list(patterns[targetIndex][paramId].keys())[0]

            if paramId=='lr':
                paramId='learning_rate'

            if paramId not in api_param:
                api_param[paramId]={}
            if label not in api_param[paramId]:
                api_param[paramId][label]=0
            api_param[paramId][label]+=useFrequency

fre_param['learning_rate']['training']['Other']=fre_param['lr']['training']['Other']
fre_param['learning_rate']['training']['Empty']=fre_param['lr']['training']['Empty']
fre_param['learning_rate']['training']['Default']=fre_param['lr']['training']['Default']

for paramId in fre_param.keys():
    if paramId == 'lr':
        continue
    if paramId not in api_param:
        continue
    for label in fre_param[paramId].keys():
        if fre_param[paramId][label]['Empty'] == fre_param[paramId][label]['Other'] and \
                fre_param[paramId][label]['Default'] == 0:
            continue

        flipPercentage = (fre_param[paramId][label]['Other'] / api_param[paramId][label]) * 100.0
        if flipPercentage > 100.0:
            jhamela += 1
            continue
        # if flipPercentage==100.0:
        #     continue

        defaultPercentage = 100.0 - flipPercentage
        total += 1
        if flipPercentage > defaultPercentage:
            flipRateHigher += 1
        out2.write(label+','+paramId + ',' + str(defaultPercentage) + ',' + str(flipPercentage) + '\n')

out2.close()

overallFlipRate=(flipRateHigher/total)*100.0
print('Overall Flip Rate(Param): ', overallFlipRate)
print('Jhamela(Param)', jhamela)