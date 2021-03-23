from networkx.readwrite import json_graph
import networkx as nx
#-----------------------------------------
  # g = nx.barabasi_albert_graph(N, M)
  # g= nx.watts_strogatz_graph(N,K,P)
  # g=nx.erdos_renyi_graph(N,P)
#-----------------------------------------



def Random_networks ( N=300 ,P=0.3):
    # Erdős-Rényi graph
    # number of nodes
    # expected number of partners
   
    
    g = nx.gnp_random_graph(N, P)  
    return graphe_TO_json(g)

def Scale_free_networks (N=300,M=10):
    #Barabasi_albert graph
    #N= Number of nodes
    #M= Number of edges to attach from a new node to existing nodes
    if(N is None):
        N=300
 
    if(M is None):
        M=0.5
    g=nx.barabasi_albert_graph(N,M)
    return graphe_TO_json(g)

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
    data['nodes'] = [ {"id": i,"state":"non_infected","opinion":"Nç ","beta":0,"omega":0,"delta":0,"jug":0,"Infetime":0,"NbrAccpR":0,"NbrSendR":0,"NbrAccpNegR":0,"value":0,"infected":'false',"degree":g.degree[i],"adj":[n for n in g.neighbors(i)]} for i in range(len(data['nodes'])) ]
    data['links'] = [ {"source":u,"target":v,"weight":(g.degree[u]+g.degree[v])/2} for u,v in g.edges ]
    return data

print(Small_World_networks(100)["nodes"][99])

#n= 300           # Number of nodes in graph
#alpha=0.41       # Probability for adding a new node connected to an existing node chosen randomly according to the in-degree distribution.
#beta =0.54       # Probability for adding an edge between two existing nodes. One existing node is chosen randomly according the in-degree distribution and the other chosen randomly according to the out-degree distribution.
#amma =0.05      # Probability for adding a new node connected to an existing node chosen randomly according to the out-degree distribution.
#delta_in =0.2    # Bias for choosing nodes from in-degree distribution.
#delta_out =0     # Bias for choosing nodes from out-degree distribution.
#g=nx.scale_free_graph(n,alpha,beta,gamma,delta_in=0,2,delta_out=0)