#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 14:39:58 2018

@author: arij
"""
import numpy as np
from matplotlib import pyplot as plt
from IPython.core.pylabtools import figsize
import networkx as nx
import pylab
import UltimateTicTacToeNew


def Tournoi(k,s1,s2):
    nbIterations=6
    toPlot = {'J1':[0], 'J2':[0]}
    gainsCumules = {'J1': 0, 'J2': 0}
    for i in range(nbIterations):
        print ("Match N°",i)
        g=UltimateTicTacToeNew.Jouer(k,s1,s2)
        if(g==1):
            gainsCumules['J1']+=1
            gainsCumules['J2']+=-0.25
        elif(g==2):
            gainsCumules['J2']+=1
            gainsCumules['J1']+=-0.25
        toPlot['J1'].append(gainsCumules['J1'])
        toPlot['J2'].append(gainsCumules['J2'])  
    return toPlot,gainsCumules

def dessin(toPlot,gainsCumules,legende):
    nbIterations=6
    figsize(12.5, 4)
    p = np.linspace(0, nbIterations, nbIterations+1)
    plt.plot(p, toPlot['J1'], color='red')
    plt.plot(p, toPlot['J2'], color = 'blue')
    plt.suptitle(legende, y=1.02, fontsize=15)
    plt.tight_layout()