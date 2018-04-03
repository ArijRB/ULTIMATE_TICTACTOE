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


    
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'tictactoe'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    #A*
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
            pour un probleme de taquin p donné
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
            print (n)
            l.append(n.etat)
            n = n.pere
            c+=1
        print ("Nombre d'étapes de la solution:", c-1)
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

    # TODO: VERSION 2 --- Un noeud en réserve peut revenir dans la frontière        
        
        stop_stepwise=""
        if stepwise==True:
            stop_stepwise = input("Press Enter to continue (s to stop)...")
            print ("best", min_f, "\n", bestNoeud)
            print ("Frontière: \n", frontiere)
            print ("Réserve:", reserve)
            if stop_stepwise=="s":
                stepwise=False
    
    l = bestNoeud.trace(p)          

    return l
    
def main():

    #for arg in sys.argv:
    iterations = 200 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()
    
    


    
    #-------------------------------
    # Initialisation
    #-------------------------------
       
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    #score = [0]*nbPlayers
    fioles = {} # dictionnaire (x,y)->couleur pour les fioles
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    
    # on localise tous les objets ramassables
    #goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    #print ("Goal states:", goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    tictactoeStates = [(x,y) for x in range(3,16) for y in range(3,16)]
    #print ("Wall states:", wallStates)
    
    #-------------------------------
    # Placement aleatoire des fioles de couleur 
    #-------------------------------
    
    for o in game.layers['ramassable']: # on considère chaque fiole
        
        #on détermine la couleur
    
        if o.tileid == (19,0): # tileid donne la coordonnee dans la fiche de sprites
            couleur = 'r'
        elif o.tileid == (19,1):
            couleur = 'j'
        else:
            couleur = 'b'

        # et on met la fiole qqpart au hasard

        x = random.randint(1,19)
        y = random.randint(1,19)

        while (x,y) in tictactoeStates or (x,y) in wallStates or (x,y) in fioles: # ... mais pas sur un mur
            x = random.randint(1,19)
            y = random.randint(1,19)
        o.set_rowcol(x,y)
        # on ajoute cette fiole 
        fioles[(x,y)]=couleur

        game.layers['ramassable'].add(o)
        game.mainiteration()                

    print("Les ", len(fioles), " fioles ont été placées aux endroits suivants: \n", fioles)


    
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    
        
    # bon ici on fait juste plusieurs random walker pour exemple...
    
    posPlayers = initStates
    
    for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement
        row,col = posPlayers[j]
        p = Probleme(posPlayers[j], fioles.keys()[0], 'manhattan', game)
        l = astar(p,False,False)

        # and ((next_row,next_col) not in posPlayers)
    for case in l:
        row,col= case
        posPlayers[j]=(row,col)
        
            
      
        
            
        # si on trouve un objet on le ramasse
        if (row,col) in fioles:
            o = players[j].ramasse(game.layers)
            game.mainiteration()
            print ("Objet de couleur ", fioles[(row,col)], " trouvé par le joueur ", j)
            fioles.pop((row,col))   # on enlève cette fiole de la liste
                
                 
                
                #break
            
    
    print (fioles)
    pygame.quit()
    
        
    
   

if __name__ == '__main__':
    main()
    


