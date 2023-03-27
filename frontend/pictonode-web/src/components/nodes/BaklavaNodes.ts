import { NodeBuilder } from "@baklavajs/core";
import {
    processPipeline
  } from "../../api"

export const MathNode = new NodeBuilder("MathNode")
    .setName("Math Node")
    .addInputInterface("Number 1", "NumberOption", 1)
    .addInputInterface("Number 2", "NumberOption", 10)
    .addOption("Operation", "SelectOption", "Add", undefined, { items: ["Add", "Subtract"] })
    .addOutputInterface("Result")
    .onCalculate(n => {
        let value1 = n.getInterface("Number 1").value;
        let value2 = n.getInterface("Number 2").value;
        let operation = n.getOptionValue("Operation");
        let result
        if (operation === "Add") {
          result = value1 + value2;
      } else if (operation === "Subtract") {
          result = value1 - value2;
      }
        n.getInterface("Result").value = result;
    })
    .build();

export const DisplayNode = new NodeBuilder("DisplayNode")
    .setName("Display")
    .addInputInterface("Value")
    .addOption("ValueText", "TextOption")
    .addOption("Test", "InputOption")
    .onCalculate(n => {
        let value = n.getInterface("Value").value;
        if (typeof value === "number") {
            value = value.toFixed(3);
        }
        n.setOptionValue("ValueText", value);
    })
    .build();

export const ImageNode = new NodeBuilder("InputImage")
    .setName("Input Image")
    .addOption("Upload image", "ButtonOption")
    .addOutputInterface("Result")
    .onCalculate(n => {
        console.log("INPUT CALCULATE")
        let pipeline: JSON = <JSON>(<unknown> {
            nodes: [
                {
                    id: ID,
                    template: 'ImgSrc',
                    metadata: {},
                    values: {
                        image: srcImgIds[srcImgIds.length-1]
                    }
                }
            ],
            links: [],      
        });
        ID++;
        n.getInterface("Result").value = pipeline
    })
    .build();

export const RenderedNode = new NodeBuilder("RenderedImage")
    .setName("Rendered Image")
    .addInputInterface("Image")
    .onCalculate (n => {
        console.log("OUTPUT CALCULATE")
        let pipeline = n.getInterface("Image").value
        if(pipeline) {
            let node = {
                id: ID,
                template: "ImgOut",
                metadata: {},
                values: {}
            }
            ID++
            let link = {
                id: ID,
                from: pipeline.nodes[pipeline.nodes.length-1].id,
                to: node.id,
                fromIndex: 0,
                toIndex: 0,
                metadata: {}
            }
            ID++
            pipeline.nodes.push(node)
            pipeline.links.push(link)
            pipeline.output = node.id

            processPipeline(pipeline).then((imageFile) => {
                // Create an image element and set its source to the image file.
                const image = new Image();
                image.src = URL.createObjectURL(imageFile);
        
                // Create a canvas element and draw the image on it.
                const canvas = <HTMLCanvasElement> document.getElementById("imgview");
                if(canvas){
                    const context = canvas.getContext("2d");
        
                    if (!context) {
                        throw new Error("Could not get canvas context");
                    }

                    context.clearRect(0, 0, canvas.width, canvas.height)
        
                    image.onload = () => {
                    canvas.width = image.width;
                    canvas.height = image.height;
                    context.drawImage(image, 0, 0);
                    };
                }
            });
        }
    })
    .build();

    export const InvertNode = new NodeBuilder("Invert Node")
        .setName("Invert")
        .addInputInterface("Image")
        .addOutputInterface("Result")
        .onCalculate (n => {
            let pipeline = n.getInterface("Image").value
            if(pipeline) {
                let node = {
                    id: ID,
                    template: "Invert",
                    metadata: {},
                    values: {}
                }

                let link = {
                    id: ID,
                    from: pipeline.nodes[pipeline.nodes.length-1].id,
                    to: node.id,
                    fromIndex: 0,
                    toIndex: 0,
                    metadata: {}
                }

                ID++
                pipeline.nodes.push(node)
                pipeline.links.push(link)
                n.getInterface("Result").value = pipeline
            }
        })
        .build();
    
    export const CompositeNode = new NodeBuilder("Composite Node")
        .setName("Composite")
        .addInputInterface("Top Image")
        .addInputInterface("Bottom Image")
        .addOutputInterface("Result")
        .onCalculate (n => {
            if(n.getInterface("Top Image").value && n.getInterface("Bottom Image").value) {
                let pipeline = n.getInterface("Top Image").value
                let pipeline2 = n.getInterface("Bottom Image").value


                let node = {
                    id: ID,
                    template: "CompOver",
                    metadata: {},
                    values: {}
                }

                let link1 = {
                    id: ID,
                    from: pipeline.nodes[pipeline.nodes.length-1].id,
                    to: node.id,
                    fromIndex: 0,
                    toIndex: 0,
                    metadata: {}
                }

                let link2 = {
                    id: ID,
                    from: pipeline2.nodes[pipeline2.nodes.length-1].id,
                    to: node.id,
                    fromIndex: 0,
                    toIndex: 0,
                    metadata: {}
                }

                ID++
                
                for( var nodes of pipeline2.nodes ) {
                    pipeline.nodes.push(nodes)
                }

                for (var link of pipeline2.links) {
                    pipeline.links.push(link)
                }

                pipeline.nodes.push(node)
                pipeline.links.push(link1)
                pipeline.links.push(link2)

                n.getInterface("Result").value = pipeline
            }
        })
        .build();

    export let srcImgIds = new Array()
    let ID = 0
    