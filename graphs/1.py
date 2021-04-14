
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
import csv
import json
from matplotlib.ticker import NullFormatter  
from flask.json import jsonify
import scipy.sparse as sp
import matplotlib.patches as mpatches
from operator import itemgetter
Betweeness_Liste = list(np.loadtxt("graphs/result1.txt", comments="#", delimiter=",", unpack=False))
Closeness_Liste=list(np.loadtxt("graphs/result2.txt", comments="#", delimiter=",", unpack=False))
Betas='\u03B2'
Max=[]
Min=[]
TBD='T'+Betas+'D'
TB='T'+Betas
BBD='B'+Betas+'D'
BB='B'+Betas
INfec=[]
#dynamic graph
time1=0
Result=[]
train_test_split=None

def HISBmodel (Graph,Seed_Set,Opinion_Set,Statistical,paramater,K,Tdet,method):
    
    #Opinion:normal/denying/supporting
    #State:non_infected/infected/spreaders 
    #Statistical:{'NonInfected':NbrOFnodes,'Infected':**,'Spreaders':**,OpinionDenying':**,'OpinionSupporting':**,'RumorPopularity':**}
    print('hello HISB')
    print("dynamic evolution graph :",dynamic)
    bl=0
    ListInfectedNodes=Seed_Set[:]
    Opinion_Set=Opinion_Set[:]
    time=0.125
    Probability=0.3
    i=0
     
     #the time to control the evolution of the networks
    time_control=time1
    stop=False
    setup=0
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
      print('setup',setup) 
      RumorPopularity = 0
      Nbr_Spreaders = 0
      L=len(ListInfectedNodes)
      ##evolution networks
      if stop==False and dynamic== True:
          #list of links at t+1
          link_predict=dynamique_graph(Graph,method=methods)
          if time1>time_control:
            time_control=time1
          else:
            stop=True
      for X in reversed(range(0,L)):
        
        id = ListInfectedNodes[X]
        
        #relative time of rumor spreading
        RelativeTime = time - Graph.nodes[id]['Infetime'] 
        if (np.exp(-RelativeTime * Graph.nodes[id]['beta']) < 0.15) :
          ListInfectedNodes.pop(X)
          Graph.nodes[id]['state'] = "infected"
          
              

        else:
            #atrraction of nodes
            ActualAttraction = individual_attraction(RelativeTime ,Graph.nodes[id]['beta'] ,Graph.nodes[id]['omega'], Graph.nodes[id]['delta'])
            
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
                    AccepR =Accepted_rumor(Graph.nodes[id]['degree'],Graph.nodes[each]['degree'])
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
        # print(method," At time:", time, "blocked nodes Nbr:", bl)
        Nodes=len(Graph.nodes)
        
        p=K-bl
        if (method=='B'):
            Random_Blocking_nodes(Graph, p)
            bl=len(blocked(Graph))
        
            
        elif method=='T':
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
        elif method=='H':
            kb,kt=Hybrid_method(Graph,link_predict,p,time)
            #blocking nodes
            for i in kb:
                Graphe.nodes[i]['blocked']='True'        
            #truth COMPAGNE
            for i in kt:
                Graphe.nodes[i]['Protector']='True'
                Graphe.nodes[i]['state']='infected'
                Graph.nodes[i]['Infetime'] =time
                Graph.nodes[i]['opinion']=="denying"
                Graph.nodes[i]['state']='spreaders'
                Graph.nodes[i]['AccpR']+=1
                Graph.nodes[i]['Accp_NegR']+=1
            
            bl=len(kb)+len(kt)
                  
          
          #print(method," At time:", time, "blocked nodes Nbr:", bl)
            
              
      time += 0.25; 

#HISBMODEl function  
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
def individual_attraction(RelativeTime,beta,omega,delta):
   return np.exp(-RelativeTime * beta) * np.abs(np.sin((RelativeTime *omega)+delta))
def Accepted_rumor(degreeNoede_target,degreeNoede_Spreader):
    return degreeNoede_target /(degreeNoede_target+degreeNoede_Spreader) * 0.3
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
#-----------------------------
#function graph
def graphe_TO_json(g):
    
    data =  json_graph.node_link_data(g,{"link": "links", "source": "source", "target": "target","weight":"weight"})
    data['nodes'] = [ {"id": i,"state":"non_infected","Protector":"false","opinion":"normal","beta":0,"omega":0,"delta":0,"jug":0,"Infetime":0,"AccpR":0,"SendR":0,"Accp_NegR":0,"value":0,"blocked":'false',"f_score":0,"g_POSscore":0,"g_NEGscore":0,"degree":g.degree[i],"neighbors":[n for n in g.neighbors(i)]} for i in range(len(data['nodes'])) ]
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
    between=[]
    betaD=[]
    Cent=((nx.degree_centrality(g)))
    clo=[]
    tuple=[]
    for i in Spreaders:
        n=g.neighbors(i)
        
        for j in n:

          if g.nodes[j]['state'] =='non_infected':
            #links for each node spreaders
            tuple.append((j,1))
            if j not in neighb : 
                neighb.append(j)
                Cente.append(Cent[j])
                MaxD.append(g.nodes[j]['degree'])
                beta.append(g.nodes[j]['beta'])
                betaD.append(g.nodes[j]['degree']/g.nodes[j]['beta'])
                between.append(Betweeness_Liste[j])
                clo.append(Closeness_Liste[j])
              
   
    return neighb,MaxD,Cente,beta,betaD,between,clo,tuple
def Degree_MAX(G,K,nb):
    L=[]  
    for i in range(len(nb)):
        L.append(G.nodes[i]['degree'])
    
    return L
#-----------------------
#start sumilation function
         
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
    
def globalStat(S,Stat_Global,parameter,method,K):
    max1=0
    Stat=[]
    
    
    for each in S:
        
        L=len(each)
        Stat.append(each)
        if(L>max1):
            max1=L
    for i in range(len(Stat)):
        L=len(Stat[i])
        Nbr_nonInfected=Stat[i][L-1]['NonInfected']
        Nbr_Infected=Stat[i][L-1]['Infected']
        
        Nbr_Spreaders=Stat[i][L-1]['Spreaders']
        OpinionDenying=Stat[i][L-1]['OpinionDenying']
        OpinionSupporting=Stat[i][L-1]['OpinionSupporting']
        RumorPopularity=Stat[i][L-1]['RumorPopularity']
        for j in range(L,max1):
            Stat[i].append({'NonInfected':Nbr_nonInfected,'Infected':Nbr_Infected,'Spreaders':Nbr_Spreaders,'OpinionDenying':OpinionDenying,'OpinionSupporting':OpinionSupporting,'RumorPopularity':RumorPopularity,'graph':0})       
    
    
    
    y1=[]
    y2=[]
    y3=[]
    y4=[]
    y5=[]   
    Len=len(Stat)
    ST=[]
    for i in range(Len):
        ST.append(Stat[i][max1-1]['Infected'])  
    a=max(ST)
    
    Max.append(a)
    b=min(ST)
    Min.append(b)
    for i in range(max1):
        
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
     
    INfec.append(y1)
    Stat_Global.append({'Infected':y1,'Spreaders':y2,'RumorPopularity':y3,'OpinionDenying':y4,'OpinionSupporting':y5,'parameter':parameter,'max':max1,'method':method})       
    #Number of nodes
def Display(Stat_Global,xx,title_fig,nb):
   #print(Stat_Global)
    Title=['B','BM','BCn','B'+Betas,'B'+Betas+'D','Btw','Bcl',
       'T','TM','TCn','T'+Betas,'T'+Betas+'D','TBw','TCl','NP']
    
    max=0
    Stat=[]
    Infected=[]
    para=[]
    for each in Stat_Global:
        L=each['max']
        #print(L,each['Infected'])
        
        para.append(each['method'])
        metho=str(each['method'])
        if metho.startswith('T'):
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
    type=['x','*','p','8','h','H','.','+','4','1','2','3','o','v','<']
    
    #Infected
    ''' plt.figure(num=xx)
        plt.subplot()
        #k="{}:{},{}]" 
        k="{}" 
        for infected,j in zip( Stat,range(len(Stat))):
          quotients = [number /Nodes  for number in infected["Infected"]]
          plt.plot(x, quotients,markersize=6,linewidth=1)
          
         # plt.plot(x,quotients,marker=type[j],markersize=7,linewidth=1,label=k.format(Title[j]))
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
          plt.plot(x, quotients,markersize=6,linewidth=1)
          #plt.plot(x, quotients,marker=type[j],markersize=6,linewidth=1,label=k.format(Title[j]))
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
          plt.plot(x, quotients,markersize=6,linewidth=1)#,label=k.format(Title[j]))
        
         # plt.plot(x, quotients,marker=type[j],markersize=6,linewidth=1,label=k.format(Title[j]))
        
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
      plt.plot(x, quotients,markersize=6,linewidth=1)
      
      #plt.plot(x, quotients,marker=type[j],markersize=6,linewidth=2,label=k.format(Title[j]))
   
    plt.legend(fontsize=12) 
    plt.grid(True)
    plt.xlabel('Temps')
    plt.ylabel('Nombre des individues')
    plt.title("Supporting")
    plt.savefig(title_fig+'OpinionSupporting.pdf',dpi=20)
    
    # Format the minor tick labels of the y-axis into empty strings with
    # `NullFormatter`, to avoid cumbering the axis with too many labels.'''
    xx+=1
    plt.figure(num=xx) 
    plt.subplot()      
    #plt.plot(para,Infected,'bo')
    er=np.subtract(Max,Min)
    Moy=[]
    for i in er:
        Moy.append(i/(Nodes))
    print(Moy)
    plt.xticks(rotation=45)
    plt.errorbar(para, Infected, yerr=Moy, fmt='o', color='black',
            ecolor='red', elinewidth=2);

    plt.grid(True)
    plt.xlabel(Title)
    plt.title("infected-Supporting")
    plt.ylabel('Nombre des individues')
    plt.savefig(title_fig+'nodes.pdf',dpi=20) 
    
    k_s=[]
    for i in K_seed:
        k_s.append(i/Nodes)
        
    rows = k_s
    INFCT=[]
    Spred=[]
    v=int(len(m)/2)
    
    Liste_t=[]
    Liste_tsp=[]
    print(K_seed)
    for i in (range (len(K_seed))):
        for j in  (range(v)):
            Liste_t.append(round(Infected[j+v*i],3))
    #    print('la taille de INFEct:',len(Liste_t))
        INFCT.append(Liste_t)
        '''with open('ik='+str(i)+'.csv', 'w') as f:
      
            # using csv.writer method from CSV package
            write = csv.writer(f)
            #write.writerow(columns1)
            write.writerows(INFCT)'''
    for i in (range (0,len(K_seed))):
        for j in  (range(v,(2*v)+1)):
            Liste_tsp.append(round(Infected[j+i*v],3))
        #print('la taille de INFEct:',(Liste_tsp))
        Spred.append(Liste_tsp)
        ''' with open('Sk='+str(i)+'.csv', 'w') as f:
      
            # using csv.writer method from CSV package
            write = csv.writer(f)
            #write.writerow(columns1)
            write.writerows(Spred)'''
        
   
    '''np.savetxt("INFECTED.csv", 
           INFCT,
           delimiter =", ", 
           fmt ='% s')
    np.savetxt("SUPPORTING.csv", 
           Spred,
           delimiter =", ", 
           fmt ='% s') '''
    with open('G12.csv', 'w') as f:
      
        # using csv.writer method from CSV package
        write = csv.writer(f)
        #write.writerow(columns1)
        write.writerows(INFCT)
    
    
    with open('G21.csv', 'w') as f1:
      
        # using csv.writer method from CSV package
        write1 = csv.writer(f1)
        #write1.writerow(columns)
        write1.writerows(Spred)
    '''
    
    xx+=1
    fig = plt.figure(xx)
    #fig.subplots_adjust(left=0.2,top=0.8, wspace=1)
    
    #Table - Main table
    #ax = plt.subplot2grid((4,3), (0,0), colspan=2, rowspan=2)
            
    plt.table(cellText=INFCT,rowLabels=rows,colLabels=columns1, loc="upper center")
    
    plt.axis("off")
    plt.savefig('INFECTED.png')
    plt.axis("tight")
    
    xx+=1
    fig1 = plt.figure(xx)
            
    plt.table(cellText=Spred,rowLabels=rows,colLabels=columns, loc="upper center")
    
    plt.axis("off")
    plt.savefig('INFECTED_WITH_SUPORTING_OP.png')
    plt.axis("tight")'''

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
def simulation_strategy(x,K,Tdet,method,G):
       
    with Manager() as manager:
        Stat_Global=manager.list() 
        v=0
        for Ki in K:
                
            for met in method :
                print(met)
                g=G[v]
                with Manager() as manager:
                    Stat=manager.list()  
                    parameter=[]
                    parameters(parameter)
                    start_time = time.time()  
                    processes=[multiprocessing.Process(target=Start,args=(i,g,parameter,Stat,percentage,Ki,Tdet,met))for i in range(NumOFsumi)] 
                    
                    [process.start() for process in processes] 
                    [process.join() for process in processes]
                    end_time = time.time() 
                    print("Parallel xx time=", end_time - start_time)
                    globalStat(Stat,Stat_Global,parameter,met,Ki)
                v+=1     
        Display(Stat_Global,x,'NBLS',Nodes)


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
    FielName="graphs/facebook.txt"
    Graphtype=nx.Graph()
    g= nx.read_edgelist(FielName,create_using=Graphtype,nodetype=int)
    
    return graphe_TO_json(g) 
#---------------------
#Hybrid method
def Hybrid_method(graph,link_predict,K_nodes,timeDetection):
    sp=[]
    search_spreaders(graph,sp)
    #the nodes that are likely to be infected at t + 1
    nodes_atT=[]

    for node in sp:  
        nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor([node],graph)   
        #reel neighbors + predict neighbors
        #neighbors=[(node,probability of link)]
        neighbors=tuple + neighbor_predict(graph,node,link_predict)
        for  id_neighbor,p in neighbors:
            score_first_layer(graph,node,id_neighbor,timeDetection,proba=p) 
            #save neighbors of firs layer for second calcul 
            if id_neighbor not in nodes_atT:
              nodes_atT.append(id_neighbor)
    
    for node in nodes_atT:  
        nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor([node],graph)   
        #reel neighbors of neighbors + predict neighbors of neighbors
        neighbors=tuple + neighbor_predict(graph,node,link_predict)
        for  id_neighbor,p in neighbors:
            score_first_layer(graph,node,id_neighbor,timeDetection,proba=p) 
    
    All_score=F_score_pos_neg(graph,nodes_atT)

    return selected_Kb_Kt_nodes(All_score,K_nodes)

def F_score_pos_neg(graph , nodes):
    F_score=[]
    for each in nodes:
        Ro=graph.nodes[each]['omega']*graph.nodes[each]['delta']/graph.nodes[each]['beta']
        f_neg_TCS=graph.nodes[each]['f_score']*graph.nodes[each]['g_NEGscore']  #neg=jug
        f_pos_BNS=graph.nodes[each]['f_score']*graph.nodes[each]['g_POSscore']  #pos=1-jg
        if f_neg_TCS<f_pos_BNS:
           #positive score [supporting]
           #tupel=>score,id of node,strategy
           F_score.append((f_pos_BNS*Ro,each,'BNS'))
        elif f_neg_TCS>f_pos_BNS:
            #negative score [denying]
            #tupel=>score,id of node,strategy
            F_score.append((f_neg_TCS*Ro,each,'TCS'))
        elif graph.nodes[each]['jug']<0.6: #favorise TCS over BNS if f_neg_TCS==f_pos_BNS
            #negative score [denying]
            #tupel=>score,id of node,strategy
            F_score.append((f_neg_TCS*Ro,each,'TCS'))
       
        #else no thing to do
    
    #Sort the list in descending order max
    F_score.sort(key=itemgetter(0),reverse=True)     
   
    return F_score
    
    #list_of_tuples.sort(key=itemgetter(0))
def neighbor_predict(g,node,listOFlink):
    list=[]
    for u,v,p in listOFlink:
        if u==node and g.nodes[v]['state']=='non_infected':
            list.append((v,p))
        elif v==node and g.nodes[u]['state']=='non_infected':
            list.append((u,p))
    return list
def score_first_layer(Graph,n_source,n_neighbor,timeDetection,proba=1):
    #Psend of spreaders 
    Psend_u=individual_attraction(timeDetection,Graph.nodes[n_source]['beta'] ,Graph.nodes[n_source]['omega'], Graph.nodes[n_source]['delta'])
    #accepte probability V_U
    Paccept_v=Accepted_rumor(Graph.nodes[n_neighbor]['degree'],Graph.nodes[n_source]['degree'])   
    
    #score F , t+1
    score=Psend_u * Paccept_v * proba #p:probability of edges
    
    Graph.nodes[n_neighbor]['f_score']+=score

def score_second_layer(graph,node,neighbor,proba=1):

    Paccept_w=Accepted_rumor(graph.nodes[neighbor]['degree'],graph.nodes[node]['degree'])
    #jug of node w"neighbor of v" * probability of link* probability of accepted W_V
    neg_score=graph.nodes[neighbor]['jug']*proba*Paccept_w
    pos_score=(1-graph.nodes[neighbor]['jug'])*proba*Paccept_w

    graph.nodes[node]['g_POSscore']+=pos_score  #supporting
    graph.nodes[node]['g_NEGscore']+=neg_score  #denying
 
def selected_Kb_Kt_nodes(ListOFscore,K_node):
    
    Kb=[]
    Kt=[]
    i=0
    for score,each,strategy in ListOFscore:
        #score,each,strategy{BNS,TCS}
        if i==K_node:
            break
        if strategy=='BNS':
            Kb.append(each)
            i+=1
        elif strategy=='TCS':
            Kt.append(each)
            i+=1

    return Kb,Kt
#BLOCKING STRATEGY

def Random_Blocking_nodes(Graphe,k):
    sp=[]
    search_spreaders(Graphe,sp)
    nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor(sp,Graphe)
    size=len(nb)
    if k>size:
      k=size-1
    for i in range(k):
        s=random.randint(0, size-1)
        Graphe.nodes[nb[s]]['blocked']='True'
        nb.pop(s)
        size-=1
      
def Hybrid_Blocking_nodes(Graphe,kb):
    
    for i in kb:
        Graphe.nodes[i]['blocked']='True'

      
def Degree_MAX_Blocking_nodes(G,k):
    
    sp=[]
   
    search_spreaders(G,sp)
   
    nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor(sp,G)
    

    for i in range(k):
            
            ID = DNode.index(max(DNode))
            G.nodes[nb[ID]]['blocked']='True'
            DNode.pop(ID)
            nb.pop(ID)
            
def Centrality_Blocking_nodes(G,k):
    
    sp=[]
   
    search_spreaders(G,sp)
    nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor(sp,G)
    for i in range(k):
            
            ID = cen.index(max(cen))
            G.nodes[nb[ID]]['blocked']='True'
            cen.pop(ID)
            nb.pop(ID)         
def Beta_Blocking_nodes(G,k):
    
    sp=[]
   
    search_spreaders(G,sp)
   
    nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor(sp,G)
    

    for i in range(k):
            
            ID = Bet.index(min(Bet))
            G.nodes[nb[ID]]['blocked']='True'
            Bet.pop(ID)
            nb.pop(ID)         
def BetaD_Blocking_nodes(G,k):
    
    sp=[]
   
    search_spreaders(G,sp)
   
    nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor(sp,G)
    

    for i in range(k):
            
            ID = betaD.index(max(betaD))
            G.nodes[nb[ID]]['blocked']='True'
            betaD.pop(ID)
            nb.pop(ID)   
def Betweenness_Blocking_nodes(G,k):
    
    sp=[]
   
    search_spreaders(G,sp)
   
    nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor(sp,G)
    

    for i in range(k):
            
            ID = Bet.index(max(Bet))
            G.nodes[nb[ID]]['blocked']='True'
            Bet.pop(ID)
            nb.pop(ID)         
def Closeness_Blocking_nodes(G,k):
    
    sp=[]
   
    search_spreaders(G,sp)
   
    nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor(sp,G)
    

    for i in range(k):
            
            ID = Clo.index(max(Clo))
            G.nodes[nb[ID]]['blocked']='True'
            Clo.pop(ID)
            nb.pop(ID)         

#TRUTH COMPAGNE STRATEGY
def Random_TRuth_comp(Graphe,k):
    sp=[]
    search_spreaders(Graphe,sp)
    nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor(sp,Graphe)
    size=len(nb)
    if k > size :
       k=size-1
    for i in range(k):
        s=random.randint(0, size-1)
        Graphe.nodes[nb[s]]['Protector']='True'
        Graphe.nodes[nb[s]]['state']='infected'
        nb.pop(s)
        size-=1
def Hybrid_TRuth_comp(Graphe,kt):
    
    for i in kt:
       
        Graphe.nodes[i]['Protector']='True'
        Graphe.nodes[i]['state']='infected'
       

def MaxDegree_TRuth_comp(Graphe,K):
    sp=[]
    search_spreaders(Graphe,sp)
    nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor(sp,Graphe)
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
   
    nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor(sp,Graphe)
   
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
    nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor(sp,Graphe)
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
    nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor(sp,Graphe)
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

def Betweeness_TRuth_comp(Graphe,K):
    sp=[]
    search_spreaders(Graphe,sp)
    nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor(sp,Graphe)
    print(len(Bet))
    size=len(nb)
    k=K
    if k > size :
       k=size-1
    for i in range(k):
        s = Bet.index(max(Bet))
        Graphe.nodes[nb[s]]['Protector']='True'
        Graphe.nodes[nb[s]]['state']='infected'
        nb.pop(s)
        Bet.pop(s)
def Closeness_TRuth_comp(Graphe,K):
    sp=[]
    search_spreaders(Graphe,sp)
    nb,DNode,bet,cen,betaD,Bet,Clo,tuple=neighbor(sp,Graphe)
    size=len(nb)
    k=K
    if k > size :
       k=size-1
    for i in range(k):
        s = Clo.index(max(Clo))
        Graphe.nodes[nb[s]]['Protector']='True'
        Graphe.nodes[nb[s]]['state']='infected'
        nb.pop(s)
        Clo.pop(s)

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

#dynamic networks function
def mask_test_edges(adj, test_frac=.01, prevent_disconnect=True):
    # NOTE: Splits are randomized and results might slightly deviate from reported numbers in the paper.
    # Remove diagonal elements
    #adj = adj - sp.dia_matrix((adj.diagonal()[np.newaxis, :], [0]), shape=adj.shape)
    #adj.eliminate_zeros()
    # Check that diag is zero:
    #assert np.diag(adj.todense()).sum() == 0
    g = nx.from_scipy_sparse_matrix(adj)
    
    #orig_num_cc = nx.number_connected_components(g)
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
            if  nx.is_isolate(g,node1) or nx.is_isolate(g,node2) :
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
    print('end split test')
    return adj_train, train_edges,test_edges,test_edges_false
def sparse_to_tuple(sparse_mx):
    if not sp.isspmatrix_coo(sparse_mx):
        sparse_mx = sparse_mx.tocoo()
    coords = np.vstack((sparse_mx.row, sparse_mx.col)).transpose()
    values = sparse_mx.data
    shape = sparse_mx.shape
    return coords, values, shape
def new_Link(matrix,ebunch):
    new_link=[]
    #matrix symetric
    for u,v,p in matrix:
          Tuple=(u,v)
          #probability of new link matrix[edges[0]][edges[1]]
          if p>0:
              if p>np.random.rand(): 
                  new_link.append(Tuple)
              else:
                  ebunch.append(Tuple)
          else:
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
    return prediction_link(g,ebunch,'adamic')
def resource_allocation_sc(g, ebunch):
    return prediction_link(g,ebunch,'resource_allocation')
# Input: NetworkX training graph, train_test_split (from mask_test_edges)
def jaccard_coefficient_sc(g, ebunch):
    return prediction_link(g,ebunch,'jaccard')

# Input: NetworkX training graph, train_test_split (from mask_test_edges)

def preferential_attachment_sc(g, ebunch):
    return prediction_link(g,ebunch,'preferential')

def prediction_link(g,ebunch,method):
    if g.is_directed(): # Only works for undirected graphs
        g= g.to_undirected()
   # Unpack input
    matrix =[]
    matrix_normalize =[]
    max=0
    if method=='adamic':
        for u, v, p in nx.adamic_adar_index(g, ebunch=ebunch): # (u, v) = node indices, p = resource_allocation index
            tupl=(u,v,p)
            matrix.append(tupl) 
            if max<p:
               max=p
    elif method=='jaccard':
        for u, v, p in nx.jaccard_coefficient(g, ebunch=ebunch): # (u, v) = node indices, p = resource_allocation index
            tupl=(u,v,p)
            matrix.append(tupl) 
            if max<p:
               max=p
    elif method=='preferential':
        for u, v, p in nx.preferential_attachment(g, ebunch=ebunch): # (u, v) = node indices, p = resource_allocation index
            tupl=(u,v,p)
            matrix.append(tupl) 
            if max<p:
               max=p
    elif method=='resource_allocation':
        for u, v, p in nx.resource_allocation_index(g, ebunch=ebunch): # (u, v) = node indices, p = resource_allocation index
            tupl=(u,v,p)
            matrix.append(tupl) 
            if max<p:
               max=p
    else:
        return max,matrix_normalize

     # Normalize matrix
    if max==0:
       print(' predection none')
    else:
       for u, v, p in matrix: #u source v target p probability
          d=p/max
          tupl=(u,v,d)
          matrix_normalize.append(tupl) 
         
    return max,matrix_normalize
def test(train_test_split,method='adamic',split=0.025):
    result=[]
    adj_train, train_edges,test_edges,test_edges_false=train_test_split
    g= nx.Graph(adj_train)
    #40% of edges for test (hidden edges) 
    ebunch=get_ebunch(train_test_split)
    #1% links added for each iteration
    frac=int(len(ebunch)*split)
    print("init---------------")
    print("links added for each iteration:",frac)
    print("edges:",len(g.edges))
    print("tets_edges:",len(test_edges))
    print("tets_edges_false:",len(test_edges_false))
    print("method:",method)
    print('#-------------------')
    if method=='adamic':
        while len(ebunch)>0: 
          ebunchi=split_test(ebunch,frac=frac)
           # matrix=>1% of test edges (tuple(u,v,p))
          max,matrix=adamic_adar_sc(g,ebunchi)
           #new link added for networks
          new_link=new_Link(matrix,ebunch)
          #update networks
          g.add_edges_from(new_link)     
          result.append({'matrix':matrix,'new_link':new_link,'method':method})
          #test to avoid infinite loop
          if max==0:
                 max,matrix=adamic_adar_sc(g,ebunch) 
                 if max==0:
                     print('end prediction')
                     break
    elif method=='jaccard':
        while len(ebunch)>0:
          ebunchi=split_test(ebunch,frac=frac)
           # matrix=>1% of test edges (tuple(u,v,p))
          max,matrix=jaccard_coefficient_sc(g,ebunchi)
           #new link added for networks
          new_link=new_Link(matrix,ebunch)
          #update networks
          g.add_edges_from(new_link)
          result.append({'matrix':matrix,'new_link':new_link,'method':method})   
         #test to avoid infinite loop
          if max==0:
                 max,matrix=jaccard_coefficient_sc(g,ebunch) 
                 if max==0:
                     print('end prediction')
                     break
    elif method=='preferential':
        while len(ebunch)>0:
          ebunchi=split_test(ebunch,frac=frac)
           # matrix=>1% of test edges (tuple(u,v,p))
          max,matrix=preferential_attachment_sc(g,ebunchi)
           #new link added for networks
          new_link=new_Link(matrix,ebunch)
          #update networks
          g.add_edges_from(new_link)
          result.append({'matrix':matrix,'new_link':new_link,'method':method})
          #test to avoid infinite loop
          if max==0:
                 max,matrix=preferential_attachment_sc(g,ebunch) 
                 if max==0:
                     print('end prediction')
                     break
    elif method=='resource_allocation':
        while len(ebunch)>0:
          ebunchi=split_test(ebunch,frac=frac)
          # matrix=>1% of test edges (tuple(u,v,p))
          max,matrix=resource_allocation_sc(g,ebunchi)
          #new link added for networks
          new_link=new_Link(matrix,ebunch)
          #update networks
          g.add_edges_from(new_link)
          result.append({'matrix':matrix,'new_link':new_link,'method':method})
          #test to avoid infinite loop
          if max==0:
                 max,matrix=resource_allocation_sc(g,ebunch) 
                 if max==0:
                     print('end prediction')
                     break
    return result  
      
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
    #display_graph(1,g,pos_link=list_tuple(train_edges,None,False),method='graphe init vs test graph')
    g.remove_edges_from(test_edges)
   
    #display_graph(2,g,pos_link=list_tuple(test_edges,None,False),new_link=list_tuple(test_edges_false,None,False),method='test edges & new link ')
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
    return Result[time1-1]['matrix']
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
#-----------------------------------

if __name__ == '__main__':
       # use net.Graph() for undirected graph

# How to read from a file. Note: if your egde weights are int, 
# change float to int.
    #methods 'adamic','jaccard','preferential','resource_allocation'
    methods='jaccard'

    #dynamic graph
    dynamic=True

    #Graph's Parametres 
    P=0.3
    K=100
    M=3
    nbb=0
    Nodes=7
    g=json_graph.node_link_graph(Scale_free_networks(Nodes,M))
    #g=Scale_free_networks(Nodes,M)
    #g=json_graph.node_link_graph(Small_World_networks(Nodes,K,P))
    #g=json_graph.node_link_graph(Random_networks(Nodes,P))
    #g=json_graph.node_link_graph(facebook_graph())
    print(len(g.nodes),len(g.edges))
    k,c=Hybrid_method(g,[(1,5,0.5)],5,0.125)
    print(k,c)
    for nodes in range(7):
        print(nodes,g.nodes[nodes]['neighbors'])
       
    '''
    G=[]
    m=['B','BM','BCen','B'+Betas,BBD,'BBet','BCl','T','TM','TCen','T'+Betas,TBD,'TBet','TCl','NP']
    #m=['NP','B','NP']
    
    Nodes=len(g.nodes)
    static="Nodes :{},Edegs:{}."
    percentage=5 #percentage% of popularity" is infected 
    NumOFsumi=1
    beta=0.2
    omega=0
    juge=0.1
    delta=0
    K_seed=[]
    q=[1,2,3,4]
    for i in q:
        K_seed.append(int(Nodes*0.05*i))
    for i in range(len(m)*len(q)):
        G.append(g)
    print(K_seed)
    Tdet=2

    simulation_strategy(1,K_seed, Tdet,m,G)
    plt.show()
    
    adj_train, train_edges,test_edges,test_edges_false=train_test_split
    #calcule score
    
    new_links=[]
    for each in Result:
        for link in each['new_link']:
            new_links.append(link)
    print('calcul score............')
    start_time = time.time() 
    pos_link,neg_link,new_link=filter_list(test_edges,new_links)
    #rappl=Vrai_Pos/(Vrai)
    end_time = time.time() 
    print("time of execution=", end_time - start_time)
    rappel=len(pos_link)/len(test_edges)
    precision=len(pos_link)/len(new_links)
    f_score=2*rappel*precision/(rappel+precision)
    per=int(len(new_link)/len(test_edges_false)*100)
    print('------------score----------')
    print("method:",methods)
    print("rappel:",rappel)
    print("precision",precision)
    print("f_score",f_score)
    print("percentage of new links added: %",per)
    #display_graph(3,g,pos_link,fals_link,new_link,methods)

    #plt.show()'''