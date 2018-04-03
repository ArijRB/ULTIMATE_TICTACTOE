#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 10:38:30 2018

@author: arij
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

game = Game()
class Probleme(object):
    """ On definit un probleme comme étant: 
        - un état initial
        - un état but
        - une heuristique
        """
        
    def __init__(self,init,but,heuristique,game):
        self.init=init
        self.but=but
        self.heuristique=heuristique
        self.game=game
        
    def estBut(self,e):
        """ retourne vrai si l'état e est un état but
            """
        return (self.but==e)
         
    def cost(self,e1,e2):
        """ donne le cout d'une action entre e1 et e2, 
            """
        return 1
    
    def estObstacle(self,e):
        """ retorune vrai si l'état est un obsacle
            """
        return e in [w.get_rowcol() for w in game.layers['obstacle']]
        
    def estDehors(self,e):
        """retourne vrai si en dehors de la grille
            """
        return  (e[0]<=0 or e[0]>=19) or (e[1]<=0 or e[1]>=19)
        
    def successeurs(self,etat):
            """ retourne des positions successeurs possibles
                """
            current_x,current_y = etat
            d = [(0,1),(1,0),(0,-1),(-1,0)]
            etatsApresMove = [(current_x+inc_x,current_y+inc_y) for (inc_x,inc_y) in d]
            return [e for e in etatsApresMove if not(self.estDehors(e)) and not(self.estObstacle(e))]

    def immatriculation(self,etat):
        """ génère une chaine permettant d'identifier un état de manière unique
            """
        s=""
        (x,y)= etat
        s+=str(x)+str(y)
        return s
        
    def h_value(self,e1,e2):
        """ applique l'heuristique pour le calcul 
            """
        if self.heuristique=='manhattan':
            h = distManhattan(e1,e2)
        return h

def distManhattan(p1,p2):
    """ calcule la distance de Manhattan entre le personnage
        et la fiole
        """
    (x1,y1)=p1
    (x2,y2)=p2
    return abs(x1-x2)+abs(y1-y2)
    
class Noeud:
    def __init__(self, etat, g, pere=None):
        self.etat = etat
        self.g = g
        self.pere = pere
        
    def __str__(self):
        #return np.array_str(self.etat) + "valeur=" + str(self.g)
        return str(self.etat) + "valeur=" + str(self.g)
        
    def __eq__(self, other):
        return str(self) == str(other)
        
    def __lt__(self, other):
        return str(self) < str(other)
        
    def expand(self,p):
        """ étend un noeud avec ces fils
            pour un probleme donné
            """
        nouveaux_fils = [Noeud(s,self.g+p.cost(self.etat,s),self) for s in p.successeurs(self.etat)]
        return nouveaux_fils
        
    def expandNext(self,p,k):
        """ étend un noeud unique, le k-ième fils du noeud n
            ou liste vide si plus de noeud à étendre
            """
        nouveaux_fils = self.expand(p)
        if len(nouveaux_fils)<k: 
            return []
        else: 
            return self.expand(p)[k-1]
            
    def trace(self,p):
        """ affiche tous les ancetres du noeud
            """
        n = self
        c=0    
        l = []
        while n!=None :
            l.append(n.etat)
            n = n.pere
            c+=1
        #print ("Nombre d'étapes de la solution:", c-1)
        return l
 
def astar(p,verbose=False,stepwise=False):
    """
    application de l'algorithme a-star
    sur un probleme donné
        """
        
    nodeInit = Noeud(p.init,0,None)
    frontiere = [(nodeInit.g+p.h_value(nodeInit.etat,p.but),nodeInit)]

    reserve = {}        
    bestNoeud = nodeInit
    
    while frontiere != [] and not p.estBut(bestNoeud.etat):              
        (min_f,bestNoeud) = heapq.heappop(frontiere)

    # VERSION 1 --- On suppose qu'un noeud en réserve n'est jamais ré-étendu
    # Hypothèse de consistence de l'heuristique        
        
        if p.immatriculation(bestNoeud.etat) not in reserve:        
            reserve[p.immatriculation(bestNoeud.etat)] = bestNoeud.g #maj de reserve
            nouveauxNoeuds = bestNoeud.expand(p)
            for n in nouveauxNoeuds:
                f = n.g+p.h_value(n.etat,p.but)
                heapq.heappush(frontiere, (f,n))
    
    l = bestNoeud.trace(p)          

    return l
