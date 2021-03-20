import numpy as np
from networkx.readwrite import json_graph
import networkx as nx
import matplotlib.pyplot as plt
import random
import os
import time
from matplotlib.ticker import NullFormatter  
import multiprocessing 
from multiprocessing import Manager

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

def HISBmodel (g,Seed_Set,Opinion_Set,Statistical,paramater):
    Graph=g
    #Opinion:normal/denying/supporting
    #State:non_infected/infected/spreaders 
    #Statistical:{'NonInfected':NbrOFnodes,'Infected':**,'Spreaders':**,OpinionDenying':**,'OpinionSupporting':**,'RumorPopularity':**}
    
    ListInfectedNodes=Seed_Set[:]
    Opinion_Set=Opinion_Set[:]
    time=0.125
    Probability=0.3
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
    Statistical.append({'NonInfected':Nbr_nonInfected,'Infected':Nbr_Infected,'Spreaders':Nbr_Spreaders,'OpinionDenying':OpinionDenying,'OpinionSupporting':OpinionSupporting,'RumorPopularity':RumorPopularity,'graph':0})
    #----------------------
    #if the list is empty we stop the propagation
    x=0
    while ListInfectedNodes: 
      RumorPopularity = 0
      Nbr_Spreaders = 0
      L=len(ListInfectedNodes)
      
      for X in reversed(range(0,L)):
        
        id = ListInfectedNodes[X]
        
        #relative time of rumor spreading
        RelativeTime = time - Graph.nodes[id]['Infetime'] 
        if (np.exp(-RelativeTime * Graph.nodes[id]['beta']) < 0.05) :
          ListInfectedNodes.pop(X)
          Graph.nodes[id]['state'] = "infected"
          
              

        else:
            #atrraction of nodes
            ActualAttraction = np.exp(-RelativeTime * Graph.nodes[id]['beta']) * np.abs(np.sin((RelativeTime * Graph.nodes[id]['omega'] )+ Graph.nodes[id]['delta']))
            
            RumorPopularity += ActualAttraction * Graph.nodes[id]['degre']
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
                    AccepR = Graph.nodes[id]['degre']/ (Graph.nodes[id]['degre'] + Graph.nodes[each]['degre'])*0.3
                    if (np.random.random_sample()<=AccepR):
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
   
    print(Nbr_Infected)
    
   
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
  
   
    opinion=jug*(Accpet_NegR / Nbr_OF_R)
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
    
  


def parameters(parameter,Beta=0.2,Omeag=0.1,Delta=0.1,Jug=0.1):
    Beta_min= round(random.uniform(Beta, Beta+0.1),2)
    Beta_max=Beta_min+ round(random.uniform(0.0, 0.5),2)
    Omega_min= round(random.uniform(0.1, 6.0), 2)
    Omega_max=Omega_min+round(random.uniform(0.0, 4.0),2)
    Delta_min= round(random.uniform(0.1, 0.20), 2)
    Delta_max=Delta_min+ round(random.uniform(0.2, 1.30),2)
    Jug_min=round(random.uniform(0.1, 0.3), 2)
    Jug_max=Jug_min+ round(random.uniform(0.2, 0.7),2)
    parameter.append({'Beta_min':Beta_min,'Beta_max':Beta_max,'Omega_min':0.1,'Omega_max':6,'Delta_min':0.1,'Delta_max':1.6,'Jug_min':0.8,'Jug_max':1})


def Start(Graph,parameter,Stat,percentage):
    for each in range(len(Graph.nodes)):
        Graph.nodes[each]['id']=each
        Graph.nodes[each]['opinion']="normal"
        Graph.nodes[each]['beta']=0
        Graph.nodes[each]['omega']=0
        Graph.nodes[each]['delta']=0
        Graph.nodes[each]['jug']=0
        Graph.nodes[each]['AccpR']=0
        Graph.nodes[each]['SendR']=0
        Graph.nodes[each]['Accp_NegR']=0
        Graph.nodes[each]['value']=0
        Graph.nodes[each]['infected']='false'
        Graph.nodes[each]['degre']=Graph.degree[each]
        Graph.nodes[each]['neighbors']=[n for n in Graph.neighbors(each)]

        Graph.nodes[each]['Infetime']=0 
        Graph.nodes[each]['state']='non_infected'
    
    Statistical=[]
    ListInfected=[]
    Listopinion=[]
    #X% of Popularity is infected 
    geneList_Infectede(ListInfected,Listopinion,len(Graph.nodes),percentage)  
    HISBmodel(Graph,ListInfected,Listopinion,Statistical,parameter)  
    Stat.append(Statistical)
    print(len(Stat))
   
def globalStat(S,Stat_Global,parametre):
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
     

  #
    Stat_Global.append({'Infected':y1,'Spreaders':y2,'RumorPopularity':y3,'OpinionDenying':y4,'OpinionSupporting':y5,'parameter':parameter,'max':max})       


    #Number of nodes

def Display(Stat_Global):
    max=0
    Stat=[]
    for each in Stat_Global:
        
        L=each['max']
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
  
    plt.figure(num=1,figsize=(18, 18))
    color=[]
    x = range(0,max)
    my_string = "Node:{},N_Simulation:{},[Beta_min:{},Beta_max:{},Omega_min:{},Omega_max:{},Delta_min:{},Delta_max:{},Jug_min:{},Jug_max:{}]"
    #Beta_min= parameter[0]['Beta_min']
    #Beta_max=parameter[0]['Beta_max']
    #Omega_min=parameter[0]['Omega_min']
    #Omega_max=parameter[0]['Omega_max']
    #Delta_min=parameter[0]['Delta_min']
    #Delta_max=parameter[0]['Delta_max']
    #Jug_min=parameter[0]['Jug_min']
    #Jug_max=parameter[0]['Jug_max']
    #title=my_string.format(N,NUM_WORKERS,Beta_min,Beta_max,Omega_min,Omega_max,Delta_min,Delta_max,Jug_min,Jug_max)

    # plot 
    
   
    #Infected
    plt.subplot(221)
    
    for infected in Stat:

      plt.plot(x, infected["Infected"],label=infected['parameter'][0]['Beta_min'])
    plt.legend() 
    plt.title('Infected')
    plt.grid(True)
    #plt.suptitle(title, fontsize=10)
   
    # RumorPopularity
    plt.subplot(223)
    for infected in Stat:
    
      plt.plot(x, infected["RumorPopularity"],label='v')
    plt.legend() 
    plt.title('RumorPopularity')
    plt.grid(True)

    #Spreaders
    plt.subplot(222)
    for infected in Stat:
        
      plt.plot(x, infected["Spreaders"],label='r')
    
    plt.legend() 
    plt.title('Spreaders')
    plt.grid(True)

    # Opinion
    plt.subplot(224)
    for infected in Stat:
            
      plt.plot(x, infected["OpinionDenying"],label='Denaying')
      plt.plot(x, infected["OpinionSupporting"],label='Supporting')

    plt.legend() 
    plt.grid(True)
    plt.title('Opinion')
   
    # Format the minor tick labels of the y-axis into empty strings with
    # `NullFormatter`, to avoid cumbering the axis with too many labels.




    plt.gca().yaxis.set_minor_formatter(NullFormatter())
            # Adjust the subplot layout, because the logit one may take more space
            # than usual, due to y-tick labels like "1 - 10^{-3}"
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                wspace=0.35)
            
    plt.show()

if __name__ == '__main__':
    N=1000
    #gene graph
    g=json_graph.node_link_graph(Small_World_networks(N))
    NUM_WORKERS=1
    percentage=1 #1% of popularity" is infected 
   
    Beta=0.2
   
    with Manager() as manager:
        Stat_Global=manager.list()
        
        for index in range(2):
            with Manager() as manager:
                Stat = manager.list()
                parameter=[]
                parameters(parameter,Beta=Beta+(index/10))
                processes=[multiprocessing.Process(target=Start,args=(g,parameter,Stat,percentage))for i in range(NUM_WORKERS)] 
                [process.start() for process in processes] 
                [process.join() for process in processes] 
                globalStat(Stat,Stat_Global,parameter)
       
        Display(Stat_Global)






   

    
  

