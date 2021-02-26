import json
import os
import random
import csv
import pandas as pd
from util.common import *
from secrets import randbelow
from statistical_test.util import *
import seaborn as sns
import matplotlib.pyplot as plt

COMAPRE_MODE=True

DOMAIN='dnn'
TARGET_CATEGORY='Applied'
COMMIT_THRESHOLD=1000
CI_THREHOLD=0.95

leftFileName = 'dnn_test'
rightFileName = 'all_changed_projects'
mlverseFileName = 'mlverse'

current_dir = os.getcwd()
root_dir = os.path.dirname(current_dir)

left = os.path.join(root_dir, "boa_output_processing", "processed_data", leftFileName + ".csv")
right = os.path.join(root_dir, "boa_output_processing", "processed_data", rightFileName + ".csv")
mlverse = os.path.join(root_dir, "boa_output_processing", "processed_data", mlverseFileName + ".csv")
out=None

def setGlobal(_domain='dnn',commitThres=1000,ciThres=0.95,targetCat='Applied', debug=True):
  global mlverse_data, left, right, mlverse, DOMAIN, TARGET_CATEGORY, COMAPRE_MODE, COMMIT_THRESHOLD, CI_THREHOLD
  global leftFileName, rightFileName, mlverseFileName, current_dir, root_dir,DEBUG,out

  DEBUG=debug
  DOMAIN = _domain
  TARGET_CATEGORY = 'Applied'
  COMMIT_THRESHOLD = commitThres
  CI_THREHOLD = ciThres
  TARGET_CATEGORY=targetCat

  leftFileName = DOMAIN+'_test'
  rightFileName = 'all_changed_projects'
  mlverseFileName = 'mlverse'

  left = os.path.join(root_dir, "boa_output_processing", "processed_data", leftFileName + ".csv")
  right = os.path.join(root_dir, "boa_output_processing", "processed_data", rightFileName + ".csv")
  # right = os.path.join(root_dir, "merge", "merge_result", rightFileName + ".csv")
  mlverse = os.path.join(root_dir, "boa_output_processing", "processed_data", mlverseFileName + ".csv")

  mlverse_data={}
  with open(mlverse, 'r') as input:
    reader = csv.reader(input)
    col = next(reader)
    for line in reader:
      projectName = line[2].strip()
      category = line[0].strip()
      mlverse_data[projectName]=category


def mainFun():
  global mlverse_data, left, right, mlverse, DOMAIN, TARGET_CATEGORY, COMAPRE_MODE, COMMIT_THRESHOLD, CI_THREHOLD
  global leftFileName, rightFileName, mlverseFileName, current_dir, root_dir, DEBUG,out

  totalTestCount=0
  totalCount=0
  left_data={}
  totalProject = 0
  test_rate=[]
  grandProject =0
  hasTestProject=0

  with open(left, 'r') as input:
    reader = csv.reader(input)
    col = next(reader)
    for line in reader:
      projectName = line[0].strip()
      testCount = int(line[1].strip())
      totalCountTemp = int(line[2].strip())
      grandProject += 1
      left_data[projectName]=(testCount,totalCountTemp)
      if DOMAIN!='dnn':
        totalTestCount += left_data[projectName][0]
        totalCount += left_data[projectName][1]
        test_rate.append((left_data[projectName][0] / left_data[projectName][1]) * 100.0)
        totalProject += 1
        if left_data[projectName][0]>0:
          hasTestProject+=1


  if DOMAIN=='dnn':
    with open(right, 'r') as input:
      reader = csv.reader(input)
      col = next(reader)
      for line in reader:
        projectName = line[0].strip()
        if projectName in left_data:
          if TARGET_CATEGORY != 'any':
            if projectName not in mlverse_data:
              continue
            if mlverse_data[projectName] != TARGET_CATEGORY:
              continue

          totalTestCount+=left_data[projectName][0]
          totalCount += left_data[projectName][1]
          test_rate.append((left_data[projectName][0] / left_data[projectName][1]) * 100.0)
          totalProject += 1
          if left_data[projectName][0] > 0:
            hasTestProject += 1

  testPercentage=(totalTestCount/totalCount)*100.0
  testProjectPercentage=(hasTestProject/totalProject)*100.0

  print('total test,total file,total project', totalTestCount,totalCount, totalProject)
  print('Total Test Percentage: ', testPercentage)
  print('Total Test Project Percentage: ', testProjectPercentage)
  out.write(DOMAIN+','+str(totalTestCount)+','+str(totalCount)+','+str(testPercentage)+','+str(testProjectPercentage)+'\n')


  return test_rate

if __name__ == "__main__":
  out = open(os.path.join(current_dir, "result", "test_file_comparison_stat.csv"), "w")
  out.write('Dataset,Total Test File,Total File,Test File Percentage,Total Project having test Percentage\n')

  if COMAPRE_MODE:
    df=pd.DataFrame()
    for _t in ['dnn','java']:
      if _t=='dnn':
        # comT=1110
        comT=549 #100
      else:
        comT=7590 #100
      comT=500
      setGlobal(_domain=_t,commitThres=comT,ciThres=0.95,targetCat='any', debug=False)
      a=mainFun()
      df['Test File' +'('+_t+')']=pd.Series(a)

    sns_plot = sns.boxplot(x="variable", y="value", data=pd.melt(df))
    plt.grid(True)
    plt.show()
    sns_plot.get_figure().savefig(os.path.join(current_dir, 'result',   'compare_test_file.png'))
  out.close()