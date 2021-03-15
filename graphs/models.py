import numpy as np
from networkx.readwrite import json_graph
import networkx as nx

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


def HISBmodel (Graph,Seed_Set,Opinion_Set,Beta_min=0.2,Beta_max=1.2,Omega_min=0.1,Omega_max=6,Delta_min=0.2,Delta_max=1.6,Jug_min=0.1,Jug_max=1):
    #Opinion:normal/denying/supporting
    #State:non_infected/infected/spreaders 
    #Statistical:{'NonInfected':NbrOFnodes,'Infected':**,'Spreaders':**,OpinionDenying':**,'OpinionSupporting':**,'RumorPopularity':**}
    Statistical=[]
    ListInfectedNodes=Seed_Set[:]
    Opinion_Set=Opinion_Set[:]
   

    time=0.125
    Probability=0.3
    i=0

   

    
    #Initialis Parameters----------------------------
    #-------------------------
    Nbr_Spreaders=len(ListInfectedNodes)
    Nbr_nonInfected=len(Graph.nodes)-Nbr_Spreaders
    Nbr_Infected=0
    OpinionDenying=0
    OpinionSupporting=0
    RumorPopularity=0
    Graph=InitParameters(Graph,Beta_min,Beta_max,Omega_min,Omega_max,Delta_min,Delta_max,Jug_min,Jug_max)
   
    for each  in ListInfectedNodes:
        Graph.nodes[each]['Infetime']=0.125 
        Graph.nodes[each]['state']='spreaders'
        Graph.nodes[each]['AccpR']+=1
        RumorPopularity+=Graph.nodes[each]['degre']
        if (Opinion_Set[i]=="denying"):
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
    while ListInfectedNodes: 
      RumorPopularity = 0
      Nbr_Spreaders = 0
      X=0

      for X in range(len(ListInfectedNodes)):
        id = ListInfectedNodes[X]
        #relative time of rumor spreading
        RelativeTime = time - Graph.nodes[id]['Infetime'] 
        if (np.exp(-RelativeTime * Graph.nodes[id]['beta']) < 0.1) :
          ListInfectedNodes.pop(X);
          Graph.nodes[id]['state'] = "infected"
          Nbr_Infected+=1
          Nbr_nonInfected-=1
        else:
            #atrraction of nodes
            ActualAttraction = np.exp(-RelativeTime * Graph.nodes[id]['beta']) * np.abs(np.sin(RelativeTime * Graph.nodes[id]['omega'] + Graph.nodes[id]['delta']))
            
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
                    AccepR = Graph.nodes[id]['degre']/ (Graph.nodes[id]['degre'] + Graph.nodes[each]['degre'])
                    if (np.random.random_sample()<=AccepR):
                        Graph.nodes[each]['AccpR']+=1

                        if (Graph.nodes[each]['Infetime']==0 ):
                            Graph.nodes[each]['Infetime'] =time
                            Graph.nodes[each]['opinion'] =Graph.nodes[id]['opinion']
                            Graph.nodes[id]['state']='spreaders'
                            ListInfectedNodes.append(each)
                            if (Graph.nodes[each]['opinion']=="denying"):
                                Graph.nodes[each]['Accp_NegR']+=1
                                OpinionDenying+=1
                            else:
                                 OpinionSupporting+=1
                        elif (Graph.nodes[each]['opinion']=="denying"):
                            Graph.nodes[each]['Accp_NegR']+=1
                        #updateOpinion(id)

        time += 0.125;                      
     
      
      Statistical.append({'NonInfected':Nbr_nonInfected,'Infected':Nbr_Infected,'Spreaders':Nbr_Spreaders,'OpinionDenying':OpinionDenying,'OpinionSupporting':OpinionSupporting,'RumorPopularity':RumorPopularity,'graph':Graph})
      time += 0.125;
    
    
    for node in Graph.nodes:
       print (Graph.nodes[node]) 
    return None
    
def InitParameters(Graph,Beta_min,Beta_max,Omega_min,Omega_max,Delta_min,Delta_max,Jug_min,Jug_max):
    #Individual back ground knowledge:Beta
    #Forgetting and remembering factore:Omega
    #Hesitating factore:Deleta
    #Subjective judjement:Jug
    g=Graph
    for node in g.nodes:
       Graph.nodes[node]['omega']=Inclusive(Omega_min,Omega_max)
       Graph.nodes[node]['beta']=Inclusive(Beta_min,Beta_max)
       Graph.nodes[node]['delta']=Inclusive(Delta_min,Delta_max)
       Graph.nodes[node]['jug']=Inclusive(Jug_min,Jug_max)

    
  
    return g

def Inclusive(min,max):
  min = np.ceil(min)
  max = np.floor(max)
  return (np.floor(np.random.random_sample()*(max - min + 1)) + min)/100

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

g=json_graph.node_link_graph(Small_World_networks(100))
#HISBmodel(g,[1,2,3,8,12],['supporting','supporting','denying','denying','supporting'])
#print(Inclusive(0.2,6.2))
s=[{'s':50,'i':0}]
x=[1,2,5]
x.pop(1)
new_active=list()
statique={'s':0,'i':0}
new_active.append(statique)
new_active.append(s)
a=0
a+=1
a+=5
new_active.append({'s':a,'i':0})
a+=6
new_active.append({'s':a,'i':0})
if x:
 print(x)

print(np.abs(-90))
