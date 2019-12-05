// create an array with nodes
function builtNetwork(container, dmap, dchem ){

    var lnodes = [{ id: 1, label: dchem.CAS, color: "red" }]
    var inode = 2;
    var ledges = [];

    var flagnode = 0;

    console.log(dmap);
    console.log("dkldkdl");
    for(var assay in dmap){
        var IDassay = searchNodeID(assay, lnodes);
        if(IDassay == 0){
            var node = {id: inode, label: assay, color: "pink"};
            lnodes.push(node);
            IDassay = inode;
            inode = inode + 1;
        }
        for(var system in dmap[assay]){
            for(var organ in dmap[assay][system]){
                // control assays to chemical
                var inledge = edgeIncludes(1, IDassay, ledges);
                if(inledge == 0){
                    var AC50 = Math.round(dmap[assay][system][organ]["AC50"], 2);
                    var AC50 = AC50.toString() + " microM";
                    //console.log(AC50);
                    var edge =  { from: 1, to: IDassay, label: AC50, color: "red" };
                    ledges.push(edge);
                    //inode = inode + 1;
                }

                // add assays node to chemical
                
                //gene
                var gene = dmap[assay][system][organ]["gene"];
                var gene = gene[0];
                if(gene == "NA"){
                    var iorgan = searchNodeID(organ, lnodes);
                    if(iorgan == 0){
                        var node = {id: inode, label: organ, color: "blue"};
                        lnodes.push(node);
                        iorgan = inode;
                        inode = inode + 1;
                        //connect to system
                        var IDsystem = searchNodeID(system, lnodes);
                        if(IDsystem == 0){
                            var node = {id: inode, label: system, color: "orange"};
                            lnodes.push(node);
                            IDsystem = inode;
                            inode = inode + 1;
                        }
                        edge = { from: IDsystem, to: iorgan};
                        ledges.push(edge);
                    }

                    var inledges = edgeIncludes(IDassay, iorgan, ledges);
                    if(inledges == 0){
                        var edge = { from: iorgan , to: IDassay, color:"blue"};
                        ledges.push(edge)
                    }
                }else{
                    var igene =  searchNodeID(gene, lnodes);
                    var iorgan = searchNodeID(organ, lnodes);
                    var exp = dmap[assay][system][organ]["exp"][0];
                    if(exp < 2.0 ){
                        continue;
                    }
                    
                    if (igene == 0){
                        var node = {id: inode, label: gene, color: "green"};
                        lnodes.push(node);
                        igene = inode;
                        inode = inode + 1;
                    }
                    if(iorgan == 0){
                        var node = {id: inode, label: organ, color: "blue"};
                        lnodes.push(node);
                        iorgan = inode;
                        inode = inode + 1;
                        //connect to system
                        var IDsystem = searchNodeID(system, lnodes);
                        if(IDsystem == 0){
                            var node = {id: inode, label: system, color: "orange"};
                            lnodes.push(node);
                            IDsystem = inode;
                            inode = inode + 1;
                        }
                        edge = { from: IDsystem, to: iorgan};
                        ledges.push(edge);
                    }

                    var inledges = edgeIncludes(igene, IDassay, ledges)
                   
                    var exp =  Math.round(exp);
                    var exp = exp.toString() + " fold";
                   
                    if (inledges == 0){
                        var edge = { from: igene, to: IDassay, color:"green"};
                        ledges.push(edge)
                    }
                    var inledges = edgeIncludes(igene, iorgan, ledges)
                    if (inledges == 0){
                        var edge = { from: igene, to: iorgan, label: exp, color: "blue"};
                        ledges.push(edge)
                    }

                }

            }
        }
    }
    //console.log(ledges);
    //console.log(lnodes);
    var data = {
        nodes: lnodes,
        edges: ledges
    };


    var options = {
        nodes: {
          shape: "dot",
          scaling: {
            min: 10,
            max: 30
          },
          //font: {
         //   size: 12,
         //   face: "Tahoma"
          //}
        },
        edges: {
          width: 0.15,
          color: { inherit: "from" },
          smooth: {
            type: "continuous"
          }
        },
        physics: {
          stabilization: false,
          barnesHut: {
            gravitationalConstant: -80000,
            springConstant: 0.001,
            springLength: 200
          }
        },
        interaction: {
          tooltipDelay: 200,
          hideEdgesOnDrag: true
        }
      };

    //var options = {
    //    nodes: { font: { strokeWidth: 0 } },
    //    edges: { font: { strokeWidth: 0 } }
    //};
    var network = new vis.Network(container, data, options);
}


function searchNodeID(labelnode, lnodes){
    for (i in lnodes){
        var n = lnodes[i]
        if(n.label == labelnode){
            var id = n.id;
            return id;
        }
    }
    return 0;
};

function edgeIncludes(from, to, ledges){
    for(var i in ledges){
        var e = ledges[i];
        if(e.from == from && e.to == to || e.from == to && e.to == from){
            return 1;
        }
    }
    return 0;
}