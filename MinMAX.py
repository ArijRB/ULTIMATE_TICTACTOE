from __future__ import absolute_import, print_function, unicode_literals

def alphabeta(morpion_pris,r,morpions,fioles,parties_j1,parties_j2,parties_nuls,jx):
    morpion_prisx=list(morpion_pris)
    morpionsx=list(morpions)
    fiolesx=list(fioles)
    parties_j1x=list(parties_j1)
    parties_j2x=list(parties_j2)
    parties_nulsx=list(parties_nuls)
    gains_cases=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[4,1,7],[5,8,2],[0,4,8],[4,6,2]]
    def after_move(morpion_prisx,fiolesx,i,jx):
        morpion_prisx.append(i)
        fiolesx.append(jx)
        jx = (jx+1)%2 
        return morpion_prisx,fiolesx,jx
    
    def victoire2(fiolex,morpion_prisx,randx,morpionsx,fiolesx,parties_j1x,parties_j2x,parties_nulsx,jx):  
        t=[]
        cpt=0
        h=False
        for f in morpion_prisx :
            cpt+=1
            if f in morpion_prisx:
                t.append(morpion_prisx.index(f))
        for d in gains_cases:
            if(set(d).issubset(set(t))):
                h=True     
        if(h):
            if(jx == 0):
                parties_j1x.append(randx)
                for d in gains_cases:
                    if(set(d).issubset(set(parties_j1x))):
                        return 1           
            else:
                parties_j2x.append(randx)
                for d in gains_cases:
                    if(set(d).issubset(set(parties_j2x))):
                        return -0.25    
                    
        if(cpt >= 9):
            if(randx not in parties_nulsx):
                parties_nulsx.append(randx)
        if((len(parties_nulsx)+len(parties_j2x)+len(parties_j1x)) >= 9):
            return 0
        return -1    
    def max_valeur(morpion_prisx,fiolesx,j,i,k,morpionsx,parties_j1x,parties_j2x,parties_nulsx,alpha, beta):
        ut=victoire2(i,morpion_prisx,k,morpionsx,fiolesx,parties_j1x,parties_j2x,parties_nulsx,j)
        if (ut != -1):
            return ut
        v = -1000
        for h in morpionsx[k]:
            if h not in morpion_prisx:
#                print("test ici ",h)
                morpion_prisx,fiolesx,j=after_move(morpion_prisx,fiolesx,i,j)
                v = max(v, min_valeur(morpion_prisx,fiolesx,j,h,morpionsx[k].index(h),morpionsx,parties_j1x,parties_j2x,parties_nulsx,alpha, beta))
                if v >= beta:
                    return v
                alpha = max(alpha, v)
        return v

    def min_valeur(morpion_prisx,fiolesx,j,i,k,morpionsx,parties_j1x,parties_j2x,parties_nulsx,alpha, beta):
        ut=victoire2(i,morpion_prisx,k,morpionsx,fiolesx,parties_j1x,parties_j2x,parties_nulsx,j)
        if (ut != -1):
            return ut
        v = 1000
        for h in morpionsx[k]:
            if h not in morpion_prisx:
#                print("test ici min ",h)
                morpion_prisx,fiolesx,j=after_move(morpion_prisx,fiolesx,i,j)
                v = min(v, max_valeur(morpion_prisx,fiolesx,j,h,morpionsx[k].index(h),morpionsx,parties_j1x,parties_j2x,parties_nulsx,alpha, beta))
                if v <= alpha:
                    return v
                beta = min(beta, v)
        return v
    best_score = -10000
    beta = 10000
    for i in morpionsx[r]:
        if i not in morpion_prisx:
            morpion_prisx,fiolesx,jx=after_move(morpion_prisx,fiolesx,i,jx)
            v = min_valeur(morpion_prisx,fiolesx,jx,i,morpionsx[r].index(i),morpionsx,parties_j1x,parties_j2x,parties_nulsx,best_score, beta)
            if v > best_score :
                best_score = v
                best_action = i
    return r, morpionsx[r].index(best_action)