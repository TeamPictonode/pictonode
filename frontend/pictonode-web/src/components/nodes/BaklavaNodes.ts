import { NodeBuilder } from "@baklavajs/core";
import { SelectOption } from "@baklavajs/plugin-options-vue3";
import { WatchIgnorePlugin } from "webpack";

import {
  getImgID,
  imgNodes,
  nodeIds,
  nodeList,
  addLinkToPipeline,
  addNodeToPipeline,
  finalProcess,
} from "./CalculateNodes";

let id = 0;

export const ImageNode = new NodeBuilder("ImgSrc")
  .setName("Input Image")
  .addOption("Upload image", "UploadOption")
  .addOutputInterface("Result", { index: 0 })
  .onCalculate((n) => {
    var imgID: number = nodeList.includes(n.id)
      ? imgNodes[n.id]
      : getImgID(n.id);
    if (!nodeList.includes(n.id)) {
      nodeList.push(n.id);
      nodeIds[n.id] = id;
      id++;
    }
    n.getInterface("Result").value = <JSON>(<unknown>{
      nodes: [addNodeToPipeline(nodeIds[n.id], "ImgSrc", { image: imgID })],
      links: [{}],
    });
  })
  .build();

export const RenderedNode = new NodeBuilder("ImgOut")
  .setName("Rendered Image")
  .addInputInterface("Image", undefined, undefined, { index: 0 })
  .onCalculate((n) => {
    let pipeline = n.getInterface("Image").value;
    if (pipeline) {
      if (!nodeList.includes(n.id)) {
        nodeList.push(n.id);
        nodeIds[n.id] = id;
        id++;
      }
      pipeline.nodes.push(addNodeToPipeline(nodeIds[n.id], "ImgOut", {}));
      pipeline.links.push(
        addLinkToPipeline(
          id,
          pipeline.nodes[pipeline.nodes.length - 2].id,
          nodeIds[n.id],
          0,
          0
        )
      );
      id++;
      pipeline.output = nodeIds[n.id];
      finalProcess(pipeline);
    }
  })
  .build();

export const InvertNode = new NodeBuilder("Invert")
  .setName("Invert")
  .addInputInterface("Image", undefined, undefined, { index: 0 })
  .addOutputInterface("Result", { index: 0 })
  .onCalculate((n) => {
    let pipeline = n.getInterface("Image").value;
    if (pipeline) {
      if (!nodeList.includes(n.id)) {
        nodeList.push(n.id);
        nodeIds[n.id] = id;
        id++;
      }
      pipeline.nodes.push(addNodeToPipeline(nodeIds[n.id], "Invert", {}));
      pipeline.links.push(
        addLinkToPipeline(
          id,
          pipeline.nodes[pipeline.nodes.length - 2].id,
          nodeIds[n.id],
          0,
          0
        )
      );
      id++;
      n.getInterface("Result").value = pipeline;
    }
  })
  .build();

export const CompositeNode = new NodeBuilder("CompOver")
  .setName("Composite")
  .addInputInterface("Top Image", undefined, undefined, { index: 0 })
  .addInputInterface("Bottom Image", undefined, undefined, { index: 1 })
  .addOutputInterface("Result", { index: 0 })
  .onCalculate((n) => {
    if (
      n.getInterface("Top Image").value &&
      n.getInterface("Bottom Image").value
    ) {
      let pipeline = n.getInterface("Top Image").value;
      let pipeline2 = n.getInterface("Bottom Image").value;
      var linkFrom1 = pipeline.nodes[pipeline.nodes.length - 1];
      var linkFrom2 = pipeline2.nodes[pipeline2.nodes.length - 1];
      if (!nodeList.includes(n.id)) {
        nodeList.push(n.id);
        nodeIds[n.id] = id;
        id++;
      }

      for (var nodes of pipeline2.nodes) {
        pipeline.nodes.push(nodes);
      }

      for (var link of pipeline2.links) {
        pipeline.links.push(link);
      }

      pipeline.nodes.push(addNodeToPipeline(nodeIds[n.id], "CompOver", {}));
      pipeline.links.push(
        addLinkToPipeline(id, linkFrom1, nodeIds[n.id], 0, 0)
      );
      id++;
      pipeline.links.push(addLinkToPipeline(id, linkFrom2, nodeIds[id], 0, 1));
      id++;

      n.getInterface("Result").value = pipeline;
    }
  })
  .build();

export const BriCon = new NodeBuilder("BrightCont")
  .setName("Brightness/Contrast")
  .addInputInterface("Image", undefined, undefined, { index: 0 })
  .addOption("Brightness", "NumberOption", 0)
  .addOption("Contrast", "NumberOption", 0)
  .addOutputInterface("Result", { index: 0 })
  .onCalculate((n) => {
    //set hard limits to option values -3 <= brightness <= 3 & -5 <= contrast <= 5
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
      if (!nodeList.includes(n.id)) {
        nodeList.push(n.id);
        nodeIds[n.id] = id;
        id++;
      }
      pipeline.nodes.push(
        addNodeToPipeline(nodeIds[n.id], "BrightCont", {
          brightness: n.getOptionValue("Brightness"),
          contrast: n.getOptionValue("Contrast"),
        })
      );
      pipeline.links.push(
        addLinkToPipeline(
          id,
          pipeline.nodes[pipeline.nodes.length - 2].id,
          nodeIds[n.id],
          0,
          0
        )
      );
      id++;

      n.getInterface("Result").value = pipeline;
    }
  })
  .build();

export const GaussBlur = new NodeBuilder("GaussBlur")
  .setName("Gauss Blur")
  .addInputInterface("Image", undefined, undefined, { index: 0 })
  .addOption("X", "NumberOption", 0)
  .addOption("Y", "NumberOption", 0)
  .addOutputInterface("Result", { index: 0 })
  .onCalculate((n) => {
    let pipeline = n.getInterface("Image").value;
    if (pipeline) {
      if (!nodeList.includes(n.id)) {
        nodeList.push(n.id);
        nodeIds[n.id] = id;
        id++;
      }
      pipeline.nodes.push(
        addNodeToPipeline(nodeIds[n.id], "GaussBlur", {
          std_dev_x: n.getOptionValue("X"),
          std_dev_y: n.getOptionValue("Y"),
        })
      );
      pipeline.links.push(
        addLinkToPipeline(
          id,
          pipeline.nodes[pipeline.nodes.length - 2].id,
          nodeIds[n.id],
          0,
          0
        )
      );
      id++;

      n.getInterface("Result").value = pipeline;
    }
  })
  .build();
