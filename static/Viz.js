     
     
      $(function() {
        
       
        var Infected=[];//Infected List Initial
        var graph ;  
        var toggle = 0;// Toggle for ego networks on click (below).
        var linkedByIndex = {};
        var degreeSize ;
        var link;
        var node;
        var color = ["red", "blue"]; //Blue=>for Nodes No Infected, Red=>for Nodes Infected
        //---Initialization of graph**************************    
        var data={
            "type": "random",
            "proba": 0.3,
            "neighbors":7,
            "NbrOFnoeds":300
          };
          $.ajax({
          url:"/gene_graph",
          type:"POST",
          contentType: 'application/json; charset=utf-8',
          data:JSON.stringify(data),
          dataType:"json",
          success:function(data)
          {
            graph=data;
            init()   ;    }
          
          });
              
        //start propagation simulation********************************************
         
        //Visialization Network******************
           //div Of Network
            var svg = d3.select("svg"),
                width = +svg.attr("width"),
                height = +svg.attr("height");
            // Call zoom for svg container.
            //svg.call(d3.zoom().on('zoom', zoomed));
           
           
            //simulation
            var simulation = d3.forceSimulation()
            .force("link", d3.forceLink())//Or to use names rather than indices: .id(function(d) { return d.id; }))
            .force("charge", d3.forceManyBody().strength([-100]).distanceMax([250]))
            .force("center", d3.forceCenter(width / 2, height / 2));
             //Container
            var container = svg.append('g');
            // Create form for search nodes (see function below).
            var search = d3.select("body").append('form').attr('onsubmit', 'return false;');
        
            var box = search.append('input')
                .attr('type', 'text')
                .attr('id', 'searchTerm')
                .attr('placeholder', 'Type to search...');
        
             var button = search.append('input')
                .attr('type', 'button')
                .attr('value', 'Search')
                .on('click', function () { searchNodes(); });
                var button1 = search.append('input')
                .attr('type', 'button')
                .attr('value', 'start')
                .on('click', function () { startOFpropagtion(); });
             // A slider (using only d3 and HTML5) that removes nodes below the input threshold.
            var slider = d3.select('body').append('p').text('Edge Weight Threshold: ');
            // A function to test if two nodes are neighboring.
            function neighboring(a, b) {
                return linkedByIndex[a.index + ',' + b.index];
            }
            function initializeDisplay(){
                link = container.append("g")
                 .attr("class", "links")
                 .selectAll("line")
                 .data(graph.links, function(d) { return d.source + ", " + d.target;})
                 .enter().append("line")
                 .attr('class', 'link');
           
                node = container.append("g")
                 .attr("class", "nodes")
                 .selectAll("circle")
                 .data(graph.nodes)
                 .enter().append("circle")
              // Calculate degree centrality within JavaScript.
              //.attr("r", function(d, i) { count = 0; graph.links.forEach(function(l) { if (l.source == i || l.target == i) { count += 1;}; }); return size(count);})
              // Use degree centrality from NetworkX in json.
              .attr('r', function(d, i) { return degreeSize(d.degree); })   
              .attr("fill", color[1])
              .attr('class', 'node') 
              .attr('id',function(d) { return "node"+d.id; })     
              // On click, toggle ego networks for the selected node.
              .on('dblclick', function(d, i) {
                    if (toggle == 0) {
                        // Ternary operator restyles links and nodes if they are adjacent.
                        d3.selectAll('.link').style('stroke-opacity', function (l) {
                            return l.target == d || l.source == d ? 1 : 0.1;
                        });
                        d3.selectAll('.node').style('opacity', function (n) {
                            return neighboring(d, n) ? 1 : 0.1;
                        });
                        d3.select(this).style("opacity", 1);
                              
                       
                       /*d3.selectAll('.link').transition().ease(d3.easeLinear)        
                       .duration(1000).delay(2000).style('stroke-opacity', '0.6');
                        d3.selectAll('.node').transition().ease(d3.easeLinear)       
                        .duration(1000).delay(2000).style('opacity', '1');*/
                        toggle = 1;
                    }
                    else{
                        // Restore nodes and links to normal opacity.
                        d3.selectAll('.link').style('stroke-opacity', '0.6');
                        d3.selectAll('.node').style('opacity', '1');
                        toggle = 0;
                }
                    
                })
               
                .on('click',function(){
                    d3.select(this)
                    .call(Status);
                })
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
          
            node.append("title")
                .text(function(d) { return "Node:" + d.id + "\n" + "Degree: " + d.degree + "\n" + "Infected: " + d.infected;});
          
            }
            //function for chang color of node
           
            function Status(element){
               element.style("fill", function (d) {
                 if(d.infected==true)
                 {//if a node is infected
                    Infected.pop(d.id);
                    d.infected=false;
                    return color[1];
                 }
                 else{
                    Infected.push(d.id);
                    d.infected=true;
                    return color[0];
                 }
                
               });
            element.select('title').text(function(d) { return "Node:" + d.id + "\n" + "Degree: " + d.degree + "\n" + "Infected: " + d.infected;});
             

            }
            function initializeSimulation(data) {
                simulation
                .nodes(graph.nodes)
                .on("tick", ticked)
                .force("link")
                .links(data);

            }
            function ticked() {
                link
                    .attr("x1", function(d) { return d.source.x; })
                    .attr("y1", function(d) { return d.source.y; })
                    .attr("x2", function(d) { return d.target.x; })
                    .attr("y2", function(d) { return d.target.y; });
            
                node
                    .attr("cx", function(d) { return d.x; })
                    .attr("cy", function(d) { return d.y; });
              }
            function DynamDraph(){
                slider.append('label')
                      .attr('for', 'threshold')
                      .text('1');
                  slider.append('input')
                      .attr('type', 'range')
                      .attr('min', d3.min(graph.links, function(d) {return d.weight; }))
                      .attr('max', d3.max(graph.links, function(d) {return d.weight; }))
                      .attr('value', d3.min(graph.links, function(d) {return d.weight; }))
                      .attr('id', 'threshold')
                      .style('width', '50%')
                      .style('display', 'block')
                      .on('input', function () { 
                          var threshold = this.value;
              
                          d3.select('label').text(threshold);
                          // Find the links that are at or above the threshold.
                          var newData = [];
                          graph.links.forEach( function (d) {
                              if (d.weight >= threshold) {newData.push(d); };
                          });
                          // Data join with only those new links.
                          link = link.data(newData, function(d) {return d.source + ', ' + d.target;});
                          link.exit().remove();
                          var linkEnter = link.enter().append('line').attr('class', 'link');
                          link = linkEnter.merge(link);
                          node = node.data(graph.nodes);
                          // Restart simulation with new link data.
                          initializeSimulation(newData);
                          simulation.alphaTarget(0.1).restart();
              
                      });
            }
        /* Initialisation  */
            function init() {
                // Make object of all neighboring nodes.
                graph.links.forEach(function(d) {
                    linkedByIndex[d.source + ',' + d.target] = 1;
                    linkedByIndex[d.target + ',' + d.source] = 1;
                });
                // Linear scale for degree centrality.
                 degreeSize = d3.scaleLinear()
                    .domain([d3.min(graph.nodes, function(d) {return d.degree; }),d3.max(graph.nodes, function(d) {return d.degree; })])
                    .range([8,25]);
                // Collision detection based on degree centrality.
                simulation.force("collide", d3.forceCollide().radius( function (d) { return degreeSize(d.degree); }));
                initializeDisplay();
                initializeSimulation(graph.links); 
                DynamDraph();
                  // A dropdown menu with three different centrality measures, calculated in NetworkX.
                  // Accounts for node collision.
                  var dropdown = d3.select('body').append('div')
                      .append('select')
                      .on('change', function() { 
                          var centrality = this.value;
                          var centralitySize = d3.scaleLinear()
                              .domain([d3.min(graph.nodes, function(d) { return d[centrality]; }), d3.max(graph.nodes, function(d) { return d[centrality]; })])
                              .range([8,25]);
                          node.attr('r', function(d) { return centralitySize(d[centrality]); } );  
                          // Recalculate collision detection based on selected centrality.
                          simulation.force("collide", d3.forceCollide().radius( function (d) { return centralitySize(d[centrality]); }));
                          simulation.alphaTarget(0.1).restart();
                      });
              
                  dropdown.selectAll('option')
                      .data(['Degree Centrality', 'Betweenness Centrality', 'Eigenvector Centrality'])
                      .enter().append('option')
                      .attr('value', function(d) { return d.split(' ')[0].toLowerCase(); })
                      .text(function(d) { return d; });
              
              };
              var diffusion=[];
              var anim;
              var nbr=0;
              function startOFpropagtion(){
                
                //data to start simulation{TypeOfmodel,Probability,Infected nodes}
               var data={
                        "model": "IC",
                        "Probability": 0.3,
                        "Infected":Infected
                    };
                $.ajax({
                    url:"/diffusion",
                    method:"POST",
                    contentType: 'application/json; charset=utf-8',
                    data:JSON.stringify(data),
                    dataType:"json",
                    success:function(data)
                    {
                        
                    for(var i=0 ;i<data.length;i++){
                         diffusion.push(data[i]);
                    }
                    
                     animation();
                   }
                      
                });
            }
                
            function animation() {
               anim=setInterval(() => {
                start();  
                 
                }
                , 1500);
            }
            function start() {
                nbr++; 
                var vol=diffusion[nbr];
               
                if(nbr>=diffusion.length-1){
                  clearInterval(anim);
                  
                 }
                else
                  for(var id=0;id<vol.length;id++){
                    Status(d3.select("#node"+vol[id]));
                    //console.log(vol[id]);
                  }
                
            }
              function dragstarted(d) {
                if (!d3.event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
              }
              
              function dragged(d) {
                d.fx = d3.event.x;
                d.fy = d3.event.y;
              }
              
              function dragended(d) {
                if (!d3.event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
              }
              
              // Zooming function translates the size of the svg container.
             function zoomed() {
                    container.attr("transform", "translate(" + d3.event.transform.x + ", " + d3.event.transform.y + ") scale(" + d3.event.transform.k + ")");
             }
              
              // Search for nodes by making all unmatched nodes temporarily transparent.
            function searchNodes() {
                  var term = document.getElementById('searchTerm').value;
                  var selected = container.selectAll('.node').filter(function (d, i) {
                      return d.degree!=term ;});
                  selected.style('opacity', '0');
                  var link = container.selectAll('.link');
                  link.style('stroke-opacity', '0');
                  d3.selectAll('.node').transition()
                      .duration(5000)
                      .style('opacity', '1');
                  d3.selectAll('.link').transition().duration(5000).style('stroke-opacity', '0.6');
            }
        });