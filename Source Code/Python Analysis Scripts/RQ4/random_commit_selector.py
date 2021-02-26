import json
import os
import random
import csv
import pandas as pd
from util.common import *
from secrets import randbelow

SAMPLE_SIZE_SELECTION_MODE='Manual'

if SAMPLE_SIZE_SELECTION_MODE=='Auto':
  SAMPLE_SIZE=5 #2 percent from each category
else:
  SAMPLE_SIZE={}
  SAMPLE_SIZE['temporal']=250
  SAMPLE_SIZE['activation']=50
  SAMPLE_SIZE['convolutional']=220
  SAMPLE_SIZE['dropout']=100
  SAMPLE_SIZE['enhancement']=50
  SAMPLE_SIZE['initializer']=50
  SAMPLE_SIZE['linear']=100
  SAMPLE_SIZE['merging']=50
  SAMPLE_SIZE['normalization']=50
  SAMPLE_SIZE['pooling']=100
  SAMPLE_SIZE['sparse']=50
  SAMPLE_SIZE['reshaping']=100
  SAMPLE_SIZE['weight regularizer']=50
  SAMPLE_SIZE['training']=250
  SAMPLE_SIZE['pretrained']=50
  SAMPLE_SIZE['prediction and evaluation'] = 60



SAMPLE_ID={}
inpuFile = 'rq1_merged_change_kind_intact_timed'

current_dir = os.getcwd()
root_dir = os.path.dirname(current_dir)

file = os.path.join(root_dir, "merge", "merge_result", inpuFile + ".csv")

out=open(os.path.join(current_dir,"result", "all_commit_sample_2.csv"), "w")


unique=set()
data={}
with open(file, 'r') as input:
  reader = csv.reader(input)
  col = next(reader)
  idx=-1
  for line in reader:
    projectName = line[0].strip()
    revisionId = line[1].strip()
    type = clean(line[7], True, True)
    idx += 1
    if (projectName,revisionId) in unique:
      continue
    if type not in data:
      data[type]=set()
    data[type].add((projectName,revisionId))
    unique.add((projectName,revisionId))

totalSample=0
for type in data.keys():
  print(type+': '+str(len(data[type])))

  if type not in SAMPLE_SIZE:
    continue
  SAMPLE_ID[type]=list()
  ln=len(data[type])
  sampleSize=0
  if SAMPLE_SIZE_SELECTION_MODE == 'Auto':
    sampleSize=int(ln*(SAMPLE_SIZE/100))
  else:
    sampleSize=SAMPLE_SIZE[type]
  totalSample+=sampleSize
  print('Sample size for '+type+': '+str(sampleSize))
  for i in range(sampleSize):
    while True:
      tmp=randbelow(ln)
      if tmp in SAMPLE_ID[type]:
        continue
      SAMPLE_ID[type].append(tmp)
      break

print(totalSample)
print(SAMPLE_ID)

totalAdded=0
out.write('Project Name,Revesion ID,Type\n')
for type in data.keys():
  ln=len(data[type])
  idx=-1
  for (projectName,revisionId) in data[type]:
   idx += 1
   if idx not in SAMPLE_ID[type]:
     continue
   out.write(projectName+','+revisionId+','+type+'\n')
   totalAdded+=1


out.close()
print(totalAdded)

