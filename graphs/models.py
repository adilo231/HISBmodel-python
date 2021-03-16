import numpy as np
from networkx.readwrite import json_graph
import networkx as nx
import matplotlib.pyplot as plt
import random
import os
import time
import threading
import multiprocessing
def IC(Networkx_Graph,Seed_Set,Probability):
    spread = []
    new_active, Ans = Seed_Set[:], Seed_Set[:]
    spread.append(new_active)
    while new_active:
        #Getting neighbour nodes of newly activate node
        targets = Neighbour_finder(Networkx_Graph,new_active)
        #Calculating if any nodes of those neighbours can be activated, if yes add them to new_ones.
        success = np.random.uniform(0,1,len(targets)) < Probability
        new_ones = list(np.extract(success, sorted(targets)))
        #Checking which ones in new_ones are not in our Ans...only adding them to our Ans so that no duplicate in Ans.
        new_active = list(set(new_ones) - set(Ans))
        Ans += new_active
        spread.append(new_active)
    
    return spread

def LT(Networkx_Graph,Seed_Set,Probability):
    new_active = Seed_Set[:]
    infected=[]
    infected.append(new_active)
    for each in new_active:
        Networkx_Graph.nodes[each]['infected']='true'
    while new_active:
        targets = Neighbour_finder(Networkx_Graph,new_active)
        new_active=list()
        for eachi in targets:  
            if(Networkx_Graph.nodes[eachi]['infected']=='false'):
                #+1 to count the number of neighbors who are infected
                Networkx_Graph.nodes[eachi]['value']+=1 
                NbrOf_neighobrs=len(set(Networkx_Graph.neighbors(eachi)))
                #if the proportion of infected neighbors is greater than threshold, the node will be infected
                if(((Networkx_Graph.nodes[eachi]['value'])/NbrOf_neighobrs)>Probability):
                    Networkx_Graph.nodes[eachi]['infected']='true'
                    new_active.append(eachi)            
        infected.append(new_active) 
       

    return infected 
    
def Neighbour_finder(g,new_active):
    
    targets = []
    for node in new_active:
        targets += g.neighbors(node)
    return(targets)

def HISBmodel (Graph,Seed_Set,Opinion_Set,Statistical,paramaters):

    #Opinion:normal/denying/supporting
    #State:non_infected/infected/spreaders 
    #Statistical:{'NonInfected':NbrOFnodes,'Infected':**,'Spreaders':**,OpinionDenying':**,'OpinionSupporting':**,'RumorPopularity':**}
    
    ListInfectedNodes=Seed_Set[:]
    Opinion_Set=Opinion_Set[:]
    time=0.125
    Probability=0.2
    i=0
    #Initialis Parameters----------------------------
    #-------------------------
    Nbr_Spreaders=len(ListInfectedNodes)

    Nbr_nonInfected=len(Graph.nodes)

    Nbr_Infected=0
    OpinionDenying=0
    OpinionSupporting=0
    RumorPopularity=0
    InitParameters(Graph,paramaters)
   
    for each  in ListInfectedNodes:
        Graph.nodes[each]['Infetime']=0.125 
        Graph.nodes[each]['state']='spreaders'
        Graph.nodes[each]['AccpR']+=1
        RumorPopularity+=Graph.nodes[each]['degre']
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
    Statistical.append({'NonInfected':Nbr_nonInfected,'Infected':Nbr_Infected,'Spreaders':Nbr_Spreaders,'OpinionDenying':OpinionDenying,'OpinionSupporting':OpinionSupporting,'RumorPopularity':RumorPopularity,'graph':Graph})
    #----------------------
    #if the list is empty we stop the propagation
    
    while ListInfectedNodes: 
      RumorPopularity = 0
      Nbr_Spreaders = 0
      L=len(ListInfectedNodes)
      
      for X in reversed(range(0,L)):
        
        id = ListInfectedNodes[X]
        
        #relative time of rumor spreading
        RelativeTime = time - Graph.nodes[id]['Infetime'] 
        if (np.exp(-RelativeTime * Graph.nodes[id]['beta']) < 0.2) :
          ListInfectedNodes.pop(X)
          Graph.nodes[id]['state'] = "infected"

        else:
            #atrraction of nodes
            ActualAttraction = np.exp(-RelativeTime * Graph.nodes[id]['beta']) * np.abs(np.sin((RelativeTime * Graph.nodes[id]['omega'] )+ Graph.nodes[id]['delta']))
            
            RumorPopularity += ActualAttraction * Graph.nodes[id]['degre']
            #rumor spreading
            if (np.random.random_sample()<=ActualAttraction):
                Nbr_Spreaders+=1
               
                #Calculating if any nodes of those neighbours can be activated, if yes add them to new_ones.
                success = np.random.uniform(0,1,len(Graph.nodes[id]['neighbors'])) < Probability #choic alpha nodes
                new_ones = list(np.extract(success, sorted(Graph.nodes[id]['neighbors'])))
                Graph.nodes[id]['SendR']+=len(new_ones)
                #Sending Rumor
                for each in new_ones:
                    #Accepted Rumor Probability 
                    AccepR = Graph.nodes[id]['degre']/ (Graph.nodes[id]['degre'] + Graph.nodes[each]['degre'])*0.3
                    if (np.random.random_sample()<=AccepR):
                        Graph.nodes[each]['AccpR']+=1

                        if (Graph.nodes[each]['Infetime']==0 ):
                            Nbr_Infected+=1



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
                        elif (Graph.nodes[each]['opinion']=="denying"):
                            Graph.nodes[each]['Accp_NegR']+=1
                        
                        #updateOpinion(id)
                if (Graph.nodes[id]['opinion']=="denying"):
                    OpinionDenying-=1
                else:
                    OpinionSupporting-=1
                Graph.nodes[id]['opinion']= updateOpinion(jug=Graph.nodes[id]['jug'],Accpet_NegR=Graph.nodes[id]['Accp_NegR'],Nbr_OF_R=Graph.nodes[id]['AccpR'])
                if (Graph.nodes[id]['opinion']=="denying"):
                    OpinionDenying+=1
                else:
                    OpinionSupporting+=1       
      
      #save each step to send it to viewing later
      Statistical.append({'NonInfected':Nbr_nonInfected,'Infected':Nbr_Infected,'Spreaders':Nbr_Spreaders,'OpinionDenying':OpinionDenying,'OpinionSupporting':OpinionSupporting,'RumorPopularity':RumorPopularity,'graph':0})
      time += 0.125;
    
    
     
    
def InitParameters(Graph,parameters):
    #Individual back ground knowledge:Beta
    #Forgetting and remembering factore:Omega
    #Hesitating factore:Deleta
    #Subjective judjement:Jug
  
    for node in Graph.nodes:
       Graph.nodes[node]['omega']=Inclusive(parameters[0]['Omega_min'],parameters[0]['Omega_max'])
       Graph.nodes[node]['beta']=Inclusive(parameters[0]['Beta_min'],parameters[0]['Beta_max'])
       Graph.nodes[node]['delta']=Inclusive(parameters[0]['Delta_min'],parameters[0]['Delta_max'])
       Graph.nodes[node]['jug']=Inclusive(parameters[0]['Jug_min'],parameters[0]['Jug_max'])


def Inclusive(min,max):
   
   b= ((np.random.random_sample()*(max - min )) + min)
    
   return b

def updateOpinion(jug,Accpet_NegR,Nbr_OF_R):
    opinion=jug*(Accpet_NegR / Nbr_OF_R);
    if(np.random.random_sample()<= opinion):
        return 'denying'
    else:
        return 'supporting'

def Small_World_networks(N=300,K=10,P=0.3):
    
    #Watts_strogatz graph
    #N=number of nodes
    #K=Each node is joined with its k nearest neighbors in a ring topology(anneau).
    #P=The probability of rewiring each edge(Probabilite de remplace les arretes)
    if(N is None):
        N=300
    if(K is None ):
        K=10
    if(P is None):
        P=0.5
    g= nx.watts_strogatz_graph(N,K,P)
    return graphe_TO_json(g)
def graphe_TO_json(g):
    
    data =  json_graph.node_link_data(g, {"link": "links", "source": "source", "target": "target","weight":"weight"})
    data['nodes'] = [ {"id": i,"state":"non_infected","opinion":"normal","beta":0,"omega":0,"delta":0,"jug":0,"Infetime":0,"AccpR":0,"SendR":0,"Accp_NegR":0,"value":0,"infected":'false',"degre":g.degree[i],"neighbors":[n for n in g.neighbors(i)]} for i in range(len(data['nodes'])) ]
    data['links'] = [ {"source":u,"target":v,"weight":(g.degree[u]+g.degree[v])/2} for u,v in g.edges ]
    return data
def geneList_Infectede(Listinfected,Listopinion,N,percentage):
    #10% of Popularity is infected 
    Nbr_OF_ndodesI=int(N*percentage/100)
    List=random.sample(range(0, N), Nbr_OF_ndodesI)
    opinion=np.random.uniform(0,1,Nbr_OF_ndodesI)
    for each in range(Nbr_OF_ndodesI):
        Listinfected.append(List[each])
        if opinion[each]<=0.5:
           Listopinion.append('denying')
        else:
            Listopinion.append('supporting')
    
  


def parameters(parameter):
    Beta_min= round(random.uniform(0.1, 6.0), 1)
    Beta_max=Beta_min+ round(random.uniform(0.0, 4.0), 1)
    Omega_min= round(random.uniform(0.1, 6.0), 1)
    Omega_max=Omega_min+round(random.uniform(0.0, 4.0), 1)
    Delta_min= round(random.uniform(0.1, 6.0), 1)
    Delta_max=Delta_min+ round(random.uniform(0.0, 4.0), 1)
    Jug_min=round(random.uniform(0.1, 6.0), 1)
    Jug_max=Jug_min+ round(random.uniform(0.0, 4.0), 1)
    parameter.append({'Beta_min':Beta_min,'Beta_max':Beta_max,'Omega_min':Omega_min,'Omega_max':Omega_max,'Delta_min':Delta_min,'Delta_max':Delta_max,'Jug_min':Jug_min,'Jug_max':Jug_max})
def Start(Graph):
    Statistical=[]
    parameter=[]
    ListInfected=[]
    Listopinion=[]
    #X% of Popularity is infected 
    geneList_Infectede(ListInfected,Listopinion,len(Graph.nodes),5)
    parameters(parameter)
    HISBmodel(Graph,ListInfected,Listopinion,Statistical,parameter)
    y1=[]
    y2=[]
    y3=[]
    y4=[]
    y5=[]
    for i in range(0,len(Statistical)):
        y1.append(Statistical[i]['Infected'])
        y2.append(Statistical[i]['Spreaders'])
        y3.append(Statistical[i]['RumorPopularity'])
        y4.append(Statistical[i]['OpinionDenying'])
        y5.append(Statistical[i]['OpinionSupporting'])

    x1 = range(0,len(Statistical))
    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.suptitle('Iteration X')

    ax1.plot(x1, y1, '.-')
    ax1.set_ylabel('Infected')

    ax2.plot(x1, y2, '.-')
    ax2.set_xlabel('time (s)')
    ax2.set_ylabel('Sprreaders')
    
    fig2, (ax3,ax4) = plt.subplots(2, 1)
    fig2.suptitle('Iteration X')
    ax3.plot(x1, y3, '.-')
    ax3.set_xlabel('time (s)')
    ax3.set_ylabel('RumorPopularity')

    ax4.plot(x1, y4, 'r-',x1,y5,'g--')
    ax4.set_xlabel('time (s)')
    ax4.set_ylabel('OpinionDenying')

    plt.show()   

#Number of nodes
N=500
#gene graph
g=json_graph.node_link_graph(Small_World_networks(N))


    
NUM_WORKERS = 4
start_time = time.time()
processes = [multiprocessing.Process(target=Start(Graph=g)) for _ in range(NUM_WORKERS)]
[process.start() for process in processes]
[process.join() for process in processes]
end_time = time.time() 
print("Parallel time=", end_time - start_time)
