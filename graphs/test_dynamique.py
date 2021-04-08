import numpy as np
from networkx.readwrite import json_graph
import networkx as nx
import matplotlib.pyplot as plt
import random
import json
import time
from matplotlib.ticker import NullFormatter  
import multiprocessing 
from multiprocessing import Manager
import math
from pyvis.network import Network
from flask.json import jsonify
import math
import scipy.sparse as sp
import matplotlib.patches as mpatches

time1=0
Result=[]
train_test_split=None



def HISBmodel (Graph,Seed_Set,Opinion_Set,Statistical,paramater):
    
    #Opinion:normal/denying/supporting
    #State:non_infected/infected/spreaders 
    #Statistical:{'NonInfected':NbrOFnodes,'Infected':**,'Spreaders':**,OpinionDenying':**,'OpinionSupporting':**,'RumorPopularity':**}
  
    ListInfectedNodes=Seed_Set[:]
    Opinion_Set=Opinion_Set[:]
    time=0.125
    Probability=0.2
    i=0
    #the time to control the evolution of the networks
    time_control=time1
    stop=False
    #list of link predected at T+1
    link_predict=[]
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
      #evolution networks
      if stop==False:
          link_predict=dynamique_graph(Graph,method=methods)
          if time1>time_control:
            time_control=time1
          else:
            stop=True
      print("edegs:",len(Graph.edges))
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
  
   
    opinion=jug*(Accpet_NegR / Nbr_OF_R)
    if(np.random.random_sample()<= opinion):
        return 'denying'
    else:
        return 'supporting'


def graphe_TO_json(g):
    
    data =  json_graph.node_link_data(g,{"link": "links", "source": "source", "target": "target","weight":"weight"})
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

def parameters(parameter,stepBeta=1,Beta=0.2,stepOmega=5.2,Omega=math.pi/3,stepDelta=0.65,Delta=math.pi/24,stepJug=0.9,Jug=0.1):
    Beta_max=Beta+stepBeta
    Omega_max=Omega +stepOmega
    Delta_max=Delta +stepDelta
    Jug_max=Jug+stepJug
    parameter.append({'beta_min':round(Beta,2),'beta_max':round(Beta_max,2),'omega_min':round(Omega,2),'omega_max':round(Omega_max,2),'delta_min':round(Delta,2),'delta_max':round(Delta_max,2),'Jug_min':round(Jug,2),'Jug_max':round(Jug_max,2)})

def Start(i,index,Graph,parameter,Stat,percentage):
    for each in range(len(Graph.nodes)):
        Graph.nodes[each]['opinion']="normal"
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
    with open('data.json', 'w', encoding='utf-8') as f:
         json.dump(Stat, f, ensure_ascii=False, indent=4)
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
 
def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()

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
                processes=[multiprocessing.Process(target=Start,args=(i,j,g,parameter,Stat,percentage))for i in range(1)] 
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
    
def mask_test_edges(adj, test_frac=.01, prevent_disconnect=True):
    # NOTE: Splits are randomized and results might slightly deviate from reported numbers in the paper.
    # Remove diagonal elements
    #adj = adj - sp.dia_matrix((adj.diagonal()[np.newaxis, :], [0]), shape=adj.shape)
    #adj.eliminate_zeros()
    # Check that diag is zero:
    #assert np.diag(adj.todense()).sum() == 0
    g = nx.from_scipy_sparse_matrix(adj)
    
    orig_num_cc = nx.number_connected_components(g)
    adj_triu = sp.triu(adj,k=1) # upper triangular portion of adj matrix
    adj_tuple = sparse_to_tuple(adj_triu) # (coords, values, shape), edges only 1 way
    edges = adj_tuple[0] # all edges, listed only once (not 2 ways)
    # edges_all = sparse_to_tuple(adj)[0] # ALL edges (includes both ways)
    num_test = int(np.floor(edges.shape[0] * test_frac)) # controls how large the test set should be
    # Store edges in list of ordered tuples (node1, node2) where node1 < node2
    edge_tuples = [(min(edge[0], edge[1]), max(edge[0], edge[1])) for edge in edges]
    all_edge_tuples = set(edge_tuples)
    train_edges = set(edge_tuples) # initialize train_edges to have all edges
    test_edges = set()
    
    print('num',num_test)
    print('init',len(train_edges))
    # Iterate over shuffled edges, add to train/val sets
    np.random.shuffle(edge_tuples)
    for edge in edge_tuples:
        # print edge
        if len(test_edges) == num_test :
            break
        node1 = edge[0]
        node2 = edge[1]  
        # If removing edge would disconnect a connected component, backtrack and move on
        g.remove_edge(node1, node2)
        if prevent_disconnect == True:
            if nx.number_connected_components(g) > orig_num_cc:
                g.add_edge(node1, node2)
                continue

        # Fill test_edges first
        if len(test_edges) < num_test:
            test_edges.add(edge)
            train_edges.remove(edge)
     # Both edge lists full --> break loop
    if (len(test_edges) < num_test):
        print ("WARNING: not enough removable edges to perform full train-test split!")
        print ("Num. (test, val) edges requested: :",num_test)
        print ("Num. (test, val) edges returned: (", len(test_edges), ")")

    if prevent_disconnect == True:
        assert nx.number_connected_components(g) == orig_num_cc
    test_edges_false = set()
    while len(test_edges_false) < num_test:
        idx_i = np.random.randint(0, adj.shape[0])
        idx_j = np.random.randint(0, adj.shape[0])
        if idx_i == idx_j:
            continue

        false_edge = (min(idx_i, idx_j), max(idx_i, idx_j))

        # Make sure false_edge not an actual edge, and not a repeat
        if false_edge in all_edge_tuples:
            continue
        if false_edge in test_edges_false:
            continue

        test_edges_false.add(false_edge)
    # assert: test, val, train positive edges disjoint
    assert test_edges.isdisjoint(train_edges)
    assert test_edges_false.isdisjoint(all_edge_tuples)
    # Re-build adj matrix using remaining graph
    adj_train = nx.adjacency_matrix(g)
    
    # Convert edge-lists to numpy arrays
    train_edges = np.array([list(edge_tuple) for edge_tuple in train_edges])
    test_edges = np.array([list(edge_tuple) for edge_tuple in test_edges])
    test_edges_false = np.array([list(edge_tuple) for edge_tuple in test_edges_false])   
    # NOTE: these edge lists only contain single direction of edge!
    return adj_train, train_edges,test_edges,test_edges_false
def sparse_to_tuple(sparse_mx):
    if not sp.isspmatrix_coo(sparse_mx):
        sparse_mx = sparse_mx.tocoo()
    coords = np.vstack((sparse_mx.row, sparse_mx.col)).transpose()
    values = sparse_mx.data
    shape = sparse_mx.shape
    return coords, values, shape
def new_Link(matrix,ebunchi,ebunch):
    new_link=[]
    L=matrix.shape[0]
    #matrix symetric
    if matrix.max()!=0:
     for edges in ebunchi:
            Tuple=(edges[0],edges[1])
            #probability of new link matrix[edges[0]][edges[1]]
            if matrix[edges[0]][edges[1]]>0:
                if matrix[edges[0]][edges[1]]>np.random.rand(): 
                    new_link.append(Tuple)
                else:
                    ebunch.append(Tuple)
            else:
              ebunch.append(Tuple)
    else:
        for edges in ebunchi:
            Tuple=(edges[0],edges[1])
            ebunch.append(Tuple)
    return new_link
def get_ebunch(train_test_split):
    adj_train, train_edges,test_edges,test_edges_false = train_test_split
 
    test_edges_list = test_edges.tolist() # convert to nested list
    test_edges_list = [tuple(node_pair) for node_pair in test_edges_list] # convert node-pairs to tuples
    test_edges_false_list = test_edges_false.tolist()
    test_edges_false_list = [tuple(node_pair) for node_pair in test_edges_false_list]
   
    return (test_edges_list + test_edges_false_list)

def split_test(test,frac):
    test_split=[]
    if len(test)<frac:
        frac=len(test)
    for i in reversed(range(frac)):
        test_split.append(test.pop(i))
   
    return test_split
# Input: NetworkX training graph, train_test_split (from mask_test_edges)
def adamic_adar_sc(g, ebunch):
    if g.is_directed(): # Only works for undirected graphs
        g= g.to_undirected()

   # Unpack input
    adj = nx.adjacency_matrix(g)
    aa_matrix = np.zeros(adj.shape)
    for u, v, p in nx.adamic_adar_index(g, ebunch=ebunch): # (u, v) = node indices, p = Adamic-Adar index
        aa_matrix[u][v] = p
        aa_matrix[v][u] = p # make sure it's symmetric
    if aa_matrix.max()==0:
       print('adamic --> predection none')
    else:
       aa_matrix = aa_matrix / aa_matrix.max() # Normalize matrix
    return aa_matrix
def resource_allocation_sc(g, ebunch):
    if g.is_directed(): # Only works for undirected graphs
       g= g.to_undirected()

   # Unpack input
    adj = nx.adjacency_matrix(g)
    aa_matrix = np.zeros(adj.shape)
    for u, v, p in nx.resource_allocation_index(g, ebunch=ebunch): # (u, v) = node indices, p = Adamic-Adar index
        aa_matrix[u][v] = p
        aa_matrix[v][u] = p # make sure it's symmetric
    if aa_matrix.max()==0:
       print('resource_allocat --> predection none')
    else:
       aa_matrix = aa_matrix / aa_matrix.max() # Normalize matrix
    return aa_matrix
 
# Input: NetworkX training graph, train_test_split (from mask_test_edges)
def jaccard_coefficient_sc(g, ebunch):
    if g.is_directed(): # Jaccard coef only works for undirected graphs
        g = g.to_undirected()

    # Unpack input

    # Calculate scores
    adj = nx.adjacency_matrix(g)
    jc_matrix = np.zeros(adj.shape)
    for u, v, p in nx.jaccard_coefficient(g, ebunch=ebunch): # (u, v) = node indices, p = Jaccard coefficient
        jc_matrix[u][v] = p
        jc_matrix[v][u] = p # make sure it's symmetric
    if jc_matrix.max()==0:
           print('jaccard -->predection none')
    else:
    
      jc_matrix = jc_matrix / jc_matrix.max() # Normalize matrix

    return jc_matrix

# Input: NetworkX training graph, train_test_split (from mask_test_edges)

def preferential_attachment_sc(g, ebunch):
    if g.is_directed(): # Only defined for undirected graphs
        g = g.to_undirected()

    # Unpack input
    adj = nx.adjacency_matrix(g)
    pa_matrix = np.zeros(adj.shape)
    for u, v, p in nx.preferential_attachment(g, ebunch=ebunch): # (u, v) = node indices, p = Jaccard coefficient
        pa_matrix[u][v] = p
        pa_matrix[v][u] = p # make sure it's symmetric
    if pa_matrix.max()==0:
        print('preferential-->prediction none')
    else:
       pa_matrix = pa_matrix / pa_matrix.max() # Normalize matrix

    return pa_matrix

def test(train_test_split,method='adamic',split=0.025):
    result=[]
    adj_train, train_edges,test_edges,test_edges_false=train_test_split
    g= nx.Graph(adj_train) 
    ebunch=get_ebunch(train_test_split)
    frac=int(len(ebunch)*split)
    print("init---------------")
    print("frac:",frac)
    print("edges:",len(g.edges))
    print("tets_edges:",len(test_edges))
    print("tets_edges_false:",len(test_edges_false))
    print("method:",method)
    print('#-------------------')
    if method=='adamic':
        while len(ebunch)>0: 
          ebunchi=split_test(ebunch,frac=frac)
          matrix=adamic_adar_sc(g,ebunchi)
          new_link=new_Link(matrix,ebunchi,ebunch)
          g.add_edges_from(new_link)     
          result.append({'ebunch':ebunchi,'matrix':matrix,'new_link':new_link,'method':method})
          if matrix.max()==0:
                 matrix=adamic_adar_sc(g,ebunch) 
                 if matrix.max()==0:
                     print('hi')
                     break
    elif method=='jaccard':
        while len(ebunch)>0:
          ebunchi=split_test(ebunch,frac=frac)
          matrix=jaccard_coefficient_sc(g,ebunchi)
          new_link=new_Link(matrix,ebunchi,ebunch)
          g.add_edges_from(new_link)
          graph=nx.Graph(nx.adjacency_matrix(g))
          result.append({'ebunch':ebunchi,'matrix':matrix,'new_link':new_link,'method':method,'graph':graph})   
          if matrix.max()==0:
                 matrix=jaccard_coefficient_sc(g,ebunch) 
                 if matrix.max()==0:
                     print('hi')
                     break
    elif method=='preferential':
        while len(ebunch)>0:
          ebunchi=split_test(ebunch,frac=frac)
          matrix=preferential_attachment_sc(g,ebunchi)
          new_link=new_Link(matrix,ebunchi,ebunch)
          g.add_edges_from(new_link)
          graph=nx.Graph(nx.adjacency_matrix(g))
          result.append({'ebunch':ebunchi,'matrix':matrix,'new_link':new_link,'method':method,'graph':graph})
          if matrix.max()==0:
                 matrix=preferential_attachment_sc(g,ebunch) 
                 if matrix.max()==0:
                     print('hi')
                     break
    elif method=='resource_allocation':
        while len(ebunch)>0:
          ebunchi=split_test(ebunch,frac=frac)
          matrix=resource_allocation_sc(g,ebunchi)
          new_link=new_Link(matrix,ebunchi,ebunch)
          g.add_edges_from(new_link)
          graph=nx.Graph(nx.adjacency_matrix(g))
          result.append({'ebunch':ebunchi,'matrix':matrix,'new_link':new_link,'method':method,'graph':graph})
          if matrix.max()==0:
                 matrix=resource_allocation_sc(g,ebunch) 
                 if matrix.max()==0:
                     print('hi')
                     break
    return result  
      #stat.append(result)


def display_graph(x,G,pos_link=None,fals_link=None,new_link=None,method="adamic"):
    
    plt.figure(num=x)
    plt.suptitle(method)
    pos = nx.spring_layout(G)  # positions for all nodes
    # nodes
    plt.subplot(121)
    nx.draw_networkx_nodes(G, pos, nodelist=G.nodes, node_color="y",)
    # edges
    nx.draw_networkx_edges(G, pos, width=1.0)
    plt.subplot(122)
    nx.draw_networkx_nodes(G, pos, nodelist=G.nodes, node_color="y",)
    if pos_link:
       nx.draw_networkx_edges(G,pos,edgelist=pos_link,width=3,edge_color="g",)
    if new_link :
       nx.draw_networkx_edges(G,pos,edgelist=new_link,width=3,edge_color="b",)
    if fals_link:
       nx.draw_networkx_edges(G,pos,edgelist=fals_link,width=3,edge_color="r",)
    
    g_patch = mpatches.Patch(color='g', label='pos_link')
    r_patch = mpatches.Patch(color='b', label='new_link')
    b_patch = mpatches.Patch(color='r', label='fals_link')
    plt.legend(handles=[g_patch,r_patch,b_patch])
    
    
def display(score):

    for xx in range(len(score)):
        plt.figure(num=xx)
        plt.subplot()
        x=range(len(score[xx]['roc']))
        plt.plot(x, score[xx]['roc'],'bo',label='roc')
        plt.plot(x, score[xx]['ap'],'ro',label='average_P')
        plt.legend(fontsize=12) 
        plt.grid(True)
        plt.xlabel('score')
        plt.ylabel('stpe')
        plt.title(score[xx]['method'])
        plt.savefig(score[xx]['method']+'.pdf',dpi=20)
    
    plt.show()    

def list_tuple(ebunch,matrix,tuple=True):
    List_triplet=[]
    if tuple:
        for edges in ebunch:
            var=(edges[0],edges[1],matrix[edges[0]][edges[1]])
            List_triplet.append(var)
        return List_triplet
    else: 
        pos=[]
        for x,y in ebunch :
          Tuple=(x,y)
          pos.append(Tuple)
        return pos
   
def dynamique_graph_Result(g,method):
    global train_test_split
    adj = nx.adjacency_matrix(g)
    train_test_split=mask_test_edges(adj,test_frac=0.2)
    adj_train, train_edges,test_edges,test_edges_false=train_test_split
   
    display_graph(1,g,pos_link=list_tuple(train_edges,None,False),method='graphe init vs test graph')
    g.remove_edges_from(test_edges)
   
    display_graph(2,g,pos_link=list_tuple(test_edges,None,False),new_link=list_tuple(test_edges_false,None,False),method='test edges & new link ')
    #result 
    return test(train_test_split,method)
      
def dynamique_graph(g,method): 
    global time1   
    global Result  
    if time1==0:
       Result=dynamique_graph_Result(g,methods)
       print("edges:",len(g.edges),"time:",time1)
       time1+=1
    else:
        if time1<len(Result):
            #edd edges t=t-1
           g.add_edges_from(Result[time1-1]['new_link'])
           print("edges:",len(g.edges),"time:",time1)
           #display_graph(g,pos_link=Result[time1-1]['new_link'],method=method)
           time1+=1
        else:
            g.add_edges_from(Result[time1-1]['new_link'])
            print("edges:",len(g.edges),"time:",time1)
            print("evolution stoped")
            return None
    #prediction in  time1+1
    return list_tuple(Result[time1-1]['ebunch'],Result[time1-1]['matrix'])
def filter_list(full_list, excludes):
    pos=[]
    neg=[]
    fals_link=[]
    s=set(excludes)
    
    for x,y in full_list :
        Tuple=(x,y)
        if Tuple not in s:
            neg.append(Tuple)
        else:
            pos.append(Tuple)
    for tuple in s:
        if tuple not in pos:
           fals_link.append(tuple)
    return pos,neg,fals_link



   
if __name__ == '__main__':
    

       # use net.Graph() for undirected graph

# How to read from a file. Note: if your egde weights are int, 
# change float to int.
   #methods 'adamic','jaccard','preferential','resource_allocation'
    methods='resource_allocation'
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
    print(static.format(Nodes,len(g.edges)))
    percentage=1 #1% of popularity" is infected 
    NumOFsumi=1
    beta=0.2
    omega=0
    juge=0.1
    delta=0
    Stat=[] 
    parameter=[]
    parameters(parameter)
    start_time = time.time()  
    Start(0,0,g,parameter,Stat,percentage) 
    end_time = time.time() 
    print("Parallel xx time=", end_time - start_time)
   
    #simul_beta(beta,1,1)
    #simul_delta(delta,7,5)
    #simul_juge(juge,13,9)
    #simul_omega(omega,19,5)
    #plt.show()
    adj_train, train_edges,test_edges,test_edges_false=train_test_split
    #calcule score
    new_links=[]
    for each in Result:
        for link in each['new_link']:
            new_links.append(link)
    pos_link,fals_link,new_link=filter_list(test_edges,new_links)
    #rappl=Vrai_Pos/(Vrai_POS+Vrai)
    rappel=len(pos_link)/len(test_edges)
    precision=len(pos_link)/len(new_links)
    f_score=2*rappel*precision/(rappel+precision)
    per=int(len(new_link)/len(test_edges_false)*100)
    print("method:",methods)
    print("rappel:",rappel)
    print("precision",precision)
    print("f_score",f_score)
    print("percentage of new links added: %",per)
    display_graph(3,g,pos_link,fals_link,new_link,methods)

    plt.show()
  