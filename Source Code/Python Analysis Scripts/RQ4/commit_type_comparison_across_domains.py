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
from statistical_test.util import *

COMAPRE_MODE=True
COMPARE='refactor'
# COMPARE='clean'
# COMPARE='resource'
# COMPARE='fix'
# COMPARE='merge'
# COMPARE='enhance'
# COMPARE='test'

DOMAIN='dnn'
TARGET_CATEGORY='Applied'
COMMIT_THRESHOLD=1000
CI_THREHOLD=0.95

leftFileName = 'commit_count_'+DOMAIN
rightFileName = 'all_changed_projects'
mlverseFileName = 'mlverse'

current_dir = os.getcwd()
root_dir = os.path.dirname(current_dir)

left = None
right =None
mlverse = None

DEBUG=True

def setGlobal(_domain='dnn',commitThres=1000,ciThres=0.95,compareWhat='test',targetCat='Applied', debug=True):
  global mlverse_data, left, right, mlverse, DOMAIN, TARGET_CATEGORY, COMAPRE_MODE, COMMIT_THRESHOLD, CI_THREHOLD, COMPARE
  global leftFileName, rightFileName, mlverseFileName, current_dir, root_dir,DEBUG

  DEBUG=debug
  COMPARE=compareWhat
  DOMAIN = _domain
  TARGET_CATEGORY = 'Applied'
  COMMIT_THRESHOLD = commitThres
  CI_THREHOLD = ciThres
  TARGET_CATEGORY=targetCat

  leftFileName = 'commit_count_' + DOMAIN
  # rightFileName = 'all_changed_projects'
  rightFileName = 'rq1_merged_change_kind_intact_timed'
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
  global mlverse_data,left,right,mlverse,DOMAIN,TARGET_CATEGORY,COMAPRE_MODE,COMMIT_THRESHOLD,CI_THREHOLD,COMPARE
  global  leftFileName,rightFileName,mlverseFileName,current_dir,root_dir,DEBUG

  totalTestCount = 0
  totalFixCount = 0
  totalRefactorCount = 0
  totalCleanupCount = 0
  totalCount = 0
  totalResourceCount = 0
  totalEnhanceCount = 0
  totalMergeCount = 0
  totalProject = 0
  grandProject=0


  test_rate = []
  fix_rate = []
  refactor_rate = []
  merge_rate = []
  enhance_rate = []
  resource_rate = []
  clean_rate = []

  left_data={}
  with open(left, 'r') as input:
    reader = csv.reader(input)
    col = next(reader)
    for line in reader:
      projectName = line[0].strip()
      testCount = int(line[1].strip())
      refactorCount = int(line[2].strip())
      cleanupCount = int(line[3].strip())
      fixCount = int(line[4].strip())
      resourceCount = int(line[5].strip())
      mergeCount = int(line[6].strip())
      enhanceCount = int(line[7].strip())
      totalCountTemp = int(line[8].strip())

      left_data[projectName]=(testCount,refactorCount,cleanupCount,fixCount,resourceCount,mergeCount,enhanceCount,totalCountTemp)

      grandProject+=1

      if DOMAIN!='dnn':
        if left_data[projectName][7] < COMMIT_THRESHOLD:
          continue

        totalTestCount+=left_data[projectName][0]
        totalRefactorCount += left_data[projectName][1]
        totalCleanupCount += left_data[projectName][2]
        totalFixCount += left_data[projectName][3]
        totalResourceCount += left_data[projectName][4]
        totalMergeCount += left_data[projectName][5]
        totalEnhanceCount += left_data[projectName][6]
        totalCount += left_data[projectName][7]
        totalProject+=1

        test_rate.append((left_data[projectName][0]/left_data[projectName][7])*100.0)
        refactor_rate.append((left_data[projectName][1] / left_data[projectName][7]) * 100.0)
        clean_rate.append((left_data[projectName][2] / left_data[projectName][7]) * 100.0)
        fix_rate.append((left_data[projectName][3] / left_data[projectName][7]) * 100.0)
        resource_rate.append((left_data[projectName][4] / left_data[projectName][7]) * 100.0)
        merge_rate.append((left_data[projectName][5] / left_data[projectName][7]) * 100.0)
        enhance_rate.append((left_data[projectName][6] / left_data[projectName][7]) * 100.0)


  if DOMAIN=='dnn':
    already_taken={}
    with open(right, 'r') as input:
      reader = csv.reader(input)
      col = next(reader)
      for line in reader:
        projectName = line[0].strip()

        if projectName in already_taken:
          continue
        already_taken[projectName]=True
        if projectName not in left_data:
          continue
        if TARGET_CATEGORY!='any':
          if projectName not in mlverse_data:
            continue
          if mlverse_data[projectName]!=TARGET_CATEGORY:
            continue
        if left_data[projectName][7]<COMMIT_THRESHOLD:
          continue
        totalTestCount+=left_data[projectName][0]
        totalRefactorCount += left_data[projectName][1]
        totalCleanupCount += left_data[projectName][2]
        totalFixCount += left_data[projectName][3]
        totalResourceCount += left_data[projectName][4]
        totalMergeCount += left_data[projectName][5]
        totalEnhanceCount += left_data[projectName][6]
        totalCount += left_data[projectName][7]
        totalProject+=1

        if (left_data[projectName][1] / left_data[projectName][7]) * 100.0>70:
          print(projectName)
        test_rate.append((left_data[projectName][0]/left_data[projectName][7])*100.0)
        refactor_rate.append((left_data[projectName][1] / left_data[projectName][7]) * 100.0)
        clean_rate.append((left_data[projectName][2] / left_data[projectName][7]) * 100.0)
        fix_rate.append((left_data[projectName][3] / left_data[projectName][7]) * 100.0)
        resource_rate.append((left_data[projectName][4] / left_data[projectName][7]) * 100.0)
        merge_rate.append((left_data[projectName][5] / left_data[projectName][7]) * 100.0)
        enhance_rate.append((left_data[projectName][6] / left_data[projectName][7]) * 100.0)


  testPercentage=(totalTestCount/totalCount)*100.0
  refactorPercentage=(totalRefactorCount/totalCount)*100.0
  cleanupPercentage=(totalCleanupCount/totalCount)*100.0
  fixPercentage=(totalFixCount/totalCount)*100.0
  resourcePercentage=(totalResourceCount/totalCount)*100.0
  mergePercentage=(totalMergeCount/totalCount)*100.0
  enhancePercentage=(totalEnhanceCount/totalCount)*100.0

  # df=pd.DataFrame({
  #   'Test': test_rate,
  #   # 'refactor': refactor_rate
  # })
  # sns_plot=sns.boxplot(x="variable", y="value", data=pd.melt(df))
  # plt.grid(True)
  # plt.show()
  # sns_plot.get_figure().savefig(os.path.join(current_dir, 'result', DOMAIN+'.png'))

  print('total commit,total project,grand project', totalCount,totalProject,grandProject)
  if DEBUG:
    print('Total Test Percentage: ', testPercentage)
    print('Total refactor Percentage: ', refactorPercentage)
    print('Total cleanup Percentage: ', cleanupPercentage)
    print('Total fix Percentage: ', fixPercentage)
    print('Total resource Percentage: ', resourcePercentage)
    print('Total merge Percentage: ', mergePercentage)
    print('Total enhance Percentage: ', enhancePercentage)

    print('CI for test: ', getConfidenInterval(test_rate,CI_THREHOLD))
    print('CI for refactor: ', getConfidenInterval(refactor_rate,CI_THREHOLD))
    print('CI for cleanup: ', getConfidenInterval(clean_rate,CI_THREHOLD))
    print('CI for fix: ', getConfidenInterval(fix_rate,CI_THREHOLD))
    print('CI for resoure: ', getConfidenInterval(resource_rate,CI_THREHOLD))
    print('CI for merge: ', getConfidenInterval(merge_rate,CI_THREHOLD))
    print('CI for enhance: ', getConfidenInterval(enhance_rate,CI_THREHOLD))

  if COMPARE=='test':
    return test_rate
  if COMPARE == 'refactor':
    return refactor_rate
  if COMPARE == 'resource':
    return resource_rate
  if COMPARE == 'fix':
    return fix_rate
  if COMPARE == 'clean':
    return clean_rate
  if COMPARE == 'merge':
    return merge_rate
  if COMPARE == 'enhance':
    return enhance_rate

if __name__ == "__main__":

  if COMAPRE_MODE:
    df=pd.DataFrame()
    testData=[]
    for _t in ['dnn','ds','java']:
      if _t=='dnn':
        comT=1110
        # comT=549 #100
        comT=0
      elif _t=='java':
        comT=500
      else:
        # comT=2850 #50
        # comT=8700 #50
        comT=50 #100
      # comT=0
      setGlobal(_domain=_t,commitThres=comT,ciThres=0.95,compareWhat=COMPARE,targetCat='any', debug=True)
      a=mainFun()
      tmp=COMPARE
      if tmp=='enhance':
        tmp='Feature'
      if tmp=='fix':
        tmp='Bug Fix'
      df[tmp.capitalize()+' ('+_t.upper()+')']=pd.Series(a)
      testData.append(a)

    stat, p, wht=kruskalTest(testData, 0.01)
    stat, p, wht = mannWhitneyU(testData[0],testData[2], 0.01)
    print(stat,p,wht)
    sns_plot = sns.boxplot(x="variable", y="value", data=pd.melt(df), showfliers=False)
    plt.grid(True)
    plt.xlabel('Dataset Type')
    plt.ylabel('Activity Rate')
    plt.show()
    sns_plot.get_figure().savefig(os.path.join(current_dir, 'result',   'compare_'+COMPARE+'.png'))
