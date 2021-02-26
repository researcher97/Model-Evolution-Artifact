import os
import csv
from collections import defaultdict
from util.common import *

leftFileName='commit_labeled_api_type_filled'

current_dir=os.getcwd()
root_dir=os.path.dirname(current_dir)

left=os.path.join(current_dir, "data", leftFileName+".csv")

out=open(os.path.join(current_dir, "result", "api_type_wise_subtype_result.csv"), "w")

commit_types=set()
grandTotal=0
fre={}
with open(left, 'r') as input:
    reader=csv.reader(input)
    col=next(reader)
    for line in reader:
        projectName=clean(line[0], False)
        revisionId = clean(line[1], False)
        apiType=clean(line[2], False)
        commitType = clean(line[3], False)

        if apiType not in fre:
            fre[apiType] = {}
        if commitType not in fre[apiType]:
          fre[apiType][commitType] = 0

        fre[apiType][commitType]+=1
        grandTotal+=1
        commit_types.add(commitType)

api_count={}
commit_types=list(commit_types)
out.write('Type,'+','.join(commit_types)+'\n')
for apiType in fre.keys():
    total=0
    for commitType in fre[apiType].keys():
        total += fre[apiType][commitType]
    vals = {}
    api_count[apiType]=total

    for commitType in fre[apiType].keys():
        val=fre[apiType][commitType]
        nW=(val/total)*100.0
        nG=(val/grandTotal)*100.0
        vals[commitType] = str(nW)
        # out.write(apiType+','+commitType+','+str(val)+','+str(nW)+','+str(nG)+'\n')
    out.write(apiType)
    for commitType in commit_types:
        if commitType not in vals:
            vals[commitType]='0'
        out.write(',' + vals[commitType])
    out.write('\n')
out.close()

print(api_count)