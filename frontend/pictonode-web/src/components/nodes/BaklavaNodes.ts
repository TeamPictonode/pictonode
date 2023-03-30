import { NodeBuilder } from "@baklavajs/core";
import { SelectOption } from "@baklavajs/plugin-options-vue3";
import { WatchIgnorePlugin } from "webpack";

import { processPipeline } from "../../api";

export const ImageNode = new NodeBuilder("InputImage")
  .setName("Input Image")
  .addOption("Upload image", "ButtonOption")
  .addOutputInterface("Result")
  .onCalculate((n) => {
    n.getInterface("Result").value = getInitialPipeline();
  })
  .build();

export const RenderedNode = new NodeBuilder("RenderedImage")
  .setName("Rendered Image")
  .addInputInterface("Image")
  .onCalculate((n) => {
    //resetList()
    let pipeline = n.getInterface("Image").value;
    finalProcess(pipeline);
  })
  .build();

export const InvertNode = new NodeBuilder("Invert Node")
  .setName("Invert")
  .addInputInterface("Image")
  .addOutputInterface("Result")
  .onCalculate((n) => {
    let pipeline = n.getInterface("Image").value;
    if (pipeline) {
      let node = {
        id: ID,
        template: "Invert",
        metadata: {},
        values: {},
      };

      let link = {
        id: ID,
        from: pipeline.nodes[pipeline.nodes.length - 1].id,
        to: node.id,
        fromIndex: 0,
        toIndex: 0,
        metadata: {},
      };

      ID++;
      pipeline.nodes.push(node);
      pipeline.links.push(link);
      n.getInterface("Result").value = pipeline;
    }
  })
  .build();

export const CompositeNode = new NodeBuilder("Composite Node")
  .setName("Composite")
  .addInputInterface("Top Image")
  .addInputInterface("Bottom Image")
  .addOutputInterface("Result")
  .onCalculate((n) => {
    if (
      n.getInterface("Top Image").value &&
      n.getInterface("Bottom Image").value
    ) {
      let pipeline = n.getInterface("Top Image").value;
      let pipeline2 = n.getInterface("Bottom Image").value;

      let node = {
        id: ID,
        template: "CompOver",
        metadata: {},
        values: {},
      };

      let link1 = {
        id: ID,
        from: pipeline.nodes[pipeline.nodes.length - 1].id,
        to: node.id,
        fromIndex: 0,
        toIndex: 0,
        metadata: {},
      };

      let link2 = {
        id: ID,
        from: pipeline2.nodes[pipeline2.nodes.length - 1].id,
        to: node.id,
        fromIndex: 0,
        toIndex: 1,
        metadata: {},
      };

      ID++;

      for (var nodes of pipeline2.nodes) {
        pipeline.nodes.push(nodes);
      }

      for (var link of pipeline2.links) {
        pipeline.links.push(link);
      }

      pipeline.nodes.push(node);
      pipeline.links.push(link1);
      pipeline.links.push(link2);

      n.getInterface("Result").value = pipeline;
    }
  })
  .build();

export const BriCon = new NodeBuilder("Brightness Contrast")
  .setName("Brightness/Contrast")
  .addInputInterface("Image")
  .addOption("Brightness", "NumberOption", 0)
  .addOption("Contrast", "NumberOption", 0)
  .addOutputInterface("Result")
  .onCalculate((n) => {
    if (n.getOptionValue("Brightness") < -3) {
      n.setOptionValue("Brightness", -3);
    }
    if (n.getOptionValue("Brightness") > 3) {
      n.setOptionValue("Brightness", 3);
    }
    if (n.getOptionValue("Contrast") < -5) {
      n.setOptionValue("Contrast", -5);
    }
    if (n.getOptionValue("Contrast") > 5) {
      n.setOptionValue("Contrast", 5);
    }

    let pipeline = n.getInterface("Image").value;
    if (pipeline) {
      let node = {
        id: ID,
        template: "BrightCont",
        metadata: {},
        values: {
          brightness: n.getOptionValue("Brightness"),
          contrast: n.getOptionValue("Contrast"),
        },
      };

      let link = {
        id: ID,
        from: pipeline.nodes[pipeline.nodes.length - 1].id,
        to: node.id,
        fromIndex: 0,
        toIndex: 0,
        metadata: {},
      };

      ID++;
      pipeline.nodes.push(node);
      pipeline.links.push(link);
      n.getInterface("Result").value = pipeline;
    }
  })
  .build();

export const GaussBlur = new NodeBuilder("Gauss Blur")
  .setName("Gauss Blur")
  .addInputInterface("Image")
  .addOption("X", "NumberOption", 0)
  .addOption("Y", "NumberOption", 0)
  .addOutputInterface("Result")
  .onCalculate((n) => {
    let pipeline = n.getInterface("Image").value;
    if (pipeline) {
      let node = {
        id: ID,
        template: "BrightCont",
        metadata: {},
        values: {
          std_dev_x: n.getOptionValue("X"),
          std_dev_y: n.getOptionValue("Y"),
        },
      };

      let link = {
        id: ID,
        from: pipeline.nodes[pipeline.nodes.length - 1].id,
        to: node.id,
        fromIndex: 0,
        toIndex: 0,
        metadata: {},
      };

      ID++;
      pipeline.nodes.push(node);
      pipeline.links.push(link);
      n.getInterface("Result").value = pipeline;
    }
  })
  .build();

///extra calculations will prob move this to it's own file once I finalize the logic

export let srcImgs = new Array();
export type Img = {
  id: number;
  used: boolean;
};
let ID = 0;

function getImgID() {
  console.log(srcImgs);
  //for (var i in srcImgs) {
  //  if(srcImgs[i].used == false) {
  //    srcImgs[i].used = true
  //  return srcImgs[i].id;
  // }
  //}

  return srcImgs[srcImgs.length - 1].id;
}

function resetList() {
  for (var i in srcImgs) {
    srcImgs[i].used == false;
  }
}

function getInitialPipeline() {
  console.log("INPUT CALCULATE");
  let imgID = getImgID();
  const pipeline: JSON = <JSON>(<unknown>{
    nodes: [
      {
        id: ID,
        template: "ImgSrc",
        metadata: {},
        values: {
          image: imgID,
        },
      },
    ],
    links: [],
  });
  ID++;
  return pipeline;
}

async function finalProcess(pipeline: any) {
  console.log("OUTPUT CALCULATE");
  console.log(pipeline);
  if (pipeline) {
    console.log("got a pipeline");
    let node = {
      id: ID,
      template: "ImgOut",
      metadata: {},
      values: {},
    };
    ID++;
    let link = {
      id: ID,
      from: pipeline.nodes[pipeline.nodes.length - 1].id,
      to: node.id,
      fromIndex: 0,
      toIndex: 0,
      metadata: {},
    };
    ID++;
    pipeline.nodes.push(node);
    pipeline.links.push(link);
    pipeline.output = node.id;

    processPipeline(pipeline).then((imageFile) => {
      // Create an image element and set its source to the image file.
      const image = new Image();
      image.src = URL.createObjectURL(imageFile);

      // Create a canvas element and draw the image on it.
      const canvas = <HTMLCanvasElement>document.getElementById("imgview");
      if (canvas) {
        const context = canvas.getContext("2d");

        if (!context) {
          throw new Error("Could not get canvas context");
        }

        context.clearRect(0, 0, canvas.width, canvas.height);

        image.onload = () => {
          canvas.width = image.width;
          canvas.height = image.height;
          context.drawImage(image, 0, 0);
        };
      }
    });
  }
}
