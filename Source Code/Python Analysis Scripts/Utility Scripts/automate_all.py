from rq2_processing import param_project_support_change_type as pst
from rq2_processing import analysis as rq2analysis
from rq1_processing import analysis as rq1analysis
from merge import merger_rq2_change_type as rq2label
from merge import merger_rq1_labled_data as rq1label
import os
from rq1_processing import api_project_support_change_type as ast

def calculateApiSupport(filterFlag=True,skipRowFlag=True,dir='',timeFlag=False,slot=0, debug=False):
    print('Calculating api support...')
    ast.setDirectory(os.path.dirname(os.getcwd()))
    for k in range(len(ast.kinds)):
        ast.setGlobal(filterFlag, skipRowFlag, dir, timeFlag, slot, k,debug=debug)
        ast.mainFun()

    print('Done calculation of api support')

def calculateParamSupport(filterFlag=True,skipRowFlag=True,dir='',timeFlag=False,slot=0, debug=False):
    print('Calculating parameter support...')
    pst.setDirectory(os.path.dirname(os.getcwd()))
    for k in range(len(pst.kinds)):
        pst.setGlobal(filterFlag, skipRowFlag, dir, timeFlag, slot, k,debug=debug)
        pst.mainFun()

    print('Done calculation of param support')


def labelApi(lftFName='',filterFlag=False,skiRowFlag=True,lftKeyColumn=[1],lftCopyColumn=[2],debug=False, skipUsage=False):
    print('Labeling api...')
    rq1label.setDirectory()
    for k in range(len(rq1label.kinds)):
        if rq1label.kinds[k].startswith('rq1'):
            continue
        umode=False
        if rq1label.kinds[k].startswith('api_usage'):
            umode=True
            if skipUsage:
                continue
        rq1label.setGlobal(lftFName=lftFName,rightFNameIndex=k, filterFlag=filterFlag, skiRowFlag=skiRowFlag, useMode=umode,
                  lftKeyColumn=lftKeyColumn,lftCopyColumn=lftCopyColumn,debug=debug)
        rq1label.mainFun()
    print('Done api labeling')

def labelParameter(lftFName='',filterFlag=False,skiRowFlag=True,lftKeyColumn=[1,2],lftCopyColumn=[3],debug=False, skipUsage=False):
    print('Labeling parameter...')
    rq2label.setDirectory()
    for k in range(len(rq2label.kinds)):
        if rq2label.kinds[k].startswith('rq2'):
            continue
        umode=False
        if rq2label.kinds[k]=='param_usage':
            umode=True
            if skipUsage:
                continue
        rq2label.setGlobal(lftFName=lftFName,rightFNameIndex=k, filterFlag=filterFlag, skiRowFlag=skiRowFlag, useMode=umode,
                  lftKeyColumn=lftKeyColumn,lftCopyColumn=lftCopyColumn,debug=debug)
        rq2label.mainFun()
    print('Done labeling parameter')

def analyzeAPi(libraryFltr=False, trgt='likelihood', typColumn=13,normalizeGlobal=False, return_data_type='modified',
               debug=False, multiplyFactor=100, toPercenet=False):
    print('Analyzing api')
    rq1analysis.setDirectory()
    left=None
    middle=None
    right=None
    if libraryFltr == False:
        rq1analysis.setGlobal(libraryFltr=False, trgt=trgt, typColumn=typColumn, normalizeGlobal=normalizeGlobal,
                              debug=debug, multiPlyFactor=multiplyFactor, toPercent=toPercenet)
        left,middle,right=rq1analysis.mainFun()

    if libraryFltr:
        for k in range(len(rq1analysis.libs)):
            rq1analysis.setGlobal(libraryFltr=True, targetLibIndex=k, trgt=trgt, typColumn=typColumn,
                                  normalizeGlobal=normalizeGlobal,debug=debug)
            left, middle, right = rq1analysis.mainFun()

    print('Done analyzing api')

    if return_data_type.lower()=='all':
        return left,middle,right
    if return_data_type.lower()=='modified':
        return  left
    if return_data_type.lower()=='added':
        return  middle
    if return_data_type.lower()=='deleted':
        return  right

def analyzeParameter(libraryFltr=False, trgt='likelihood', typColumn=18,normalizeGlobal=False,
                     return_data_type='modified',debug=False, toPercent=False):
    print('Analyzing parameter')
    rq2analysis.setDirectory()
    left=None
    middle=None
    right=None
    if libraryFltr == False:
        rq2analysis.setGlobal(libraryFltr=False, trgt=trgt, typColumn=typColumn,
                              normalizeGlobal=normalizeGlobal,debug=debug, toPercent=toPercent)
        left,middle,right=rq2analysis.mainFun()

    if libraryFltr:
        for k in range(len(rq2analysis.libs)):
            rq2analysis.setGlobal(libraryFltr=True, targetLibIndex=k, trgt=trgt, typColumn=typColumn,
                                  normalizeGlobal=normalizeGlobal,debug=debug)
            left, middle, right = rq2analysis.mainFun()

    print('Done analyzing parameter')

    if return_data_type.lower()=='all':
        return left,middle,right
    if return_data_type.lower()=='modified':
        return  left
    if return_data_type.lower()=='added':
        return  middle
    if return_data_type.lower()=='deleted':
        return  right