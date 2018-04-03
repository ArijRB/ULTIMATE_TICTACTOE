# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 14:20:16 2018

@author: 3520359
"""

# -*- coding: utf-8 -*-

# Nicolas, 2015-11-18

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
from Astar import *
from Glouton import *
from GloutonV2 import *
from MinMAX import *

    
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'tictactoeBis'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 30  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    


#-------------------------------
    # Gerer Victoire  
    #-------------------------------
def victoire(fiole_a_poser,morpion_pris,rand,morpions,fioles,test,parties_j1,parties_j2,parties_nuls,j,gains_cases):    
    x_test, y_test = fiole_a_poser
    x_min,y_min = morpions[rand][0]
    x_max, y_max = morpions[rand][8]
    h = 0
    v = 0
    dg = 0
    dd = 0
    cpt = 0
    for i in morpion_pris:
        if(i in morpions[rand]):
            cpt = cpt + 1
        if(fioles[morpion_pris.index(i)] == j):
            (x, y) = i
            for k in test:
                if(x == x_test+k and y == y_test and x_test+k <= x_max and x_test+k >= x_min):
                    h = h+1
                if(x == x_test and y == y_test+k and y_test+k <= y_max and y_test+k >= y_min):
                    v = v+1
                if(x == x_test+k and y == y_test+k and x_test+k <= x_max and x_test+k >= x_min and y_test+k <= y_max and y_test+k >= y_min):
                    dg = dg+1
                if(x == x_test+k and y == y_test-k and x_test+k <= x_max and x_test+k >= x_min and y_test-k <= y_max and y_test-k >= y_min):
                    dd = dd+1
    if(h == 2 or v == 2 or dg ==2 or dd == 2):
        if(j == 0):
            parties_j1.append(rand)
            for d in gains_cases:
                if(set(d).issubset(set(parties_j1))):
                    print("j1:",parties_j1)
                    print("j2:",parties_j2)
                    print("Victoire joueur1")
                    return 1;            
        else:
            parties_j2.append(rand)
            for d in gains_cases:
                if(set(d).issubset(set(parties_j2))):
                    print("j1:",parties_j1)
                    print("j2:",parties_j2)
                    print("Victoire joueur2")
                    return 2;    
                
    if(cpt >= 9):
        if(rand not in parties_nuls):
            parties_nuls.append(rand)
    if((len(parties_nuls)+len(parties_j2)+len(parties_j1)) >= 9):
        print("j1:",parties_j1)
        print("j2:",parties_j2)
        print("bloqués: ", parties_nuls)
        print("Match Null")
        return 0
    return -1

def aleatoire(rand,morpions,morpion_pris,parties_b):
    while(rand in parties_b):
        rand = random.randint(0,8)
    rand2 = random.randint(0,8)
    while(morpions[rand][rand2] in morpion_pris):
        rand2 = random.randint(0,8)
    return rand,rand2

def Jouer(v,s1,s2):            
    
    init()
    
    #-------------------------------
    # Initialisation
    #-------------------------------
       
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    #score = [0]*nbPlayers
    #fioles = {} # dictionnaire (x,y)->couleur pour les fioles
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
#    print ("Init states:", initStates)   
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    # et la zone de jeu pour le tic-tac-toe
    tictactoeStates = [(x,y) for x in range(3,16) for y in range(3,16)]
    #print ("Wall states:", wallStates)
    
    # les coordonnees des tiles dans la fiche
    tile_fiole_jaune = (19,1)
    tile_fiole_bleue = (20,1)
    
    # listes des objets fioles jaunes et bleues
    
    fiolesJaunes = [f for f in game.layers['ramassable'] if f.tileid==tile_fiole_jaune]
    fiolesBleues = [f for f in game.layers['ramassable'] if f.tileid==tile_fiole_bleue]   
    all_fioles = (fiolesJaunes,fiolesBleues) 
    fiole_a_ramasser = (0,0) # servira à repérer la prochaine fiole à prendre
    
    # renvoie la couleur d'une fiole
    # potentiellement utile
    
    def couleur(o):
        if o.tileid==tile_fiole_jaune:
            return 'j'
        elif o.tileid==tile_fiole_bleue:
            return 'b'
    
    
    #-------------------------------
    # Placement aleatoire d'une fioles de couleur 
    #-------------------------------
    
    def put_next_fiole(j,t):
        o = all_fioles[j][t]
    
        # et on met cette fiole qqpart au hasard
    
        x = random.randint(1,19)
        y = random.randint(1,19)
    
        while (x,y) in tictactoeStates or (x,y) in wallStates: # ... mais pas sur un mur
            x = random.randint(1,19)
            y = random.randint(1,19)
        o.set_rowcol(x,y)
        # on ajoute cette fiole dans le dictionnaire
        #fioles[(x,y)]=couleur(o)
    
        game.layers['ramassable'].add(o)
        game.mainiteration()
        return (x,y)
  
    
    

    posPlayers = initStates

    tour = 0    
    j = v # le joueur v commence
    # on place la premiere fiole jaune      

    fiole_a_ramasser = put_next_fiole(v,tour)
    p = Probleme(posPlayers[0], fiole_a_ramasser, 'manhattan', game)
    l = astar(p,False,False)
    
    morpions = [] #création du grand morpion contenant tous les autres petits morpions
    ligne = 4
    colonne = 4
    for k in range (0,9):
        morpion = []
        for x in range(ligne, ligne + 3):
            for y in range(colonne, colonne + 3):
                morpion.append((x,y))
        if(colonne < 12):
            colonne = colonne + 4
        else:
            ligne = ligne + 4
            colonne = 4
        morpions.append(morpion)
    gains_cases=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[4,1,7],[5,8,2],[0,4,8],[4,6,2]]
    morpion_pris = [] #contiendra toutes les cases prises dans le grand morpion
    fioles = [] 
    parties_j1 = [] #contiendra toutes les parties gagnées par le premier joueur dans le morpion courant
    parties_j2 = [] #contiendra toutes les parties gagnées par le second joueur dans le morpion courant
    fioles_j1 = [] #contiendra les fioles posées par le premier joueur dans chacun des petits morpions -> sert à la fonction gloutonne 
    fioles_j2 = [] #contiendra les fioles posées par le second joueur dans chacun des petits morpions -> sert à la fonction gloutonne
    for i in range(0,9):
        liste = []
        fioles_j1.append(liste)
        fioles_j2.append(liste)
    parties_nuls = []
    test = [-2, -1, 1, 2]
    rand = random.randint(0,8)
    fiole_a_poser = (-1,-1)
    cond=-1
    
    while(cond == -1):        
        row,col = posPlayers[j]

        
        next_row, next_col = l.pop()
        #Pour déplacer le joueur
        
        # and ((next_row,next_col) not in posPlayers)
        players[j].set_rowcol(next_row,next_col)
        game.mainiteration()

        col=next_col
        row=next_row
        posPlayers[j]=(row,col)
        
        # si on est arrivé à la fiole 
        if (row,col)==fiole_a_ramasser:
            o = players[j].ramasse(game.layers) # on la ramasse
#            print ("Objet de couleur ", couleur(o), " trouvé par le joueur ", j)
            game.mainiteration()
            if(j == 0):
                if (s1==1):
                   rand,rand2= glouton(fioles_j1, morpion_pris, morpions, rand, parties_j1 + parties_j2+ parties_nuls, test)
                else:
                    if (s1==0):
                        rand,rand2=aleatoire(rand,morpions,morpion_pris,parties_j1 + parties_j2+ parties_nuls)
                    elif(s1==2):
                        rand,rand2= gloutonv2(fioles_j1, morpion_pris,morpions,rand,parties_j1 + parties_j2+ parties_nuls, fioles_j2, test)
                    elif(s1==3):
                        parties_b=list(parties_j1 + parties_j2+ parties_nuls)
                        while(rand in parties_b):
                            rand = random.randint(0,8)
                        rand,rand2=alphabeta(morpion_pris,rand,morpions,fioles,parties_j1,parties_j2,parties_nuls,0)
            if(j == 1):
                if (s2==0):
                    rand,rand2=aleatoire(rand,morpions,morpion_pris,parties_j1 + parties_j2+ parties_nuls)
                else:
                    if (s2==1):
                       rand,rand2= glouton(fioles_j2, morpion_pris,morpions,rand,parties_j1 + parties_j2+ parties_nuls,test)
                    elif(s2==2):
                        rand,rand2= gloutonv2(fioles_j2, morpion_pris,morpions,rand,parties_j1 + parties_j2+ parties_nuls, fioles_j1, test)
            #on stock les indices de la case à jouer dans notre variable, on ajoute la case que l'on va jouer au cases jouées et l'on calcul le chemin à faire
            fiole_a_poser = morpions[rand][rand2]
            morpion_pris.append(fiole_a_poser)
            fioles.append(j)
            fiole_a_ramasser = (0,0)
            p = Probleme(posPlayers[j], fiole_a_poser, 'manhattan', game)
            l = astar(p,False,False)
        
        if (row,col)==fiole_a_poser:
            # on active le joueur suivant
            # et on place la fiole suivante
            o.set_rowcol(row,col)
            game.layers['ramassable'].add(o)
            game.mainiteration()
            #on regarde si le joueur à gagner suite à la pose de sa fiole
            cond=victoire(fiole_a_poser,morpion_pris,rand,morpions,fioles,test,parties_j1,parties_j2,parties_nuls,j,gains_cases)
            #on rajoute la fiole à son registre de fioles posées
            if(j == 0):
                fioles_j1[rand].append(fiole_a_poser)
            else:
                fioles_j2[rand].append(fiole_a_poser)
            rand = rand2
            j = (j+1)%2        
            if j == v:
                tour+=1
            
            fiole_a_ramasser=put_next_fiole(j,tour)
            p = Probleme(posPlayers[j], fiole_a_ramasser, 'manhattan', game)
            l = astar(p,False,False)
            fiole_a_poser = (-1,-1)
    
       
            
    
    return cond

Jouer(0,0,0)