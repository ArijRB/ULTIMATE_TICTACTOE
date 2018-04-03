#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 11:35:28 2018

@author: 3520359
"""
from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo
import heapq

import random 
import numpy as np
import sys
from matplotlib import pyplot as plt
from IPython.core.pylabtools import figsize
import networkx as nx
import pylab


def gloutonv2(fioles_jouees, morpion_joue, morpions, rand, parties_bloquees, fioles_jouees_autre_j, test):
    """On détermine le morpion dans lequel on joue avec rand
        Ensuite une fois que l'on sait dans quel morpion on détermine les limites du morpion et on prend les fioles qu'on a joué dans ce morpion"""
    while(rand in parties_bloquees):
        rand = random.randint(0,8)
    x_base, y_base = morpions[rand][0]
    x_max, y_max = morpions[rand][8]
    fioles_jouee = fioles_jouees[rand]
    
    """Si on a pas encore joué de fiole et que la case du milieu est libre alors on joue au milieu sinon aléatoirement en renvoyant (rand,-1)"""
    if(fioles_jouee == []):
        rand2=4
        if( (x_base + 1,y_base + 1) not in morpion_joue):
                return rand,morpions[rand].index((x_base + 1,y_base + 1))
        elif( (x_base + 2,y_base + 2) not in morpion_joue):
                return rand,morpions[rand].index((x_base + 2,y_base + 2))
        if( (x_base ,y_base + 2) not in morpion_joue):
            return rand,morpions[rand].index((x_base + 2,y_base + 0))
        elif( (x_base +2 ,y_base + 0) not in morpion_joue):
            return rand,morpions[rand].index((x_base + 2,y_base + 0))
        else:
            while(morpions[rand][rand2] in morpion_joue):
                rand2 = random.randint(0,8)
            return rand,rand2
    else:
        """Sinon pour chaque fiole qu'on a joué on regarde si elle peut nous amener à une situation gagnante sur ce morpion
"""
        for i in fioles_jouee:
            x, y = i
            h = 0
            v = 0
            dg = 0
            dd = 0
            """On regarde si l'on peut gagner en diagonales (gauche ou droite) ou en horizontal et vertical
"""
            for k in test:
                if(((x + k, y) not in morpion_joue or (x + k, y) in fioles_jouee) and x + k <= x_max and x + k >= x_base):
                    h = h+1
                if(((x, y + k) not in morpion_joue or (x, y + k) in fioles_jouee) and y + k <= y_max and y + k >= y_base):
                    v = v+1
                if(((x + k, y + k) not in morpion_joue or (x + k, y + k) in fioles_jouee) and x + k <= x_max and x + k >= x_base and y + k <= y_max and y + k >= y_base):
                    dg = dg+1
                if(((x + k, y - k) not in morpion_joue or (x + k, y - k) in fioles_jouee) and x + k <= x_max and x + k >= x_base and y - k <= y_max and y - k >= y_base):
                    dd = dd+1
            """Si on trouve deux cases en plus de celle que l'on examine qui sont libres ou bien déjà à nous alors on complète
                Les diagonales seront complétées en priorité par rapport aux lignes"""
            if(dg == 2):
                for k in test:
                    if((x + k, y + k) not in morpion_joue and (x + k, y + k) not in fioles_jouee and x + k <= x_max and x + k >= x_base and y + k <= y_max and y + k >= y_base):
                        return rand,morpions[rand].index((x + k, y + k))
            if(dd == 2):
                for k in test:
                    if((x + k, y - k) not in morpion_joue and (x + k, y - k) not in fioles_jouee and x + k <= x_max and x + k >= x_base and y - k <= y_max and y - k >= y_base):
                        return rand,morpions[rand].index((x + k, y - k))
            if(h == 2):
                for k in test:
                    if((x + k, y) not in morpion_joue and (x + k, y) not in fioles_jouee and x + k <= x_max and x + k >= x_base):
                        return rand,morpions[rand].index((x + k, y))
            if(v == 2):
                for k in test:
                    if((x, y + k) not in morpion_joue and (x, y + k) not in fioles_jouee and y + k <= y_max and y + k >= y_base):
                        return rand,morpions[rand].index((x, y + k))
        
    min = 10
    for cpt in range (0,fioles_jouees_autre_j.length):
        if(cpt not in parties_bloquees and min > fioles_jouees_autre_j[cpt]):
            rand2 = cpt
    return rand,rand2