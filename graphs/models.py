#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  4 09:18:28 2021

@author: mac
"""

import numpy as np
from networkx.readwrite import json_graph
import networkx as nx
import matplotlib.pyplot as plt
import random
import time
#from matplotlib.ticker import NullFormatter  
import multiprocessing 
from multiprocessing import Manager
import math
def Neighbour_finder(g,new_active):
    
    targets = []
    for node in new_active:
        targets += g.neighbors(node)
    return(targets)
def HISBmodel (Graph,Seed_Set,Opinion_Set,Statistical,paramater,K,Tdet,method):
    
    #Opinion:normal/denying/supporting
    #State:non_infected/infected/spreaders 
    #Statistical:{'NonInfected':NbrOFnodes,'Infected':**,'Spreaders':**,OpinionDenying':**,'OpinionSupporting':**,'RumorPopularity':**}
    bl=0
    ListInfectedNodes=Seed_Set[:]
    Opinion_Set=Opinion_Set[:]
    time=0.125
    Probability=0.20
    i=0
    #Initialis Parameters----------------------------
    #-------------------------
    Nbr_Spreaders=len(ListInfectedNodes)
    Nbr_nonInfected=len(Graph.nodes)
    Nbr_Infected=0
    OpinionDenying=0
    OpinionSupporting=0
    RumorPopularity=0
    InitParameters(Graph,paramater)
    ''' if(L_protector!=None):
       for each  in L_protector:
        Graph.nodes[each]['jug']=1'''
   
    for each  in ListInfectedNodes:
        Graph.nodes[each]['Infetime']=0.125 
        Graph.nodes[each]['state']='spreaders'
        Graph.nodes[each]['AccpR']+=1
        
        RumorPopularity+=Graph.nodes[each]['degree']
        Nbr_Infected+=1
        Nbr_nonInfected-=1
        if (Opinion_Set[i]=='denying'):

            Graph.nodes[each]['opinion']='denying'
            Graph.nodes[each]['Accp_NegR']+=1
            OpinionDenying+=1
        else:
          Graph.nodes[each]['opinion']='supporting'
          OpinionSupporting+=1
        i+=1
        
    
    #------------------------------
    Statistical.append({'NonInfected':Nbr_nonInfected,'Infected':Nbr_Infected,'Spreaders':Nbr_Spreaders,'OpinionDenying':OpinionDenying,'OpinionSupporting':OpinionSupporting,'RumorPopularity':RumorPopularity,'graph':0})
    #----------------------
    #if the list is empty we stop the propagation
    
    while ListInfectedNodes: 
      RumorPopularity = 0
      Nbr_Spreaders = 0
      L=len(ListInfectedNodes)
      #print(L)
      for X in reversed(range(0,L)):
        
        id = ListInfectedNodes[X]
        
        #relative time of rumor spreading
        RelativeTime = time - Graph.nodes[id]['Infetime'] 
        if (np.exp(-RelativeTime * Graph.nodes[id]['beta']) < 0.15) :
          ListInfectedNodes.pop(X)
          Graph.nodes[id]['state'] = "infected"
          
              

        else:
            #atrraction of nodes
            ActualAttraction = np.exp(-RelativeTime * Graph.nodes[id]['beta']) * np.abs(np.sin((RelativeTime * Graph.nodes[id]['omega'] )+ Graph.nodes[id]['delta']))
            
            RumorPopularity += ActualAttraction * Graph.nodes[id]['degree']
            #rumor spreading
            
            c=np.random.random_sample()
            
            if (c<=ActualAttraction):
                Nbr_Spreaders+=1
               
                #Calculating if any nodes of those neighbours can be activated, if yes add them to new_ones.
                success = np.random.uniform(0,1,len(Graph.nodes[id]['neighbors'])) < Probability #choic alpha nodes
                new_ones = list(np.extract(success, sorted(Graph.nodes[id]['neighbors'])))
                
                Graph.nodes[id]['SendR']+=len(new_ones)
                
                #Sending Rumor
                for each in new_ones:
                    #Accepted Rumor Probability 
                    AccepR = Graph.nodes[id]['degree']/ (Graph.nodes[id]['degree'] + Graph.nodes[each]['degree'])*0.3
                    if (Graph.nodes[each]['blocked'] =='false'):
                        if(np.random.random_sample()<=AccepR):
                        
                            Graph.nodes[each]['AccpR']+=1
    
                            if (Graph.nodes[each]['Infetime']==0 ):
                                Nbr_Infected+=1
                                Nbr_nonInfected-=1
                                Graph.nodes[each]['Infetime'] =time
                                Graph.nodes[each]['opinion'] =Graph.nodes[id]['opinion']
                                Graph.nodes[id]['state']='spreaders'
                                ListInfectedNodes.append(each)
                                if (Graph.nodes[each]['opinion']=="denying"):
                                    #negativ opinion
                                    Graph.nodes[each]['Accp_NegR']+=1
                                    OpinionDenying+=1
                                else:
                                     OpinionSupporting+=1
                            elif (Graph.nodes[id]['opinion']=="denying"):
                                Graph.nodes[each]['Accp_NegR']+=1
                    
                   # else:
                        #print('le noeud',each,'is blocked')
                        #updateOpinion(id)'''
                if (Graph.nodes[id]['opinion']=="denying"):
                    OpinionDenying-=1
                else:
                    OpinionSupporting-=1
                Graph.nodes[id]['opinion']= updateOpinion(jug=Graph.nodes[id]['jug'],Accpet_NegR=Graph.nodes[id]['Accp_NegR'],Nbr_OF_R=Graph.nodes[id]['AccpR'],Role=Graph.nodes[id]['Protector'])
                if (Graph.nodes[id]['opinion']=="supporting"):
                    
                    OpinionSupporting+=1
                else:
                    
                    OpinionDenying+=1       
      
      #save each step to send it to viewing later
      Statistical.append({'NonInfected':Nbr_nonInfected,'Infected':Nbr_Infected,'Spreaders':Nbr_Spreaders,'OpinionDenying':OpinionDenying,'OpinionSupporting':OpinionSupporting,'RumorPopularity':RumorPopularity,'graph':0})
      if time >=Tdet*0.125 and bl<K  and method != 'NP' :
          print(method," At time:", time, "blocked nodes Nbr:", bl)
          Nodes=len(Graph.nodes)
          
          p=K-bl
          if (method=='BNLS'):
              Random_Blocking_nodes(Graph, p)
              bl=len(blocked(Graph))
          if (method=='BNLSM'):
              Degree_MAX_Blocking_nodes(Graph,p)
              bl=len(blocked(Graph))
          if (method=='BNLSCen'):
              Centrality_Blocking_nodes(Graph,p)
              bl=len(blocked(Graph))
          if (method=='BNLSBeta'):
              Beta_Blocking_nodes(Graph,p)
              bl=len(blocked(Graph))
          if (method=='BNLSBetaD'):
              BetaD_Blocking_nodes(Graph,p)
              bl=len(blocked(Graph))

              
          elif method=='TCS':
              Random_TRuth_comp(Graph, p)
              Liste_protector=Protector(Graph)
              taille=len(Liste_protector)
             # print(taille)
              for i in range(taille):
                  Graph.nodes[Liste_protector[i]]['Infetime'] =time
                  Graph.nodes[Liste_protector[i]]['opinion']=="denying"
                  Graph.nodes[Liste_protector[i]]['state']='spreaders'
                  Graph.nodes[Liste_protector[i]]['AccpR']+=1
                  Graph.nodes[Liste_protector[i]]['Accp_NegR']+=1
                  ListInfectedNodes.append(Liste_protector[i])
              bl=len(Liste_protector)
          elif method=='TCSM':
             MaxDegree_TRuth_comp(Graph, p)
             Liste_protector=Protector(Graph)
             taille=len(Liste_protector)
             for i in range(taille):
                 ListInfectedNodes.append(Liste_protector[i])
                 Graph.nodes[Liste_protector[i]]['Infetime'] =time
                 Graph.nodes[Liste_protector[i]]['opinion']=="denying"
                 Graph.nodes[Liste_protector[i]]['state']='spreaders'
                 Graph.nodes[Liste_protector[i]]['AccpR']+=1
                 Graph.nodes[Liste_protector[i]]['Accp_NegR']+=1
             bl=len(Liste_protector)
          elif method=='TCSCen':
             Centrality_TRuth_comp(Graph, p)
             Liste_protector=Protector(Graph)
             taille=len(Liste_protector)
             for i in range(taille):
                 ListInfectedNodes.append(Liste_protector[i])
                 Graph.nodes[Liste_protector[i]]['Infetime'] =time
                 Graph.nodes[Liste_protector[i]]['opinion']=="denying"

                 Graph.nodes[Liste_protector[i]]['state']='spreaders'
                 Graph.nodes[Liste_protector[i]]['AccpR']+=1
                 Graph.nodes[Liste_protector[i]]['Accp_NegR']+=1
             bl=len(Liste_protector)
          elif method=='TCSBeta':
             Beta_TRuth_comp(Graph, p)
             Liste_protector=Protector(Graph)
             taille=len(Liste_protector)
             for i in range(taille):
                 ListInfectedNodes.append(Liste_protector[i])
                 Graph.nodes[Liste_protector[i]]['Infetime'] =time
                 Graph.nodes[Liste_protector[i]]['opinion']=="denying"
                 Graph.nodes[Liste_protector[i]]['state']='spreaders'
                 Graph.nodes[Liste_protector[i]]['AccpR']+=1
                 Graph.nodes[Liste_protector[i]]['Accp_NegR']+=1
             bl=len(Liste_protector)
          elif method=='TCSBetaD':
             BetaD_TRuth_comp(Graph, p)
             Liste_protector=Protector(Graph)
             taille=len(Liste_protector)
             for i in range(taille):
                 ListInfectedNodes.append(Liste_protector[i])
                 Graph.nodes[Liste_protector[i]]['Infetime'] =time
                 Graph.nodes[Liste_protector[i]]['opinion']=="denying"
                 Graph.nodes[Liste_protector[i]]['state']='spreaders'
                 Graph.nodes[Liste_protector[i]]['AccpR']+=1
                 Graph.nodes[Liste_protector[i]]['Accp_NegR']+=1
             bl=len(Liste_protector)
          print(method," At time:", time, "blocked nodes Nbr:", bl)
            
              
      time += 0.25;   
def InitParameters(Graph,parameters):
    #Individual back ground knowledge:Beta
    #Forgetting and remembering factore:Omega
    #Hesitating factore:Deleta
    #Subjective judjement:Jug
  
    for node in Graph.nodes:
       Graph.nodes[node]['omega']=Inclusive(parameters[0]['omega_min'],parameters[0]['omega_max'])
       Graph.nodes[node]['beta']=Inclusive(parameters[0]['beta_min'],parameters[0]['beta_max'])
       Graph.nodes[node]['delta']=Inclusive(parameters[0]['delta_min'],parameters[0]['delta_max'])
       Graph.nodes[node]['jug']=Inclusive(parameters[0]['Jug_min'],parameters[0]['Jug_max'])
def Inclusive(min,max):
   
   b= ((np.random.random_sample()*(max - min )) + min)
    
   return b
def updateOpinion(jug,Accpet_NegR,Nbr_OF_R,Role): 
    if(Role=='True'):
       return 'denying' 
   
    opinion=jug
    if Accpet_NegR != 0:
        opinion*=(Accpet_NegR / Nbr_OF_R)
   
    
    if(np.random.random_sample()<= opinion):
        return 'denying'
    else:
        return 'supporting'
def graphe_TO_json(g):
    
    data =  json_graph.node_link_data(g,{"link": "links", "source": "source", "target": "target","weight":"weight"})
    data['nodes'] = [ {"id": i,"state":"non_infected","Protector":"false","opinion":"normal","beta":0,"omega":0,"delta":0,"jug":0,"Infetime":0,"AccpR":0,"SendR":0,"Accp_NegR":0,"value":0,"blocked":'false',"degree":g.degree[i],"neighbors":[n for n in g.neighbors(i)]} for i in range(len(data['nodes'])) ]
    data['links'] = [ {"source":u,"target":v,"weight":(g.degree[u]+g.degree[v])/2} for u,v in g.edges ]
    return data
def geneList_Infectede(Listinfected,Listopinion,N,percentage):
    #10% of Popularity is infected 
    Nbr_OF_ndodesI=int(N*percentage/100)
    L=list(range(N))
    List=random.sample(L, Nbr_OF_ndodesI)
    opinion=np.random.uniform(0,1,Nbr_OF_ndodesI)
    for each in range(Nbr_OF_ndodesI):
        Listinfected.append(List[each])
        if opinion[each]<=0.2:
           Listopinion.append('denying')
        else:
            Listopinion.append('supporting')
            
def parameters(parameter,stepBeta=1,Beta=0.2,stepOmega=5.2,Omega=math.pi/3,stepDelta=0.65,Delta=math.pi/24,stepJug=0.6,Jug=0.1):
    Beta_max=Beta+stepBeta
    Omega_max=Omega +stepOmega
    Delta_max=Delta +stepDelta
    Jug_max=Jug+stepJug
    parameter.append({'beta_min':round(Beta,2),'beta_max':round(Beta_max,2),'omega_min':round(Omega,2),'omega_max':round(Omega_max,2),'delta_min':round(Delta,2),'delta_max':round(Delta_max,2),'Jug_min':round(Jug,2),'Jug_max':round(Jug_max,2)})
def Start(i,Graph,parameter,Stat,percentage,K,Tdet,method):
    
    for each in range(len(Graph.nodes)):
        Graph.nodes[each]['opinion']="normal"
        Graph.nodes[each]['Infetime']=0 
        Graph.nodes[each]['state']='non_infected'
        Graph.nodes[each]['Protector']='false'
        Graph.nodes[each]['blocked']='false'
        
    Statistical=[]
    ListInfected=[]
    Listopinion=[]
    #X% of Popularity is infected 
    geneList_Infectede(ListInfected,Listopinion,len(Graph.nodes),percentage)
   
    HISBmodel(Graph,ListInfected,Listopinion,Statistical,parameter,K,Tdet,method)  
    Stat.append(Statistical)    
    
    
def globalStat(S,Stat_Global,parameter,method):
    max=0
    Stat=[]
    for each in S:
        
        L=len(each)
        Stat.append(each)
        if(L>max):
            max=L
    for i in range(len(Stat)):
        L=len(Stat[i])
        Nbr_nonInfected=Stat[i][L-1]['NonInfected']
        Nbr_Infected=Stat[i][L-1]['Infected']
        Nbr_Spreaders=Stat[i][L-1]['Spreaders']
        OpinionDenying=Stat[i][L-1]['OpinionDenying']
        OpinionSupporting=Stat[i][L-1]['OpinionSupporting']
        RumorPopularity=Stat[i][L-1]['RumorPopularity']
        for j in range(L,max):
            Stat[i].append({'NonInfected':Nbr_nonInfected,'Infected':Nbr_Infected,'Spreaders':Nbr_Spreaders,'OpinionDenying':OpinionDenying,'OpinionSupporting':OpinionSupporting,'RumorPopularity':RumorPopularity,'graph':0})       

    y1=[]
    y2=[]
    y3=[]
    y4=[]
    y5=[]   
    Len=len(Stat)
  
    for i in range(max):
        
        Infected=0
        Spreaders=0
        RumorPopularity=0
        OpinionDenying=0
        OpinionSupporting=0
        for each in Stat:           
            Infected+=(each[i]['Infected'])
            Spreaders+=(each[i]['Spreaders'])
            RumorPopularity+=(each[i]['RumorPopularity'])
            OpinionDenying+=(each[i]['OpinionDenying'])
            OpinionSupporting+=(each[i]['OpinionSupporting'])
        y1.append(Infected/Len)
        y2.append(Spreaders/Len)
        y3.append(RumorPopularity/Len)
        y4.append(OpinionDenying/Len)
        y5.append(OpinionSupporting/Len)
     

    Stat_Global.append({'Infected':y1,'Spreaders':y2,'RumorPopularity':y3,'OpinionDenying':y4,'OpinionSupporting':y5,'parameter':parameter,'max':max,'method':method})       
    #Number of nodes
def Display(Stat_Global,xx,title_fig,nb):
   #print(Stat_Global)
    Title=['BNLS','BNLSM','BNLSCen','BNLSBeta','BNLSBetaD',
       'TCS','TCSBeta','TCSM','TCSCen','TCSBetaD','NP']
    max=0
    Stat=[]
    Infected=[]
    para=[]
    for each in Stat_Global:
        L=each['max']
        #print(L,each['Infected'])
        
        para.append(each['method'])
        metho=str(each['method'])
        if metho.startswith('TCS'):
            Infected.append(each['OpinionSupporting'][L-1]/Nodes)
        else:
            Infected.append(each['Infected'][L-1]/Nodes)
                
        
        Stat.append(each)
        if(L>max):
            max=L
    for each in Stat:
        L=each['max']
        if (L<max):
            Nbr_Infected=each['Infected'][L-1]
            Nbr_Spreaders=each['Spreaders'][L-1]
            OpinionDenying=each['OpinionDenying'][L-1]
            OpinionSupporting=each['OpinionSupporting'][L-1]
            RumorPopularity=each['RumorPopularity'][L-1]
            for j in range(L,max):
                each['Infected'].append(Nbr_Infected)
                each['Spreaders'].append(Nbr_Spreaders)
                each['OpinionDenying'].append(OpinionDenying)
                each['OpinionSupporting'].append(OpinionSupporting)
                each['RumorPopularity'].append(RumorPopularity)
    
    pro=int(max/50)
    
    for each in Stat:
            for j in reversed(range(max)):
                d=j%pro
                if(d!=0):
                    each['Infected'].pop(j)
                    each['Spreaders'].pop(j)
                    each['OpinionDenying'].pop(j)
                    each['OpinionSupporting'].pop(j)
                    each['RumorPopularity'].pop(j)

    for each in Stat:
            for j in reversed(range(10)):
                    each['Infected'].pop(40+j)
                    each['Spreaders'].pop(40+j)
                    each['OpinionDenying'].pop(40+j)
                    each['OpinionSupporting'].pop(40+j)
                    each['RumorPopularity'].pop(40+j)
    x = range(0,len(Stat[0]['Infected']))
    x=np.array(x)*pro
    

    # plot 
    
    type=['x','*','p','8','h','H','.','+','4','1','2','3']
    
    #Infected
    plt.figure(num=xx)
    plt.subplot()
    #k="{}:{},{}]" 
    k="{}" 
    for infected,j in zip( Stat,range(len(Stat))):
      quotients = [number /Nodes  for number in infected["Infected"]]
      plt.plot(x,quotients,marker=type[j],markersize=7,linewidth=1,label=k.format(Title[j]))
    plt.legend(fontsize=12) 

    plt.xlabel('Temps',fontsize=10)
    plt.ylabel('Nombre des individues')
    plt.grid(True)
    plt.savefig(title_fig+'infected.pdf',dpi=50)
    # RumorPopularity
    xx+=1
    plt.figure(num=xx)
    plt.subplot()
    #k="{}:{},{}]" 
    k="{}" 
    for infected,j in zip( Stat,range(len(Stat))):
      quotients = [number /Nodes  for number in infected["RumorPopularity"]]
      plt.plot(x, quotients,marker=type[j],markersize=6,linewidth=1,label=k.format(Title[j]))
    plt.legend(fontsize=12) 
    plt.xlabel('Temps')
    plt.ylabel('Nombre des individues')
    plt.grid(True)
    plt.title("popularity")
    plt.savefig(title_fig+'RumorPopularity.pdf',dpi=20)
    
    #Spreaders
    xx+=1
    plt.figure(num=xx)
    plt.subplot()
    #k="{}:{},{}]" 
    k="{}" 
    for infected ,j in zip( Stat,range(len(Stat))):
      quotients = [number /Nodes  for number in infected["Spreaders"]]
      plt.plot(x, quotients,marker=type[j],markersize=6,linewidth=1,label=k.format(Title[j]))
    
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.title("Spreaders")
    plt.xlabel('Temps')
    plt.ylabel('Nombre des individues')
    plt.savefig(title_fig+'Spreaders.pdf',dpi=20)
   
    
   # # Opinion
   #  xx+=1
   #  plt.figure(num=xx)
   #  plt.subplot()
   #  #k="{}:{},{}]" 
   #  k="{}" 
   #  for infected,j in zip( Stat,range(len(Stat))):
   #    quotients = [number /Nodes  for number in infected["OpinionDenying"]]
      
   #    plt.plot(x, quotients,marker=type[j],markersize=6,linewidth=2,label=k.format(Title[j]))
   #  plt.legend(fontsize=12) 
   #  plt.grid(True)
   #  plt.xlabel('Temps')
   #  plt.ylabel('Nombre des individues')
   #  plt.savefig(title_fig+'OpinionDenying.pdf',dpi=20)
    

    # Opinion
    xx+=1
    plt.figure(num=xx)
    plt.subplot()
    #k="{}:{},{}]" 
    k="{}" 
    for infected,j in zip( Stat,range(len(Stat))):
      quotients = [number /Nodes  for number in infected["OpinionSupporting"]]
      plt.plot(x, quotients,marker=type[j],markersize=6,linewidth=2,label=k.format(Title[j]))
   
    plt.legend(fontsize=12) 
    plt.grid(True)
    plt.xlabel('Temps')
    plt.ylabel('Nombre des individues')
    plt.title("Supporting")
    plt.savefig(title_fig+'OpinionSupporting.pdf',dpi=20)
    
    # Format the minor tick labels of the y-axis into empty strings with
    # `NullFormatter`, to avoid cumbering the axis with too many labels.

    xx+=1
    plt.figure(num=xx) 
    plt.subplot()      
    plt.plot(para,Infected,'bo')
    plt.grid(True)
    plt.xlabel(Title)
    plt.title("infected")
    plt.ylabel('Nombre des individues')
    plt.savefig(title_fig+'nodes.pdf',dpi=20) 
    
def Simulation(index,graph,Stat_Global,percentage):
     Beta=0.2
     with Manager() as manager:
        Stat=manager.list()  
        parameter=[]
        parameters(parameter,Beta=Beta+index/10)
        start_time = time.time()  
        processes=[multiprocessing.Process(target=Start,args=(i,index,graph,parameter,Stat,percentage))for i in range(10)] 
        [process.start() for process in processes] 
        [process.join() for process in processes]
        end_time = time.time() 
        print("Parallel xx time=", end_time - start_time)
        globalStat(Stat,Stat_Global,parameter)
#gene graph
def Random_networks ( N=300 ,P=0.3):
    # Erdős-Rényi graph
    # number of nodes
    # expected number of partners
    
    g = nx.gnp_random_graph(N, P)  
    return graphe_TO_json(g)
def Small_World_networks(N=300,K=10,P=0.3):
    
    #Watts_strogatz graph
    #N=number of nodes
    #K=Each node is joined with its k nearest neighbors in a ring topology(anneau).
    #P=The probability of rewiring each edge(Probabilite de remplace les arretes)
    g= nx.watts_strogatz_graph(N,K,P)
    return graphe_TO_json(g)
def Scale_free_networks (N=300,M=10):
    #Barabasi_albert graph
    #N= Number of nodes
    #M= Number of edges to attach from a new node to existing nodes
    g=nx.barabasi_albert_graph(N,M)
    return graphe_TO_json(g)
def facebook_graph():
    FielName="facebook.txt"
    Graphtype=nx.Graph()
    g= nx.read_edgelist(FielName,create_using=Graphtype,nodetype=int)
    
    return graphe_TO_json(g) 
def search_spreaders(G,sp):
    
    l=len(G.nodes)
    for i in range (l):
        if ( G.nodes[i]['state']=='spreaders'):
          sp.append(i)
                
def neighbor(Spreaders,g):
    neighb=[]
    MaxD=[]
    Cente=[]
    beta=[]
    betaD=[]
    Cent=((nx.degree_centrality(g)))
    
    for i in Spreaders:
        n=g.neighbors(i)
        
        for j in n:
          
          if g.nodes[j]['state'] =='non_infected':
              if j not in neighb :
                  neighb.append(j)
                  Cente.append(Cent[j])
                  MaxD.append(g.nodes[j]['degree'])
                  beta.append(g.nodes[j]['beta'])
                  betaD.append(g.nodes[j]['degree']/g.nodes[j]['beta'])
           
              
   
    return neighb,MaxD,Cente,beta,betaD
def simulation_strategy(x,K,Tdet,method,G):
   
    with Manager() as manager:
        Stat_Global=manager.list() 
        v=0
        for met in method :
            print(met)
            g=G[v]
            with Manager() as manager:
                Stat=manager.list()  
                parameter=[]
                parameters(parameter)
                start_time = time.time()  
                processes=[multiprocessing.Process(target=Start,args=(i,g,parameter,Stat,percentage,K,Tdet,met))for i in range(NumOFsumi)] 
                
                [process.start() for process in processes] 
                [process.join() for process in processes]
                end_time = time.time() 
                print("Parallel xx time=", end_time - start_time)
                globalStat(Stat,Stat_Global,parameter,met)
            v+=1     
        Display(Stat_Global,x,'NBLS',Nodes)
def Iterative():
    start_time = time.time()  
    StatI=[]

    for i in range(6):
        parameter=[]
        parameters(parameter,Omega=0.2+i/10)
        Stat=[]
        start_time1 = time.time() 
        for j in range(50):
            Start(i,j,g,parameter,Stat,percentage)
        end_time1 = time.time()
        print("Serial xx time=", end_time1 - start_time1)
        globalStat(Stat,StatI,parameter)
    end_time = time.time()
    print("Serial time=", end_time - start_time)
    Display(StatI)
def Random_Blocking_nodes(Graphe,k):
    sp=[]
    search_spreaders(Graphe,sp)
    nb,d,cen,Bet,betaD=neighbor(sp,Graphe)
    size=len(nb)
    if k>size:
      k=size-1
    for i in range(k):
        s=random.randint(0, size-1)
        Graphe.nodes[nb[s]]['blocked']='True'
        nb.pop(s)
        size-=1
       
def Degree_MAX(G,K,nb):
    L=[]
    
  
    for i in range(len(nb)):
        L.append(G.nodes[i]['degree'])

    return L
def Degree_MAX_Blocking_nodes(G,k):
    
    sp=[]
   
    search_spreaders(G,sp)
   
    nb,DNode,cen,Bet,betaD=neighbor(sp,G)
    

    for i in range(k):
            
            ID = DNode.index(max(DNode))
            G.nodes[nb[ID]]['blocked']='True'
            DNode.pop(ID)
            nb.pop(ID)
            
def Centrality_Blocking_nodes(G,k):
    
    sp=[]
   
    search_spreaders(G,sp)
    nb,DNode,cen,Bet,betaD=neighbor(sp,G)
    for i in range(k):
            
            ID = cen.index(max(cen))
            G.nodes[nb[ID]]['blocked']='True'
            cen.pop(ID)
            nb.pop(ID)         
def Beta_Blocking_nodes(G,k):
    
    sp=[]
   
    search_spreaders(G,sp)
   
    nb,DNode,cen,Bet,betaD=neighbor(sp,G)
    

    for i in range(k):
            
            ID = Bet.index(min(Bet))
            G.nodes[nb[ID]]['blocked']='True'
            Bet.pop(ID)
            nb.pop(ID)         
def BetaD_Blocking_nodes(G,k):
    
    sp=[]
   
    search_spreaders(G,sp)
   
    nb,DNode,cen,Bet,betaD=neighbor(sp,G)
    

    for i in range(k):
            
            ID = betaD.index(max(betaD))
            G.nodes[nb[ID]]['blocked']='True'
            betaD.pop(ID)
            nb.pop(ID)   

def Random_TRuth_comp(Graphe,k):
    sp=[]
    search_spreaders(Graphe,sp)
    nb,d,cen,Bet,betaD=neighbor(sp,Graphe)
    size=len(nb)
    if k > size :
       k=size-1
    for i in range(k):
        s=random.randint(0, size-1)
        Graphe.nodes[nb[s]]['Protector']='True'
        Graphe.nodes[nb[s]]['state']='infected'
        nb.pop(s)
        size-=1
def MaxDegree_TRuth_comp(Graphe,K):
    sp=[]
    search_spreaders(Graphe,sp)
    nb,d,cen,Bet,betaD=neighbor(sp,Graphe)
    size=len(nb)
    k=K
    if k > size :
       k=size-1
    for i in range(k):
        s = d.index(max(d))
        Graphe.nodes[nb[s]]['Protector']='True'
        Graphe.nodes[nb[s]]['state']='infected'
        nb.pop(s)
        d.pop(s)
def Centrality_TRuth_comp(Graphe,K):
    sp=[]
    search_spreaders(Graphe,sp)
   
    nb,d,cen,Bet,betaD=neighbor(sp,Graphe)
   
    size=len(nb)
    k=K
    if k > size :
       k=size-1
    for i in range(k):
        s = cen.index(max(cen))
        Graphe.nodes[nb[s]]['Protector']='True'
        Graphe.nodes[nb[s]]['state']='infected'
        nb.pop(s)
        cen.pop(s)
def Beta_TRuth_comp(Graphe,K):
    sp=[]
    search_spreaders(Graphe,sp)
    nb,d,bet,cen,betaD=neighbor(sp,Graphe)
    size=len(nb)
    k=K
    if k > size :
       k=size-1
    for i in range(k):
        s = cen.index(min(cen))
        Graphe.nodes[nb[s]]['Protector']='True'
        Graphe.nodes[nb[s]]['state']='infected'
        nb.pop(s)
        cen.pop(s)
def BetaD_TRuth_comp(Graphe,K):
    sp=[]
    search_spreaders(Graphe,sp)
    nb,d,bet,cen,betaD=neighbor(sp,Graphe)
    size=len(nb)
    k=K
    if k > size :
       k=size-1
    for i in range(k):
        s = betaD.index(max(betaD))
        Graphe.nodes[nb[s]]['Protector']='True'
        Graphe.nodes[nb[s]]['state']='infected'
        nb.pop(s)
        betaD.pop(s)


def blocked(G):
    
    L=[]
    for i in range (len(G.nodes)):
        if(G.nodes[i]['blocked']=='True'):
            L.append(i)           
    return L
def Protector(G):  
    
    L=[]
    for i in range (len(G.nodes)):
        if(G.nodes[i]['Protector']=='True'):
            L.append(i)           
    return L
if __name__ == '__main__':
       # use net.Graph() for undirected graph

# How to read from a file. Note: if your egde weights are int, 
# change float to int.
   
    #Graph's Parametres 
    P=0.3
    K=100
    M=7
    nbb=0
   
    #g=json_graph.node_link_graph(Scale_free_networks(Nodes,M))
    #g=Scale_free_networks(Nodes,M)
    #g=json_graph.node_link_graph(Small_World_networks(Nodes,K,P))
    #g=json_graph.node_link_graph(Random_networks(Nodes,P))
    g=json_graph.node_link_graph(facebook_graph())
    
    #print(g.nodes[12]['neighbors'])
    G=[]
    m=['TCSCen']
    m=['BNLS','BNLSM','BNLSCen','BNLSBeta','BNLSBetaD',
       'TCS','TCSBeta','TCSM','TCSCen','TCSBetaD','NP']
    
    for i in range(len(m)):
        G.append(g)

    
    Nodes=len(g.nodes)
    static="Nodes :{},Edegs:{}."
    percentage=5 #1% of popularity" is infected 
    NumOFsumi=50
    beta=0.2
    omega=0
    juge=0.1
    delta=0
    K=int(Nodes*0.2)
    print(K)
    Tdet=1
    
   
  

    
    simulation_strategy(1,  K, Tdet, m,G)
    plt.show()
