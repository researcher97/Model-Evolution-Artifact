import json
import re
import os
import csv
from dateutil import parser
from dateutil import tz

def is_keras_api(api):
    if api.startswith('keras'):
        return True
    return False

def is_tf_api(api):
    if api.startswith('tensorflow'):
        return True
    return False

def is_torch_api(api):
    if api.startswith('torch'):
        return True
    return False

def getLibName(api):
    if is_tf_api(api):
        return 'tensorflow'
    if is_keras_api(api):
        return 'keras'
    if is_torch_api(api):
        return 'torch'
    return ''

def isKerasOrTfKeras(apiName):
    if getLibName(apiName) == 'keras' or re.match('tensorflow\..*keras\..*', apiName) != None:
        return True
    return False

def loadLabel(label, keyColumn=1):
    current_dir = os.getcwd()
    root_dir = os.path.dirname(current_dir)
    left=os.path.join(root_dir, "merge", "merge_from", label+".csv")
    columns=[]
    labels={}
    with open(left, 'r') as input:
        reader = csv.reader(input)
        columns = next(reader)
        for line in reader:
            if line[keyColumn].strip()=='':
                continue
            labels[clean(line[keyColumn])]=line

    return columns,labels

def clean(str, lower=True, strip=True, replaceAllEscapeChar=False,jsonDump=True):
    if(strip):
        str=str.strip()
    if(lower):
        str=str.lower()
    if(replaceAllEscapeChar):
        str=re.sub('[^A-Za-z0-9 \._-]+', '', str)
        if jsonDump:
            str=json.dumps(str)
    return str

def joinListWith(lst, separator=','):
    i=False
    out=''
    for c in lst:
        if i==True:
            out+=separator
        out+=json.dumps(c)
        i=True
    return out

def filterListByIndex(lst, indexLst):
    i=0
    newLst=[]
    for a in lst:
        if indexLst=='all' or i in indexLst:
            newLst.append(a)
        i+=1
    return newLst

def anyEmpty(lst, indexLst):
    i=0
    for a in lst:
        if indexLst=='all' or i in indexLst:
            if a=='' or a==None:
                return True
        i+=1
    return False

def processRawValue(str):
    str=str.strip()
    sp=['\'', '"']
    j=0
    while j<2:
        a=str.split(sp[j])
        j+=1
        i=0
        result=''
        tmp=''
        for s in a:
            if i==0:
                result+=s
                i+=1
                continue
            if i==len(a)-1:
                result+=json.dumps(tmp)
                result+=s
                i+=1
                continue
            s=re.sub('[^A-Za-z0-9 ]+', '', s)
            tmp+=s
            i+=1
        str=result

    return result

def isKeyColumnPresent(line, keyColumn):
    for kc in keyColumn:
        if line[kc] == None or line[kc] == "":
            return False
    return True

def normalizeApiName(layerApi, maxLen=None):
    layerApi=clean(layerApi, True, True)
    if layerApi.startswith('tensorflow.compat.v1.'):
        layerApi = layerApi.replace('.compat.v1', '')

    if layerApi.startswith('tensorflow.keras.'):
        layerApi=layerApi[len('tensorflow.'):]

    if layerApi.startswith('tensorflow.python.keras.') :
        layerApi = layerApi.replace('tensorflow.python.','')

    if maxLen!=None:
        tmp = layerApi.split(".")

        layerApi = ""
        for _i, _t in enumerate(tmp):
            if _i  == maxLen:
                break
            if _i != 0:
                layerApi += '.'
            layerApi += _t

    return layerApi

def getLeftLine(layerApi, leftData):
    if layerApi in leftData:
        return leftData[layerApi]

    if layerApi.startswith('tensorflow.compat.v1.') and layerApi.replace('.compat.v1','') in leftData:
        return leftData[layerApi.replace('.compat.v1','')]

    if layerApi.startswith('tensorflow.keras.') and layerApi[len('tensorflow.'):] in leftData:
        return leftData[layerApi[len('tensorflow.'):]]

    if layerApi.startswith('tensorflow.python.keras.') :

        if layerApi.replace('.python','') in leftData:
            return leftData[layerApi.replace('.python','')]
        if layerApi.replace('tensorflow.python.', '') in leftData:
            return leftData[layerApi.replace('tensorflow.python.', '')]

    if layerApi.startswith('keras.'):
        if ('tensorflow.'+layerApi) in leftData:
            return leftData[('tensorflow.'+layerApi)]
        if ('tensorflow.python.' + layerApi) in leftData:
            return leftData[('tensorflow.python.' + layerApi)]
    return ''

def matchPattern(patterns, value):
    i=0
    for p in patterns:
        if p=='*':
            return i
        if p.startswith('@'):
            try:
                value=float(value)
            except:
                i+=1
                continue
            p=p[1:]

            if p.startswith('>'):
                p=p[1:]
                p=float(p)
                if float(value)>p:
                    return i
            elif p.startswith('<'):
                p=p[1:]
                p=float(p)
                if float(value)<p:
                    return i


        elif p.startswith('*'):
            p=p[1:]

            if p.endswith('*'):
                p=p[:-1]

                if p in value:
                    return i
            else:
                if value.endswith(p):
                    return i
        else:
            if p.endswith('*'):
                p = p[:-1]

                if value.startswith(p):
                    return i
            else:
                if p==value:
                    return i
        i+=1
    return -1

def getAllTzInfo():
    timezone_info = {
        "A": 1 * 3600,
        "ACDT": 10.5 * 3600,
        "ACST": 9.5 * 3600,
        "ACT": -5 * 3600,
        "ACWST": 8.75 * 3600,
        "ADT": 4 * 3600,
        "AEDT": 11 * 3600,
        "AEST": 10 * 3600,
        "AET": 10 * 3600,
        "AFT": 4.5 * 3600,
        "AKDT": -8 * 3600,
        "AKST": -9 * 3600,
        "ALMT": 6 * 3600,
        "AMST": -3 * 3600,
        "AMT": -4 * 3600,
        "ANAST": 12 * 3600,
        "ANAT": 12 * 3600,
        "AQTT": 5 * 3600,
        "ART": -3 * 3600,
        "AST": 3 * 3600,
        "AT": -4 * 3600,
        "AWDT": 9 * 3600,
        "AWST": 8 * 3600,
        "AZOST": 0 * 3600,
        "AZOT": -1 * 3600,
        "AZST": 5 * 3600,
        "AZT": 4 * 3600,
        "AoE": -12 * 3600,
        "B": 2 * 3600,
        "BNT": 8 * 3600,
        "BOT": -4 * 3600,
        "BRST": -2 * 3600,
        "BRT": -3 * 3600,
        "BST": 6 * 3600,
        "BTT": 6 * 3600,
        "C": 3 * 3600,
        "CAST": 8 * 3600,
        "CAT": 2 * 3600,
        "CCT": 6.5 * 3600,
        "CDT": -5 * 3600,
        "CEST": 2 * 3600,
        "CET": 1 * 3600,
        "CHADT": 13.75 * 3600,
        "CHAST": 12.75 * 3600,
        "CHOST": 9 * 3600,
        "CHOT": 8 * 3600,
        "CHUT": 10 * 3600,
        "CIDST": -4 * 3600,
        "CIST": -5 * 3600,
        "CKT": -10 * 3600,
        "CLST": -3 * 3600,
        "CLT": -4 * 3600,
        "COT": -5 * 3600,
        "CST": -6 * 3600,
        "CT": -6 * 3600,
        "CVT": -1 * 3600,
        "CXT": 7 * 3600,
        "ChST": 10 * 3600,
        "D": 4 * 3600,
        "DAVT": 7 * 3600,
        "DDUT": 10 * 3600,
        "E": 5 * 3600,
        "EASST": -5 * 3600,
        "EAST": -6 * 3600,
        "EAT": 3 * 3600,
        "ECT": -5 * 3600,
        "EDT": -4 * 3600,
        "EEST": 3 * 3600,
        "EET": 2 * 3600,
        "EGST": 0 * 3600,
        "EGT": -1 * 3600,
        "EST": -5 * 3600,
        "ET": -5 * 3600,
        "F": 6 * 3600,
        "FET": 3 * 3600,
        "FJST": 13 * 3600,
        "FJT": 12 * 3600,
        "FKST": -3 * 3600,
        "FKT": -4 * 3600,
        "FNT": -2 * 3600,
        "G": 7 * 3600,
        "GALT": -6 * 3600,
        "GAMT": -9 * 3600,
        "GET": 4 * 3600,
        "GFT": -3 * 3600,
        "GILT": 12 * 3600,
        "GMT": 0 * 3600,
        "GST": 4 * 3600,
        "GYT": -4 * 3600,
        "H": 8 * 3600,
        "HDT": -9 * 3600,
        "HKT": 8 * 3600,
        "HOVST": 8 * 3600,
        "HOVT": 7 * 3600,
        "HST": -10 * 3600,
        "I": 9 * 3600,
        "ICT": 7 * 3600,
        "IDT": 3 * 3600,
        "IOT": 6 * 3600,
        "IRDT": 4.5 * 3600,
        "IRKST": 9 * 3600,
        "IRKT": 8 * 3600,
        "IRST": 3.5 * 3600,
        "IST": 5.5 * 3600,
        "JST": 9 * 3600,
        "K": 10 * 3600,
        "KGT": 6 * 3600,
        "KOST": 11 * 3600,
        "KRAST": 8 * 3600,
        "KRAT": 7 * 3600,
        "KST": 9 * 3600,
        "KUYT": 4 * 3600,
        "L": 11 * 3600,
        "LHDT": 11 * 3600,
        "LHST": 10.5 * 3600,
        "LINT": 14 * 3600,
        "M": 12 * 3600,
        "MAGST": 12 * 3600,
        "MAGT": 11 * 3600,
        "MART": 9.5 * 3600,
        "MAWT": 5 * 3600,
        "MDT": -6 * 3600,
        "MHT": 12 * 3600,
        "MMT": 6.5 * 3600,
        "MSD": 4 * 3600,
        "MSK": 3 * 3600,
        "MST": -7 * 3600,
        "MT": -7 * 3600,
        "MUT": 4 * 3600,
        "MVT": 5 * 3600,
        "MYT": 8 * 3600,
        "N": -1 * 3600,
        "NCT": 11 * 3600,
        "NDT": 2.5 * 3600,
        "NFT": 11 * 3600,
        "NOVST": 7 * 3600,
        "NOVT": 7 * 3600,
        "NPT": 5.5 * 3600,
        "NRT": 12 * 3600,
        "NST": 3.5 * 3600,
        "NUT": -11 * 3600,
        "NZDT": 13 * 3600,
        "NZST": 12 * 3600,
        "O": -2 * 3600,
        "OMSST": 7 * 3600,
        "OMST": 6 * 3600,
        "ORAT": 5 * 3600,
        "P": -3 * 3600,
        "PDT": -7 * 3600,
        "PET": -5 * 3600,
        "PETST": 12 * 3600,
        "PETT": 12 * 3600,
        "PGT": 10 * 3600,
        "PHOT": 13 * 3600,
        "PHT": 8 * 3600,
        "PKT": 5 * 3600,
        "PMDT": -2 * 3600,
        "PMST": -3 * 3600,
        "PONT": 11 * 3600,
        "PST": -8 * 3600,
        "PT": -8 * 3600,
        "PWT": 9 * 3600,
        "PYST": -3 * 3600,
        "PYT": -4 * 3600,
        "Q": -4 * 3600,
        "QYZT": 6 * 3600,
        "R": -5 * 3600,
        "RET": 4 * 3600,
        "ROTT": -3 * 3600,
        "S": -6 * 3600,
        "SAKT": 11 * 3600,
        "SAMT": 4 * 3600,
        "SAST": 2 * 3600,
        "SBT": 11 * 3600,
        "SCT": 4 * 3600,
        "SGT": 8 * 3600,
        "SRET": 11 * 3600,
        "SRT": -3 * 3600,
        "SST": -11 * 3600,
        "SYOT": 3 * 3600,
        "T": -7 * 3600,
        "TAHT": -10 * 3600,
        "TFT": 5 * 3600,
        "TJT": 5 * 3600,
        "TKT": 13 * 3600,
        "TLT": 9 * 3600,
        "TMT": 5 * 3600,
        "TOST": 14 * 3600,
        "TOT": 13 * 3600,
        "TRT": 3 * 3600,
        "TVT": 12 * 3600,
        "U": -8 * 3600,
        "ULAST": 9 * 3600,
        "ULAT": 8 * 3600,
        "UTC": 0 * 3600,
        "UYST": -2 * 3600,
        "UYT": -3 * 3600,
        "UZT": 5 * 3600,
        "V": -9 * 3600,
        "VET": -4 * 3600,
        "VLAST": 11 * 3600,
        "VLAT": 10 * 3600,
        "VOST": 6 * 3600,
        "VUT": 11 * 3600,
        "W": -10 * 3600,
        "WAKT": 12 * 3600,
        "WARST": -3 * 3600,
        "WAST": 2 * 3600,
        "WAT": 1 * 3600,
        "WEST": 1 * 3600,
        "WET": 0 * 3600,
        "WFT": 12 * 3600,
        "WGST": -2 * 3600,
        "WGT": -3 * 3600,
        "WIB": 7 * 3600,
        "WIT": 9 * 3600,
        "WITA": 8 * 3600,
        "WST": 14 * 3600,
        "WT": 0 * 3600,
        "X": -11 * 3600,
        "Y": -12 * 3600,
        "YAKST": 10 * 3600,
        "YAKT": 9 * 3600,
        "YAPT": 10 * 3600,
        "YEKST": 6 * 3600,
        "YEKT": 5 * 3600,
        "Z": 0 * 3600,
    }
    return timezone_info
def getTimeInUTC(commitTime):
    commitTime = parser.parse(commitTime, tzinfos=getAllTzInfo())
    commitTime = commitTime.astimezone(tz.tzutc())
    return commitTime

def convertToPythonRegex(pattern):
    if pattern.startswith('*')==False:
        pattern='^'+pattern
    if pattern.endswith('*')==False:
        pattern=pattern+'$'
    pattern = pattern.replace('.', '\.')
    pattern = pattern.replace('*', '.*')
    return pattern

def apiMatcherFromList(patterns, apiName):
    for p in patterns:
        if re.match(p, apiName)!=None:
            return p
    return None

def apiMatcher(patterns, apiName):
    for p in patterns.keys():
        if re.match(p, apiName)!=None:
            return p
    return None

def normalizeWithin(data, to_percent=True):
    total=0
    for curType in data.keys():
        total+=data[curType]
    if to_percent:
        for curType in data.keys():
            data[curType]=(data[curType]/total)*100.0
    return data

if __name__ == "__main__":
    # str='impactList[AlexiaJM/Deep-learning-with-cats][f5c1118f59e2b853969894a2bcc3200d940fd765][torch.nn.Sequential.add_module][0]["Start\'-[%]\'BatchNorm2d"][ADDED] = 2'
    # print(processRawValue(str))
    print(normalizeApiName('tensorflow.compat.v1.keras.hei.1.2.3.4.5', 4))