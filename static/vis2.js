//  G= $.getJSON("HISBmodel/G.json", function(data) {


//      return data;

// });
// g=JSON.parse(G);
// console.log(g);
$(function(){
  var G;
  
  var data={
    "type": "small world",
    "proba": 0.3,
    "neighbors":10,
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
    G=data;
    intIC(G);
  }
  
  });
  function intIC(G){
  var valid_data = 1;
  var running = 0;
 
  var NodeSelected = 0;
  var time_interval = 10;
  var count = 0;
  var timeseries;
  var End = 0;
  
  
  var NodeDeg=[];
  var nodeArrayIC = G.nodes;
  var edgeArrayIC = G.links;
  var ListInfectedNodes = [];
  var Stat;
 
  var time = 0.125;
  
  var sir_color = { S: "#0000ff", I: "#ff0000", R: "#08b808" }
  
  
  var epi_state = { S: nodeArrayIC.length, I: 0, R: 0};
  
  Stat={
    DD: { label: "Degree Distribution", color: "#0000ff", data: [] },
  
  };
  function reset_history() {
    timeseries = {
      S: { label: "S", color: sir_color.S, data: [] },
      I: { label: "Spreaders", color: sir_color.I, data: [] },
      R: { label: "Infected nodes", color: sir_color.R, data: [] },
    };
  
    timeseries.S.data.push([count, epi_state.S]);
    timeseries.I.data.push([count, epi_state.I]);
    timeseries.R.data.push([count, epi_state.R]);
   
  }
  
  reset_history();
  // pour dessier les graphes resutat 1
  var plotOptions = {
    lines: { show: true },
    
    xaxis: { min: 0 },
    series: { shadowSize: 0 }
  
  };
  // pour dessier les graphes statistique 
  var plotOptions2 = {
    lines: { show: false },
    points: { show: true },
    xaxis: { min: 0 },
    series: { shadowSize: 0 }
  
  };
  
  var plot = $.plot($("#epicurves"), [], plotOptions);
  var plot2 = $.plot($("#Infcurves2"), [], plotOptions);
  var plotDD = $.plot($("#Nodes_degree_distribution"), [], plotOptions2);

  var kArray = [];
 
  
  for (i in nodeArrayIC) {
    kArray[nodeArrayIC[i].id] = 0;
    nodeArrayIC[i].Adj = [];
    
  }
  
  for (i in edgeArrayIC) {
    s = edgeArrayIC[i].source;
    t = edgeArrayIC[i].target;
    kArray[s]++;
    kArray[t]++;
    nodeArrayIC[s].Adj[nodeArrayIC[s].Adj.length] = t;
    nodeArrayIC[t].Adj[nodeArrayIC[t].Adj.length] = s;
  
  }
  
  
    
    var MaxDeg=0;
  
  
  for (i in nodeArrayIC) {
    nodeArrayIC[i].k = kArray[i];
    if (MaxDeg<nodeArrayIC[i].k) {
      MaxDeg=nodeArrayIC[i].k;
      
    }
    nodeArrayIC[i].state = "S";
    nodeArrayIC[i].ColorNode = "#00f";
  
  
  }
  
  for (let index = 1; index <= MaxDeg; index++) {
    NodeDeg[index]=0;
    
   
  }
  
  for (i in nodeArrayIC) {
    NodeDeg[nodeArrayIC[i].k]++;
    
  }
  
  for (let index = 1; index <= MaxDeg; index++) {
    if (NodeDeg[index] !=0 ) {
      Stat.DD.data.push([index, NodeDeg[index]]); 
    }
    
  }
  
  plotDD.setData([Stat.DD]);
  plotDD.setupGrid();
  plotDD.draw();
  
  
  
  var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);
  
  var w = "100%";
  var h = 650;

  var vis = d3.select("#graph-layout")
    .append("svg:svg")
    .attr("width", w)
    .attr("height", h)
    .call(d3.behavior.zoom().on("zoom", function () {
      vis.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
    }))
    .append("g");

  var force = d3.layout.force()
    .charge(-200)
    .linkStrength(0.5)
    .friction(0.5)
    .gravity(0.02)
    .linkDistance(100)
    .nodes(nodeArrayIC)
    .links(edgeArrayIC)
    .size([300, h]);
  
  
  force.on("tick", function () {
    vis.selectAll("line.link")
      .attr("x1", function (d) { return d.source.x; })
      .attr("y1", function (d) { return d.source.y; })
      .attr("x2", function (d) { return d.target.x; })
      .attr("y2", function (d) { return d.target.y; });
  
    vis.selectAll("circle.node")
      .attr("cx", function (d) { return d.x; })
      .attr("cy", function (d) { return d.y; })
      .style("fill", function (d) { return d.ColorNode; });
  });
  
  $("#Time_sime").val(time_interval)
  $("#Time_sime").keyup(update_Sim_time);
  
  
  update_graph();
  update_plot();
  update_counters();
  
  $("#reset-button").click(reset_all);
  $("#Start-button").click(Start_propagation);
  $("#Pause-button").click(Pause_sim);
  function Pause_sim() {
    $('#Pause-button').prop('disabled', true);
    if (running == 1) {
      running = 0;
    }
    $('#Start-button').prop('disabled', false);
  }
  
  
  
  function update_graph() {
  
    x = vis.selectAll("line.link").data(edgeArrayIC, function (d) { return d.source.name + "-" + d.target.name; });
    x.enter().insert("svg:line", "circle.node")
      .attr("class", "link")
      .attr("x1", function (d) { return d.source.x; })
      .attr("y1", function (d) { return d.source.y; })
      .attr("x2", function (d) { return d.target.x; })
      .attr("y2", function (d) { return d.target.y; });
    x.exit().remove();
  
  
  
    x = vis.selectAll("circle.node").data(nodeArrayIC, function (d) { return d.id; });
    x.enter().insert("svg:circle")
      .attr("class", "node")
      .attr("cx", function (d) { return d.x; })
      .attr("cy", function (d) { return d.y; })
      .attr("r", function (d) { return 4 * Math.sqrt(d.k); })
      .style("fill", function (d) { return d.ColorNode; })
      .call(force.drag)
      .on("click", function (d, i) {
       
        if (running == 0 && valid_data == 1 && d.state == "S") {
          d.state = "I";
          epi_state.S--;
          epi_state.I++;
          NodeSelected = 1;
          ListInfectedNodes[ListInfectedNodes.length] = i;
          d.ColorNode = "#f00";
        }
        else 
          if(running == 0 && valid_data == 1 && d.state == "I"){
            d.state = "S";
            epi_state.S++;
            epi_state.I--;
            NodeSelected = 1;
            d.ColorNode = "#00f";
            ListInfectedNodes.splice(i, 1);

        }
        update_counters();
        update_plot();
      })
      .on("mouseover", function (d) {
        div.transition()
          .duration(200)
          .style("opacity", .9);
        div.html("Node Id: " + d.id + "<br/>" + "Node degree: " + d.k
          + "<br/>" + "Beta: " + d.beta
          + "<br/>" + "omega: " + d.omega
          + "<br/>" + "delta: " + d.delta
          + "<br/>" + "delta: " + d.j
          + "<br/>" + "Color: " + d.ColorNode)
          .style("left", (d3.event.pageX+50) + "px")
          .style("top", (d3.event.pageY-50) + "px");
      })
      .on("mouseout", function (d) {
        div.transition()
          .duration(500)
          .style("opacity", 0);
      });
  
    x.exit().remove();
    force.start();
  
  }
  
  function update_plot() {
    plot.setData([timeseries.I]);
    plot.setupGrid();
    plot.draw();
  
    plot2.setData([timeseries.R]);
    plot2.setupGrid();
    plot2.draw();
  
  }
  
  
  function update_counters() {
    $("#count_I").html(epi_state.I);
    $("#count_R").html(epi_state.R);
    $("#count_S").html(epi_state.S);
  
  }
  
  
  
  function update_Sim_time() {
    p = Number($("#Time_sime").val());
    if (isNaN(p) || p < 0.0 || p > 2000) {
      valid_data = 0;
      $("#Time_sime").css("background-color", "#f88");
    } else {
      time_interval = p;
      valid_data = 1;
  
      $("#Time_sime").css("background-color", "#fff");
    }
    setInterval(run_SIR, time_interval);
  }
  var diffusion=[];
  var nbr=0;
  function Start_propagation() {
      if (ListInfectedNodes.length >0) {
        if(diffusion.length==0){
        var data={
          "model": "IC",
          "Probability": 0.3,
          "Infected":ListInfectedNodes
        };
        $.ajax({
            url:"/diffusion",
            type:"POST",
            contentType: 'application/json; charset=utf-8',
            data:JSON.stringify(data),
            dataType:"json",
            success:function(data)
            {
                
            for(var i=0 ;i<data.length;i++){
                diffusion.push(data[i]);
             
            }
            $("#start-text").fadeOut();
            $("#start-text2").fadeOut();
            $('#Pause-button').prop('disabled', false);
            $('#Start-button').prop('disabled', true); 
            setInterval(run_HISBmodel, time_interval);
            running = 1;
          }
              
        });
       }
        restart();
       
      }
   
    }
    
  function restart(){
    $("#start-text").fadeOut();
    $("#start-text2").fadeOut();
    $('#Pause-button').prop('disabled', false);
    $('#Start-button').prop('disabled', true); 
    setInterval(run_HISBmodel, time_interval);
    running = 1;
  }
  
  
  function reset_all() {
    running = 0;
    NodeSelected = 0;
    count = 0;
    End = 0;
    epi_state = { S: nodeArrayIC.length, I: 0, R: 0};
    ListInfectedNodes = [];
    diffusion=[];
    time = 0.125;
  
    reset_history();
    update_plot();
  
    update_counters();
  
    for (i in nodeArrayIC) {
      nodeArrayIC[i].state = "S";
      nodeArrayIC[i].ColorNode = "#00f";
  
    }
    update_graph();
  
    $("#start-text").fadeIn();
    $("#start-text2").fadeIn();
    $('#Start-button').prop('disabled', false);
    $('#Pause-button').prop('disabled', false);
  }
  

  
  function run_HISBmodel() {
  
    if (running == 0) {
      return;
    }
    epi_state.I = 0;
    var ID = 0;
    var vol=diffusion[nbr];
    nbr++; 
    for (ID = ListInfectedNodes.length - 1; ID >= 0; ID--) {
      nodeArrayIC[ListInfectedNodes[ID]].ColorNode="#08b808";
      nodeArrayIC[ListInfectedNodes[ID]].state = "R";
      ListInfectedNodes.splice(ID, 1);
          epi_state.R++;
        }
        ID=0;
    if(nbr>=diffusion.length-1){ Update_stat(); running = 0; End = 1; }
    else{
    for (ID = vol.length - 1; ID >= 0; ID--) {  
   
      nodeArrayIC[vol[ID]].ColorNode = "#ff0000"
      ListInfectedNodes[ListInfectedNodes.length] = vol[ID]; 
      nodeArrayIC[vol[ID]].state = "I";
      epi_state.S--;
      epi_state.I++; 

      }
     
    }
      
    update_graph();
  
    count++;
  
    timeseries.S.data.push([time, epi_state.S]);
    timeseries.I.data.push([time, epi_state.I]);
    timeseries.R.data.push([time, epi_state.R]);
    
    update_plot();
    update_counters();
    
  }
  
  Update_stat();
  
  function Update_stat() {
    $("#Stat_NN").html(nodeArrayIC.length);
    var NbrEdge = 0;
    
    var jB = 0;
    var jA = 0;
    
  
  
    for (let index = 0; index < nodeArrayIC.length; index++) {
      NbrEdge += nodeArrayIC[index].k;
      jB += nodeArrayIC[index].j;
      jA += nodeArrayIC[index].F_j;
  
    }
    $("#Stat_NE").html(NbrEdge);
    $("#Stat_k").html(Math.floor(NbrEdge / nodeArrayIC.length * 1000) / 1000);
   
    $("#JB").html(Math.floor(jB / nodeArrayIC.length * 1000) / 1000);
    $("#JA").html(Math.floor(jA / nodeArrayIC.length * 1000) / 1000);
    $("#Stat_NRR").html(epi_state.R);
    $("#Stat_NnRR").html(epi_state.S);
    $("#Stat_RLT").html(time - 0.125);
   
  
  
  
  }
  
  
  }

    
  });