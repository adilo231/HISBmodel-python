from flask import Flask, render_template, request, jsonify
from graphs import gene,models
import numpy as np
import json
import networkx as nx
from networkx.readwrite import json_graph

#BigData json
def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()



app = Flask(__name__)

# Your codes .... 

#initialization
graph=None
typeOfGraph=["small world","scale free","random"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/model_propagation', methods=['POST'])
def model_propagation():
    if request.method== "POST":
      global graph
      model=request.form['model']
      index=request.form['type']
      N=request.form['NbrOFnoeds']
      K=request.form['neighbors']
      P=request.form['proba']
      print(N)
      print(K)
      print(model)
      N=int(N)
      K=int(K)
      P=float(P)

      if index=="0":
            graph=gene.Small_World_networks(N=N,K=K,P=P)
      elif index=="1":
            graph=gene.Scale_free_networks(N=N,M=K)
      else:
            graph=gene.Random_networks(N=N,P=P)

      if model=="3":
        return render_template('model.html',model="IC")
      elif model=="2":
        return render_template('model.html',model="LT")
      elif model=="1":
       
        return render_template('model_HISB.html',model="HISB")
      else:
          return render_template('index.html')

@app.route('/gene_graph', methods=['POST'])
def gene_graph():
    if request.method== "POST":
        global graph
        #data request format is json {model:"xx",Probability:"float",Infected:[id of nodes]}
       # data=request.get_json(force=True)
        #type of model{LT or IC}
        #type=data['type']
        #List of infected nodes
        #if(type in typeOfGraph):
        #infection threshold
       #     index=typeOfGraph.index(type)
       #     N=data['NbrOFnoeds']
        #    K=data['neighbors']
         #   P=data['proba']
            #check the data
         #   if index==0:
         #      graph=gene.Small_World_networks(N=N,K=K,P=P)
         # elif index==1:
          #      graph=gene.Scale_free_networks(N=N,M=K)
           # else:
           #      graph=gene.Random_networks(N=N,P=P)
            
        return json.dumps(graph,default=np_encoder)
        
        #return jsonify({'error' : 'missing model type! !'}) 
    
    return jsonify({'error' : 'missing !'}) 
    


@app.route('/diffusion', methods=['POST'])
def diffusion():
    if request.method== "POST":
        #data request format is json {model:"xx",Probability:"float",Infected:[id of nodes]}
        data=request.get_json(force=True)
       
        #type of model{LT or IC}
        typeOf_model=data['model']
        #List of infected nodes
        Seed_Set=data['Infected']
        #infection threshold
        Probability=float(data['Probability'])
        #check the data
        if typeOf_model and Seed_Set and Probability:
            global graph
            if graph:
                #independence cascade model
                if typeOf_model=="IC":
                    resultat=models.IC(json_graph.node_link_graph(graph),Seed_Set,Probability)
                    #data format is json: list of list (array) to json
                    return json.dumps(resultat,default=np_encoder)

                else:
                    #threshold linear model
                    resultat=models.LT(json_graph.node_link_graph(graph),Seed_Set,Probability)
                    #data format is json: list of list (array) to json
                    return json.dumps (resultat, default=np_encoder)
    
            return jsonify({'error' : 'missing !'}) 
   
        return jsonify({'error' : 'missing model type!'}) 
    

if __name__ == '__main__':

    app.run(debug=True) 