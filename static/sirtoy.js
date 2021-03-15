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
  int(G);
}

});
function int(G){
var valid_data = 1;
var running = 0;
var running1 = 0;
var NodeSelected = 0;
var time_interval = 10;
var count = 0;
var timeseries;
var End = 0;
var Statistical_anal=0;

var NodeDeg=[];
var nodeArray = G.nodes;
var edgeArray = G.links;
var ListInfectedNodes = [];
var Stat;

var time = 0.125;

var sir_color = { S: "#0000ff", I: "#ff0000", R: "#08b808", RuP: "#0f00f0" }
var Opinion_color = { N: "#0000ff", Su: "#039b8b", D: "#bbb01b" }

var epi_state = { S: nodeArray.length, I: 0, R: 0, OpP: 0, OpD: 0, RuP: 0 };

Stat={
  DD: { label: "Degree Distribution", color: "#0000ff", data: [] },
  ADD: { label: "Accepted Rumors", color: "#0000ff", data: [] },
  SDD: { label: "Sent Rumors", color: "#ff00ff", data: [] },

};
function reset_history() {
  timeseries = {
    S: { label: "S", color: sir_color.S, data: [] },
    I: { label: "Spreaders", color: sir_color.I, data: [] },
    R: { label: "Infected nodes", color: sir_color.R, data: [] },
    RuP: { label: "Rumor Popularity", color: sir_color.RuP, data: [] },
    OpP: { label: "Supporting Opinion", color: Opinion_color.Su, data: [] },
    OpD: { label: "Denying Opinion", color: Opinion_color.D, data: [] },
  };

  timeseries.S.data.push([count, epi_state.S]);
  timeseries.I.data.push([count, epi_state.I]);
  timeseries.R.data.push([count, epi_state.R]);
  timeseries.RuP.data.push([count, epi_state.RuP]);
  timeseries.OpP.data.push([count, epi_state.OpD]);
  timeseries.OpD.data.push([count, epi_state.OpD]);
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
var plotRP = $.plot($("#RumorPopuCurves"), [], plotOptions);
var plotOp = $.plot($("#OpinionCurves"), [], plotOptions);
var plotDD = $.plot($("#Nodes_degree_distribution"), [], plotOptions2);
var plotARDD = $.plot($("#Acc_RumorDD"), [], plotOptions2);
var plotSRDD = $.plot($("#Sent_RumorDD"), [], plotOptions2);




function getRandomIntInclusive(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return (Math.floor(Math.random() * (max - min + 1)) + min) / 100; //The maximum is inclusive and the minimum is inclusive 
}

var kArray = [];
var Node_opinion = [];

for (i in nodeArray) {
  kArray[nodeArray[i].id] = 0;
  nodeArray[i].Adj = [];
  
}

for (i in edgeArray) {
  s = edgeArray[i].source;
  t = edgeArray[i].target;
  kArray[s]++;
  kArray[t]++;
  nodeArray[s].Adj[nodeArray[s].Adj.length] = t;
  nodeArray[t].Adj[nodeArray[t].Adj.length] = s;

}


  
  var MaxDeg=0;


for (i in nodeArray) {
  nodeArray[i].k = kArray[i];
  if (MaxDeg<nodeArray[i].k) {
    MaxDeg=nodeArray[i].k;
    
  }
  nodeArray[i].state = "S";
  nodeArray[i].opinion = "N";
  min = Number($("#Beta_min").val());
  max = Number($("#Beta_max").val());
  nodeArray[i].beta = getRandomIntInclusive(min * 100, max * 100);
  min = Number($("#Omega_min").val());
  max = Number($("#Omega_max").val());
  nodeArray[i].omega = getRandomIntInclusive(min * 100, max * 100);
  min = Number($("#Delta_min").val());
  max = Number($("#Delta_max").val());
  nodeArray[i].delta = getRandomIntInclusive(min * 100, max * 100);
  min = Number($("#J_min").val());
  max = Number($("#J_max").val());
  nodeArray[i].j = getRandomIntInclusive(min * 100, max * 100);
  nodeArray[i].F_j = nodeArray[i].j;
  nodeArray[i].Infetime = 0;
  nodeArray[i].NbrAccpR = 0;
  nodeArray[i].NbrAccptDR = 0;
  nodeArray[i].NbrSendR = 0;
  nodeArray[i].ColorNode = "#00f";


}

for (let index = 1; index <= MaxDeg; index++) {
  NodeDeg[index]=0;
  
 
}

for (i in nodeArray) {
  NodeDeg[nodeArray[i].k]++;
  
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
var vis2 = d3.select("#graph-layout_opinion")
  .append("svg:svg")
  .attr("width", w)
  .attr("height", h)
  .call(d3.behavior.zoom().on("zoom", function () {
    vis2.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
  }))
  .append("g");

var vis = d3.select("#graph-layout")
  .append("svg:svg")
  .attr("width", w)
  .attr("height", h)
  .call(d3.behavior.zoom().on("zoom", function () {
    vis.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
  }))
  .append("g");

var force2 = d3.layout.force()
  .charge(-50)
  .linkStrength(0.5)
  .friction(0.6)
  .gravity(0.02)
  .linkDistance(100)
  .nodes(nodeArray)
  .links(edgeArray)
  .size([300, h]);

var force = d3.layout.force()
  .charge(-200)
  .linkStrength(0.5)
  .friction(0.5)
  .gravity(0.02)
  .linkDistance(100)
  .nodes(nodeArray)
  .links(edgeArray)
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

force2.on("tick", function () {
  vis2.selectAll("line.link")
    .attr("x1", function (d) { return d.source.x; })
    .attr("y1", function (d) { return d.source.y; })
    .attr("x2", function (d) { return d.target.x; })
    .attr("y2", function (d) { return d.target.y; });

  vis2.selectAll("circle.node")
    .attr("cx", function (d) { return d.x; })
    .attr("cy", function (d) { return d.y; })
    .style("fill", function (d) { return Opinion_color[d.opinion]; });
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

  x = vis.selectAll("line.link").data(edgeArray, function (d) { return d.source.name + "-" + d.target.name; });
  x.enter().insert("svg:line", "circle.node")
    .attr("class", "link")
    .attr("x1", function (d) { return d.source.x; })
    .attr("y1", function (d) { return d.source.y; })
    .attr("x2", function (d) { return d.target.x; })
    .attr("y2", function (d) { return d.target.y; });
  x.exit().remove();



  x = vis.selectAll("circle.node").data(nodeArray, function (d) { return d.name; });
  x.enter().insert("svg:circle")
    .attr("class", "node")
    .attr("cx", function (d) { return d.x; })
    .attr("cy", function (d) { return d.y; })
    .attr("r", function (d) { return 4 * Math.sqrt(d.k); })
    .style("fill", function (d) { return d.ColorNode; })
    .call(force.drag)
    .on("click", function (d, i) {
     
      if (running == 0 && valid_data == 1 && d.state == "S") {
        d.opinion = "Su";
        epi_state.OpP++;
        d.state = "I";
        epi_state.S--;
        epi_state.RuP += d.k;
        epi_state.I++;
        NodeSelected = 1;
        d.Infetime = time;
        d.NbrAccpR++;
        ListInfectedNodes[ListInfectedNodes.length] = i;
        d.ColorNode = "#f00";
      }
      update_counters();
      update_plot();
    })
    .on("mouseover", function (d) {
      div.transition()
        .duration(200)
        .style("opacity", .9);
      div.html("Node Id: " + d.name + "<br/>" + "Node degree: " + d.k
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

  x = vis2.selectAll("line.link").data(edgeArray, function (d) { return d.source.name + "-" + d.target.name; });
  x.enter().insert("svg:line", "circle.node")
    .attr("class", "link")
    .attr("x1", function (d) { return d.source.x; })
    .attr("y1", function (d) { return d.source.y; })
    .attr("x2", function (d) { return d.target.x; })
    .attr("y2", function (d) { return d.target.y; });
  x.exit().remove();



  x = vis2.selectAll("circle.node").data(nodeArray, function (d) { return d.name; });
  x.enter().insert("svg:circle")
    .attr("class", "node")
    .attr("cx", function (d) { return d.x; })
    .attr("cy", function (d) { return d.y; })
    .attr("r", function (d) { return 4 * Math.sqrt(d.k); })
    .style("fill", function (d) { return d.ColorNode; })
    .call(force2.drag)
    .on("click", function (d, i) {
      if (running == 0 && valid_data == 1 && d.state == "S") {
        d.opinion = "Su";
        d.state = "I";
        epi_state.OpP++;
        epi_state.S--;
        epi_state.RuP += d.k;
        epi_state.I++;
        d.NbrAccpR++;
        NodeSelected = 1;
        d.Infetime = time;
        ListInfectedNodes[ListInfectedNodes.length] = i;
        d.opinion = "Su";
        d.state = "I";
        d.ColorNode = "#f00";
      }
      else {
        if (running == 0 && valid_data == 1 && d.opinion == "D") {
          d.opinion = "Su";
          epi_state.OpP++;
          epi_state.OpD--;
        }
        else {
          d.opinion = "D";
          epi_state.OpP--;
          epi_state.OpD++;
        }
      }
      update_counters();
      update_plot();
    })
    .on("mouseover", function (d) {
      div.transition()
        .duration(200)
        .style("opacity", .9);
      div.html("Node Id: " + d.name + "<br/>"
        + "Node degree: " + d.k + "<br/>"
        + "Nbr of Acc. rumor: " + d.NbrAccpR + "<br/>"
        + "Nbr of Sent rumor: " + d.NbrSendR + "<br/>"
        + "Nbr of Acc. -Opi " + d.NbrAccptDR)
        .style("left", (d3.event.pageX + 50) + "px")
        .style("top", (d3.event.pageY - 50 ) + "px");
    })
    .on("mouseout", function (d) {
      div.transition()
        .duration(500)
        .style("opacity", 0);
    });
  x.exit().remove();
  force2.start();

}

function update_plot() {
  plot.setData([timeseries.I]);
  plot.setupGrid();
  plot.draw();

  plot2.setData([timeseries.R]);
  plot2.setupGrid();
  plot2.draw();

  plotRP.setData([timeseries.OpD, timeseries.OpP]);
  plotRP.setupGrid();
  plotRP.draw();


  plotOp.setData([timeseries.RuP]);
  plotOp.setupGrid();
  plotOp.draw();

}


function update_counters() {
  $("#count_I").html(epi_state.I);
  $("#count_R").html(epi_state.R);
  $("#count_S").html(epi_state.S);
  $("#count_SO").html(epi_state.OpP);
  $("#count_DO").html(epi_state.OpD);

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
function Start_propagation() {
 /* if (End == 1) {
	    rest_all();
	    if (NodeSelected == 1) {
	      $("#start-text").fadeOut();
	      $("#start-text2").fadeOut();

	      running = 1;
	    }
	    else {
	      var i = 1;
	      while (i <= 10) {
	        ID = Math.floor(Math.random() * nodeArray.length)
	        if (nodeArray[ID].Infetime == 0) {
	          nodeArray[ID].Infetime = 0.125;
	          nodeArray[ID].NbrAccpR++;
	          ListInfectedNodes[ListInfectedNodes.length] = ID;

	          if (Math.random() > 0.5) {
	            nodeArray[ID].opinion = "Su";
	            epi_state.OpP++;
	          }
	          else {
	            nodeArray[ID].opinion = "D";
	            nodeArray[ID].NbrAccptDR++;
	            epi_state.OpD++;
	          }
	          nodeArray[ID].state = "I"; epi_state.S--; epi_state.I++; epi_state.RuP += nodeArray[ID].k; NodeSelected = 1;
	          update_graph();
	          update_counters();
	          i++;
	        }
	      }
	      NodeSelected == 1;
	      $("#start-text").fadeOut();
	      $("#start-text2").fadeOut();
	      running = 1;
	    }
  }
  else {*/
    if (NodeSelected == 1) {
      $("#start-text").fadeOut();
      $("#start-text2").fadeOut();
       $('#Pause-button').prop('disabled', false);
      $('#Start-button').prop('disabled', true); 
      setInterval(run_HISBmodel, time_interval);
      running = 1;
    }
  /*  else {
      var i = 1;
      while (i <= 10) {
        ID = Math.floor(Math.random() * nodeArray.length)
        if (nodeArray[ID].Infetime == 0) {
          nodeArray[ID].state = "I";
          nodeArray[ID].Infetime = 0.125;
          ListInfectedNodes[ListInfectedNodes.length] = ID;
          nodeArray[ID].NbrAccpR++;
          if (Math.random() > 0.5) {

            nodeArray[ID].opinion = "Su";
            epi_state.OpP++;
          }
          else {
            nodeArray[ID].opinion = "D";
            epi_state.OpD++;
            nodeArray[ID].NbrAccptDR++;
          }
          epi_state.S--; epi_state.I++;
          epi_state.RuP += nodeArray[ID].k;
          NodeSelected = 1;
          update_graph();
          update_counters();
          update_plot();

          i++;
        }
      }

      update_plot();
      update_counters();
      NodeSelected == 1;
      $("#start-text").fadeOut();
      $("#start-text2").fadeOut();
      running = 1;
    }*/
  }
  

//}

function UpdateOpinion(i) {

  var DecFactor = (nodeArray[i].F_j + (nodeArray[i].NbrAccptDR / nodeArray[i].NbrAccpR)) * 0.5;

 
  if (nodeArray[i].opinion == "Su") epi_state.OpP--; else epi_state.OpD--;
  if (Math.random() <= DecFactor) {
    nodeArray[i].opinion = "D";
    epi_state.OpD++;


  }
  else {
    nodeArray[i].opinion = "Su";
    epi_state.OpP++;

  }

}

function reset_all() {

  running = 0;
  NodeSelected = 0;
  count = 0;
  End = 0;
  epi_state = { S: nodeArray.length, I: 0, R: 0, OpP: 0, OpD: 0, RuP: 0 };
  ListInfectedNodes = [];
  time = 0.125;

  reset_history();
  update_plot();

  update_counters();

  for (i in nodeArray) {
    nodeArray[i].state = "S";
    nodeArray[i].opinion = "N";
    min = Number($("#Beta_min").val());
    max = Number($("#Beta_max").val());
    nodeArray[i].beta = getRandomIntInclusive(min * 100, max * 100);
    min = Number($("#Omega_min").val());
    max = Number($("#Omega_max").val());
    nodeArray[i].omega = getRandomIntInclusive(min * 100, max * 100);
    min = Number($("#Delta_min").val());
    max = Number($("#Delta_max").val());
    nodeArray[i].delta = getRandomIntInclusive(min * 100, max * 100);
    min = Number($("#J_min").val());
    max = Number($("#J_max").val());
    nodeArray[i].j = getRandomIntInclusive(min * 100, max * 100);
    nodeArray[i].Infetime = 0;
    nodeArray[i].NbrAccpR = 0;
    nodeArray[i].NbrAccptDR = 0;
    nodeArray[i].NbrSendR = 0;
    nodeArray[i].ColorNode = "#00f";

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



  epi_state.RuP = 0;
  epi_state.I = 0;
  var ID = 0;

  for (ID = ListInfectedNodes.length - 1; ID >= 0; ID--) {

    var i;
    i = ListInfectedNodes[ID];

    NodeRelativeTime = time - nodeArray[i].Infetime;

    if (Math.exp(-NodeRelativeTime * nodeArray[i].beta) < 0.1) {
      ListInfectedNodes.splice(ID, 1);
      nodeArray[i].state = "R";



    }
    else {

      var ActualAttraction;
      ActualAttraction = Math.exp(-NodeRelativeTime * nodeArray[i].beta) * Math.abs(Math.sin(NodeRelativeTime * nodeArray[i].omega + nodeArray[i].delta));
      UpdateColor(i, ActualAttraction);
      epi_state.RuP += ActualAttraction * nodeArray[i].k;
      var SendingProbability;
      SendingProbability = ActualAttraction;

      var p = 0.35;


      if (Math.random() <= SendingProbability) {

        epi_state.I += 1;



        for (let index = 0; index < nodeArray[i].Adj.length - 1; index++) {
          j = nodeArray[i].Adj[index];

          if (Math.random() <= p) {
            nodeArray[i].NbrSendR++;
            AcceptanceProbability = nodeArray[i].k / (nodeArray[i].k + nodeArray[j].k) * 0.5;

            if (Math.random() <= AcceptanceProbability) {
              
              nodeArray[j].NbrAccpR++;

              if (nodeArray[j].Infetime == 0) {
                epi_state.R++;
                epi_state.S--;
                nodeArray[j].Infetime = time;
                ListInfectedNodes[ListInfectedNodes.length] = j;
                nodeArray[j].opinion = nodeArray[i].opinion;
                nodeArray[j].state = "I";
                if (nodeArray[j].opinion == "Su") {
                  epi_state.OpP++;

                } else {
                  epi_state.OpD++;
                  nodeArray[j].NbrAccptDR++;

                }
               


              }
              else {
                if (nodeArray[j].opinion == "D") nodeArray[j].NbrAccptDR++;
               
              }


            }

          }


        }
        UpdateOpinion(i);
      }

    }


  }

  update_graph();

  count++;
  time += 0.125;

  timeseries.S.data.push([time, epi_state.S]);
  timeseries.I.data.push([time, epi_state.I]);
  timeseries.R.data.push([time, epi_state.R]);
  timeseries.RuP.data.push([time, epi_state.RuP]);
  timeseries.OpP.data.push([time, epi_state.OpP]);
  timeseries.OpD.data.push([time, epi_state.OpD]);
  epi_state.I = 0;
  update_plot();

  update_counters();

  if (ListInfectedNodes.length == 0) { Update_stat(); running = 0; End = 1; };


}






function UpdateColor(i, Atrraction) {
  nodeArray[i].ColorNode = RGB2Color((256 * Atrraction), (256 * (1 - Atrraction)), 0);
}

function RGB2Color(r, g, b) {
  return 'rgb(' + Math.round(r) + ',' + Math.round(g) + ',' + Math.round(b) + ')';
}
Update_stat();

function Update_stat() {
  $("#Stat_NN").html(nodeArray.length);
  var NbrEdge = 0;
  var NbrRumorSent = 0;
  var NbrRumorA = 0;
  var b = 0;
  var o = 0;
  var h = 0;
  var jB = 0;
  var jA = 0;
  var NPOS = 0;
  var NDOS = 0;


  for (let index = 0; index < nodeArray.length; index++) {
    NbrEdge += nodeArray[index].k;
    NbrRumorSent += nodeArray[index].NbrSendR;
    NbrRumorA += nodeArray[index].NbrAccpR;
    b += nodeArray[index].beta;
    o += nodeArray[index].omega;
    h += nodeArray[index].delta;
    jB += nodeArray[index].j;
    jA += nodeArray[index].F_j;
    NDOS += nodeArray[index].NbrAccptDR;

  }
  NPOS += NbrRumorA - NDOS;
  $("#Stat_NE").html(NbrEdge);
  $("#Stat_k").html(Math.floor(NbrEdge / nodeArray.length * 1000) / 1000);
  $("#Stat_ASR").html(Math.floor(NbrRumorSent / nodeArray.length * 1000) / 1000);
  $("#Stat_AAR").html(Math.floor(NbrRumorA / nodeArray.length * 1000) / 1000);
  $("#Stat_AIBK").html(Math.floor(b / nodeArray.length * 1000) / 1000);
  $("#Stat_AFR").html(Math.floor(o / nodeArray.length * 1000) / 1000);
  $("#Stat_AHM").html(Math.floor(h / nodeArray.length * 1000) / 1000);
  $("#JB").html(Math.floor(jB / nodeArray.length * 1000) / 1000);
  $("#JA").html(Math.floor(jA / nodeArray.length * 1000) / 1000);
  $("#Stat_NRR").html(epi_state.R);
  $("#Stat_NnRR").html(epi_state.S);
  $("#Stat_RLT").html(time - 0.125);
  $("#Stat_SR").html(NbrRumorSent);
  $("#Stat_AR").html(NbrRumorA);
  $("#Stat_PO").html(NPOS);
  $("#Stat_DO").html(NDOS);
  update_Statistics() ;


}

function update_Statistics() {
  Stat.ADD.data=[];
  Stat.SDD.data=[];

  plotSRDD.setData([Stat.SDD]);
  plotSRDD.setupGrid();
  plotSRDD.draw();

  plotARDD.setData([Stat.ADD]);
  plotARDD.setupGrid();
  plotARDD.draw();    

  var AccRuorDeg=[];
  var SentRuorDeg=[];
  for (let index = 0; index < nodeArray.length; index++) {
    if (AccRuorDeg[nodeArray[index].k]== null)  AccRuorDeg[nodeArray[index].k]=nodeArray[index].NbrAccpR;else AccRuorDeg[nodeArray[index].k]+=nodeArray[index].NbrAccpR;
    if (SentRuorDeg[nodeArray[index].k]== null)  SentRuorDeg[nodeArray[index].k]=nodeArray[index].NbrSendR;else SentRuorDeg[nodeArray[index].k]+=nodeArray[index].NbrSendR;
    
  }


  for (let index = 1; index <= MaxDeg; index++) {
    if (NodeDeg[index] !=0 ) {
     
      Stat.ADD.data.push([index, AccRuorDeg[index]/NodeDeg[index]]);
      Stat.SDD.data.push([index, SentRuorDeg[index]/NodeDeg[index]]);
      
      
    }
    
    
  }
 
 

  
  plotSRDD.setData([Stat.SDD]);
  plotSRDD.setupGrid();
  plotSRDD.draw();

  plotARDD.setData([Stat.ADD]);
  plotARDD.setupGrid();
  plotARDD.draw();



}
}
});