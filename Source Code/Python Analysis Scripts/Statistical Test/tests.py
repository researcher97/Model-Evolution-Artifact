from scipy.stats import mannwhitneyu
from scipy.stats import chi2_contingency, chi2
import scipy.stats as st
import numpy as np
from scipy.stats import kruskal

def mannWhitneyU(data1,data2,alpha=0.05):
    stat, p = mannwhitneyu(data1, data2, alternative='two-sided', use_continuity=False)

    wht='Different'
    if p > alpha:
        wht='Same'

    return stat,p,wht

def chiSquareTest(data1,data2,alpha=0.05):
    table=[data1, data2]

    stat, p, dof, expected = chi2_contingency(table)

    # print('significance=%.3f, p=%.3f' % (alpha, p))
    wht = 'Independent'
    if p <= alpha:
        wht='Dependent'


    return stat,p,wht

def getConfidenInterval(data,alpha=0.95):
    return st.norm.interval(alpha=alpha, loc=np.mean(data), scale=st.sem(data))

def getConfidenIntervalForLessData(data,alpha=0.95):
    return st.t.interval(alpha=0.95, df=len(data)-1, loc=np.mean(data), scale=st.sem(data))

def kruskalTest(data, alpha=0.05):

    if len(data)==3:
        stat, p = kruskal(data[0],data[1],data[2])
    else:
        stat, p = kruskal(data[0], data[1])

    wht = 'Same' #fail to reject H0
    if p <= alpha:
        wht='Different' #reject H0


    return stat,p,wht