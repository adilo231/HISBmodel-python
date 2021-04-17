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
import math
from pyvis.network import Network

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

def HISBmodel (Graph,Seed_Set,Opinion_Set,Statistical,paramater):
    
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
    
    while ListInfectedNodes: 
      RumorPopularity = 0
      Nbr_Spreaders = 0
      L=len(ListInfectedNodes)
      
      for X in reversed(range(0,L)):
        
        id = ListInfectedNodes[X]
        
        #relative time of rumor spreading
        RelativeTime = time - Graph.nodes[id]['Infetime'] 
        if (np.exp(-RelativeTime * Graph.nodes[id]['beta']) < 0.15) :
          ListInfectedNodes.pop(X)
          Graph.nodes[id]['state'] ='infected'
          
              

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
                    AccepR = Graph.nodes[id]['degre']/ (Graph.nodes[id]['degre'] + Graph.nodes[each]['degre'])*0.25
                    if (np.random.random_sample()<=AccepR):
                        Graph.nodes[each]['AccpR']+=1

                        if (Graph.nodes[each]['Infetime']==0 ):
                            Nbr_Infected+=1
                            Nbr_nonInfected-=1


                            Graph.nodes[each]['Infetime'] =time
                            Graph.nodes[each]['opinion'] =Graph.nodes[id]['opinion']
                            Graph.nodes[id]['state']='spreaders'
                            ListInfectedNodes.append(each)
                            if (Graph.nodes[each]['opinion']=='denying'):
                                #negativ opinion
                                Graph.nodes[each]['Accp_NegR']+=1
                                OpinionDenying+=1
                            else:
                                 OpinionSupporting+=1
                        elif (Graph.nodes[id]['opinion']=='denying'):
                            Graph.nodes[each]['Accp_NegR']+=1
                        
                        #updateOpinion(id)
                if (Graph.nodes[id]['opinion']=='denying'):
                    OpinionDenying-=1
                else:
                    OpinionSupporting-=1
                Graph.nodes[id]['opinion']= updateOpinion(jug=Graph.nodes[id]['jug'],Accpet_NegR=Graph.nodes[id]['Accp_NegR'],Nbr_OF_R=Graph.nodes[id]['AccpR'])
                if (Graph.nodes[id]['opinion']=='denying'):
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
       Graph.nodes[node]['omega']=Inclusive(parameters[0]['omega_min'],parameters[0]['omega_max'])
       Graph.nodes[node]['beta']=Inclusive(parameters[0]['beta_min'],parameters[0]['beta_max'])
       Graph.nodes[node]['delta']=Inclusive(parameters[0]['delta_min'],parameters[0]['delta_max'])
       Graph.nodes[node]['jug']=Inclusive(parameters[0]['Jug_min'],parameters[0]['Jug_max'])


def Inclusive(min,max):
   
   b= ((np.random.random_sample()*(max - min )) + min)
    
   return b

def updateOpinion(jug,Accpet_NegR,Nbr_OF_R): 
  
   
    opinion=jug
    if Accpet_NegR / Nbr_OF_R>0:
      opinion*=(Accpet_NegR / Nbr_OF_R)
    if(np.random.random_sample()<= opinion):
        return 'denying'
    else:
        return 'supporting'


def graphe_TO_json(g):
    
    data =  json_graph.node_link_data(g,{"link": "links", "source": "source", "target": "target","weight":"weight"})
    data['nodes'] = [ {"id": i,"state":'non_infected',"opinion":'normal',"beta":0,"omega":0,"delta":0,"jug":0,"Infetime":0,"AccpR":0,"SendR":0,"Accp_NegR":0,"value":0,"infected":'false',"degre":g.degree[i],"neighbors":[n for n in g.neighbors(i)]} for i in range(len(data['nodes'])) ]
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

def parameters(parameter,stepBeta=1,Beta=0.2,stepOmega=5.2,Omega=math.pi/3,stepDelta=0.65,Delta=math.pi/24,stepJug=0.9,Jug=0.1):
    Beta_max=Beta+stepBeta
    Omega_max=Omega +stepOmega
    Delta_max=Delta +stepDelta
    Jug_max=Jug+stepJug
    parameter.append({'beta_min':round(Beta,2),'beta_max':round(Beta_max,2),'omega_min':round(Omega,2),'omega_max':round(Omega_max,2),'delta_min':round(Delta,2),'delta_max':round(Delta_max,2),'Jug_min':round(Jug,2),'Jug_max':round(Jug_max,2)})

def Start(i,index,Graph,parameter,Stat,percentage):
    for each in range(len(Graph.nodes)):
        Graph.nodes[each]['opinion']='normal'
        Graph.nodes[each]['Infetime']=0 
        Graph.nodes[each]['state']='non_infected'
        
    Statistical=[]
    ListInfected=[]
    Listopinion=[]
    #X% of Popularity is infected 
    geneList_Infectede(ListInfected,Listopinion,len(Graph.nodes),percentage)  
    HISBmodel(Graph,ListInfected,Listopinion,Statistical,parameter)  
    Stat.append(Statistical)
       
def globalStat(S,Stat_Global,parameter):
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

def Display(Stat_Global,xx,title_fig,nb):
    Title=''
    if(title_fig=='beta'):
        Title=r'$\beta$'
        
    elif(title_fig=='delta'):
        Title=r'$\delta$'
    elif(title_fig=='omega'):
        Title=r'$\omega$'
    else:
       Title="J"
    max=0
    Stat=[]
    Infected=[]
    para=[]
    for each in Stat_Global:
        L=each['max']
        Infected.append(each['Infected'][L-1])
        para.append(each['parameter'][0][title_fig+"_min"])
        
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
    
    type=['x','*','p','8','h','H','.','+','4']
    
    #Infected
    plt.figure(num=xx)
    plt.subplot()
    k="{}:[{},{}]"
    for infected,j in zip( Stat,range(len(Stat))):
      
      plt.plot(x, infected["Infected"],marker=type[j],markersize=7,linewidth=1,label=k.format(Title,round(infected['parameter'][0][title_fig+"_min"],2),round(infected['parameter'][0][title_fig+"_max"],2)))
    plt.legend(fontsize=12) 

    plt.xlabel('Temps',fontsize=10)
    plt.ylabel('Nombre des individues')
    plt.grid(True)
    plt.savefig(title_fig+'infected.pdf',dpi=50)
    # RumorPopularity
    xx+=1
    plt.figure(num=xx)
    plt.subplot()
    k="{}:[{},{}]"
    for infected,j in zip( Stat,range(len(Stat))):
      
      plt.plot(x, infected["RumorPopularity"],marker=type[j],markersize=6,linewidth=1,label=k.format(Title,round(infected['parameter'][0][title_fig+"_min"],2),round(infected['parameter'][0][title_fig+"_max"],2)))
    plt.legend(fontsize=12) 
    plt.xlabel('Temps')
    plt.ylabel('Nombre des individues')
    plt.grid(True)
    plt.savefig(title_fig+'RumorPopularity.pdf',dpi=20)
    
    #Spreaders
    xx+=1
    plt.figure(num=xx)
    plt.subplot()
    k="{}:[{},{}]" 
    for infected ,j in zip( Stat,range(len(Stat))):
      
      plt.plot(x, infected["Spreaders"],marker=type[j],markersize=6,linewidth=1,label=k.format(Title,round(infected['parameter'][0][title_fig+"_min"],2),round(infected['parameter'][0][title_fig+"_max"],2)))
    
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.xlabel('Temps')
    plt.ylabel('Nombre des individues')
    plt.savefig(title_fig+'Spreaders.pdf',dpi=20)
    
   # Opinion
    xx+=1
    plt.figure(num=xx)
    plt.subplot()
    k="{}:[{},{}]" 
    for infected,j in zip( Stat,range(len(Stat))):
      plt.plot(x, infected["OpinionDenying"],marker=type[j],markersize=6,linewidth=2,label=k.format(Title,round(infected['parameter'][0][title_fig+"_min"],2),round(infected['parameter'][0][title_fig+"_max"],2)))
    plt.legend(fontsize=12) 
    plt.grid(True)
    plt.xlabel('Temps')
    plt.ylabel('Nombre des individues')
    plt.savefig(title_fig+'OpinionDenying.pdf',dpi=20)
    

    # Opinion
    xx+=1
    plt.figure(num=xx)
    plt.subplot()
    k="{}:[{},{}]" 
    for infected,j in zip( Stat,range(len(Stat))):
      plt.plot(x, infected["OpinionSupporting"],marker=type[j],markersize=6,linewidth=2,label=k.format(Title,round(infected['parameter'][0][title_fig+"_min"],2),round(infected['parameter'][0][title_fig+"_max"],2)))
   
    plt.legend(fontsize=12) 
    plt.grid(True)
    plt.xlabel('Temps')
    plt.ylabel('Nombre des individues')
    plt.savefig(title_fig+'OpinionSupporting.pdf',dpi=20)
    
    # Format the minor tick labels of the y-axis into empty strings with
    # `NullFormatter`, to avoid cumbering the axis with too many labels.

    xx+=1
    plt.figure(num=xx) 
    plt.subplot()      
    plt.plot(para,Infected,'bo')
    plt.grid(True)
    plt.xlabel(Title)
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
    FielName="C:/Users/RAMZI/Desktop/PFE/Application/flask/graphs/facebook.txt"
    Graphtype=nx.DiGraph()
    g= nx.read_edgelist(FielName,create_using=Graphtype,nodetype=int)
    
    return graphe_TO_json(g)
   
'''
    with Manager() as manager:
        Stat_Global=manager.list() 
        start_time = time.time()     
        processes=[multiprocessing.Process(target=Simulation,args=(i,g,Stat_Global,percentage))for i in range(NUM_WORKERS)] 
        [process.start() for process in processes] 
        [process.join() for process in processes] 
        end_time = time.time()
        print("Parallel time=", end_time - start_time)
        Display(Stat_Global)
    
'''
def simul_beta(parbeta,x,NUM_WORKERS):
     beta=parbeta
     stepBeta=0.2
     with Manager() as manager:
        Stat_Global=manager.list() 
        for j in range(NUM_WORKERS):
            with Manager() as manager:
                Stat=manager.list()  
                parameter=[]
                parameters(parameter,stepBeta=stepBeta,Beta=beta)
                start_time = time.time()  
                processes=[multiprocessing.Process(target=Start,args=(i,j,g,parameter,Stat,percentage))for i in range(NumOFsumi)] 
                [process.start() for process in processes] 
                [process.join() for process in processes]
                end_time = time.time() 
                print("Parallel xx time=", end_time - start_time)
                globalStat(Stat,Stat_Global,parameter)
                beta+=stepBeta
                print("step:",j,parameter)
        Display(Stat_Global,x,"beta",Nodes)
def simul_omega(paromega,x,NUM_WORKERS):
  omega=paromega
  stepOmega=math.pi*0.4
  with Manager() as manager:
    Stat_Global=manager.list() 
    for j in range(NUM_WORKERS):
        with Manager() as manager:
            Stat=manager.list()  
            parameter=[]        
            parameters(parameter,stepOmega=stepOmega,Omega=omega)
            start_time = time.time()  
            processes=[multiprocessing.Process(target=Start,args=(i,j,g,parameter,Stat,percentage))for i in range(NumOFsumi)] 
            [process.start() for process in processes] 
            [process.join() for process in processes]
            end_time = time.time() 
            print("Parallel xx time=", end_time - start_time)
            globalStat(Stat,Stat_Global,parameter)
            omega+=stepOmega
            print("step:",j,parameter)
    Display(Stat_Global,x,"omega",Nodes)
def simul_delta(pardelta,x,NUM_WORKERS):
  delta=pardelta
  stepDelta=0.156
  with Manager() as manager:
    Stat_Global=manager.list() 
    for j in range(NUM_WORKERS):
        with Manager() as manager:
            Stat=manager.list()  
            parameter=[]
            parameters(parameter,stepDelta=stepDelta,Delta=delta)
            start_time = time.time()  
            processes=[multiprocessing.Process(target=Start,args=(i,j,g,parameter,Stat,percentage))for i in range(NumOFsumi)] 
            [process.start() for process in processes] 
            [process.join() for process in processes]
            end_time = time.time() 
            print("Parallel xx time=", end_time - start_time)
            globalStat(Stat,Stat_Global,parameter)
            delta+=stepDelta
            print("step:",j,parameter)
    Display(Stat_Global,x,"delta",Nodes)
def simul_juge(parjuge,x,NUM_WORKERS):
 jug=parjuge
 stepJug=0.1
 with Manager() as manager:
    Stat_Global=manager.list() 
    for j in range(NUM_WORKERS):
        with Manager() as manager:
            Stat=manager.list()  
            parameter=[]
            parameters(parameter,stepJug=stepJug,Jug=jug)
            start_time = time.time()  
            processes=[multiprocessing.Process(target=Start,args=(i,j,g,parameter,Stat,percentage))for i in range(NumOFsumi)] 
            [process.start() for process in processes] 
            [process.join() for process in processes]
            end_time = time.time() 
            print("Parallel xx time=", end_time - start_time)
            globalStat(Stat,Stat_Global,parameter)
            jug+=stepJug
            print("step:",j,parameter)
    Display(Stat_Global,x,"Jug",Nodes)

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
    
    
   
if __name__ == '__main__':
    

       # use net.Graph() for undirected graph

# How to read from a file. Note: if your egde weights are int, 
# change float to int.
   
    Nodes=100
    #Graph's Parametres 
    P=0.3
    K=10
    M=7
    g=json_graph.node_link_graph(Scale_free_networks(Nodes,M))
    #g=json_graph.node_link_graph(Small_World_networks(Nodes,K,P))
    #g=json_graph.node_link_graph(Random_networks(Nodes,P))
    #g=json_graph.node_link_graph(facebook_graph())
    static="Nodes :{},Edegs:{}."
    #print(static.format(Nodes,len(g.edges)))
    percentage=1 #1% of popularity" is infected 
    NumOFsumi=1
    beta=0.2
    omega=0
    juge=0.1
    delta=0
    simul_beta(beta,1,5)
    #simul_delta(delta,7,5)
    #simul_juge(juge,13,9)
    #simul_omega(omega,19,5)
    #plt.show()
    
    #net=Network(notebook="true")
    #net.from_nx(g)
    #net.show('rmzi.html')