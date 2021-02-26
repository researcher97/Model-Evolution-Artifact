import json
import os
import random
import csv
import pandas as pd
from util.common import *
from util.automate_all import *
from statistical_test.util import *

LAYER='layer_label'

TIME_SLOT=4
# TARGET='frequency'
TARGET='likelihood'
RETRUN_KIND='modified'
# RETRUN_KIND='added'
# RETRUN_KIND='deleted'

current_dir = os.getcwd()
root_dir = os.path.dirname(current_dir)
baseFileName = 'layer_base_api'+'_'+RETRUN_KIND
baseFile = os.path.join(current_dir, "input", baseFileName + ".csv")

base_data={}
with open(baseFile, 'r') as input:
  reader = csv.reader(input)
  next(reader)
  for line in reader:
    category=clean(line[0], False)
    val = float(line[1].strip())
    base_data[category]=val

base_data={k:v for k,v in sorted(base_data.items(), key=lambda item: item[0])}
# base_data=normalizeWithin(base_data)

distribute_out = open(os.path.join(current_dir, "result", 'distribution_'+LAYER+'_'+TARGET +'_' +RETRUN_KIND+".csv"), "w")
distribute_out.write('Time Slot,Type\n')

slot_data=list()
for slotNo in range(TIME_SLOT):
    calculateApiSupport(filterFlag=False,skipRowFlag=True,dir='',timeFlag=True,slot=slotNo)
    labelApi(lftFName=LAYER, lftKeyColumn=[1], filterFlag=False, skiRowFlag=True, skipUsage=False, debug=False)
    modified_stats=analyzeAPi(return_data_type=RETRUN_KIND, trgt=TARGET, multiplyFactor=None,
                              toPercenet=True, normalizeGlobal=True)
    modified_stats={k:v for k,v in sorted(modified_stats.items(), key=lambda item: item[0])}
    modified_stats_temp={}
    for k in modified_stats.keys():
        if k in base_data:
            modified_stats_temp[k]=modified_stats[k]

    modified_stats=modified_stats_temp
    for k in base_data.keys():
        if k not in modified_stats:
            modified_stats[k]=0.0

    # modified_stats=normalizeWithin(modified_stats)

    stat,p,what=mannWhitneyU(list(base_data.values()),list(modified_stats.values()))

    # sorted_modified_stats={k:v for k,v in sorted(modified_stats.items(), key=lambda item: item[1], reverse=True)}
    print('Slot: '+str(slotNo+1)+', '+what)
    print(modified_stats)

    # out = open(os.path.join(current_dir, "result", LAYER+'_'+TARGET+'_'+str(slotNo) + ".csv"), "w")
    # out.write('Type,'+TARGET.capitalize()+'\n')
    # for k in sorted_modified_stats.keys():
    #     out.write(k+','+str(sorted_modified_stats[k])+'\n')
    # out.close()

    slot_data.append(modified_stats)

    distribute_out.write(str(slotNo)+','+what+'\n')
    base_data=modified_stats

out = open(os.path.join(current_dir, "result", LAYER+'_'+TARGET +'_'+RETRUN_KIND+ ".csv"), "w")

titles=['First Quarter','Second Quarter','Third Quarter','Fourth Quarter']
out.write('Type')
for slotNo in range(TIME_SLOT):
    out.write(','+titles[slotNo])
out.write('\n')
for k in base_data.keys():
    out.write(k)
    for slotNo in range(TIME_SLOT):
        out.write(','+str(slot_data[slotNo][k])+'%')
    out.write('\n')
out.close()
distribute_out.close()

