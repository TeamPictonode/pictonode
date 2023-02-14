// GNU AGPL v3 License

// This file in its entirety was written by John Nunley and Grace Meredith.

import { NodeTemplate, LinkTemplate, TemplateTable, Link } from "libnode";
import {
  Color,
  NodeData,
  NodeDataType,
  NodeMetadata,
  MetadataType,
  SpecialNodeType,
} from "./NodeTree";

const TEMPLATES = new TemplateTable<NodeData, NodeMetadata>();
let initialized = false;

export default function getTemplates(): TemplateTable<NodeData, NodeMetadata> {
  if (!initialized) {
    initialized = true;
    initializeTemplates();
  }
  return TEMPLATES;
}

function initializeTemplates() {
  // Final output node; used as a marker.
  const outputNode = new NodeTemplate<NodeData, NodeMetadata>(
    (_) => [],
    [new LinkTemplate(ltMeta("Viewport", NodeDataType.Image), noOutputImage())],
    [],
    ntMeta("Output", "Output", SpecialNodeType.OutputNode)
  );

  // Composite two images together.
  const compositeNode = new NodeTemplate<NodeData, NodeMetadata>(
    composite,
    [
      new LinkTemplate(ltMeta("Top Image", NodeDataType.Image), defaultImage()),
      new LinkTemplate(
        ltMeta("Bottom Image", NodeDataType.Image),
        defaultImage()
      ),
    ],
    [
      new LinkTemplate(
        ltMeta("Composite Image", NodeDataType.Image),
        defaultImage()
      ),
    ],
    ntMeta("Composite", "Composites", SpecialNodeType.PureFunction)
  );

  // Image input node.
  const inputNode = new NodeTemplate<NodeData, NodeMetadata>(
    (_) => [{ type: NodeDataType.Invalid }],
    [],
    [
      new LinkTemplate(
        ltMeta("Input Image", NodeDataType.Image),
        defaultImage()
      ),
    ],
    ntMeta("Image Input", "Input", SpecialNodeType.ImageInput)
  );

  // Color input node.
  const colorInputNode = new NodeTemplate<NodeData, NodeMetadata>(
    (_) => [{ type: NodeDataType.Invalid }],
    [],
    [
      new LinkTemplate(ltMeta("Input Color", NodeDataType.Color), {
        type: NodeDataType.Color,
        color: "#FF00FF",
      }),
    ],
    ntMeta("Color Input", "Input", SpecialNodeType.ColorInput)
  );

  // Add all of the nodes.
  TEMPLATES.addTemplate("output", outputNode);
  TEMPLATES.addTemplate("composite", compositeNode);
  TEMPLATES.addTemplate("input", inputNode);
  TEMPLATES.addTemplate("color-input", colorInputNode);
}

type Link2 = Link<NodeData, NodeMetadata>;

function composite(input: Array<Link2>): Array<NodeData> {
  throw new Error("Not implemented.");
}

function transformToImage(data: NodeData): HTMLCanvasElement {
  throw new Error("Not implemented.");
}

function ntMeta(
  name: string,
  category: string,
  special: SpecialNodeType
): NodeMetadata {
  return {
    metatype: MetadataType.NodeTemplate,
    name,
    special,
    category,
  };
}

function ltMeta(title: string, type: NodeDataType): NodeMetadata {
  return {
    metatype: MetadataType.LinkTemplate,
    title,
    type,
  };
}

function defaultImage(): NodeData {
  const canvas = document.createElement("canvas");
  canvas.width = 100;
  canvas.height = 100;
  const ctx = canvas.getContext("2d");
  if (ctx === null) {
    throw new Error("Could not get context.");
  }

  ctx.fillStyle = "#FF00FF";
  ctx.fillRect(0, 0, 100, 100);
  
  // Write "default image"
  ctx.fillStyle = "#000000";
  ctx.font = "20px Arial";
  ctx.fillText("default image", 10, 50);

  return {
    type: NodeDataType.Image,
    image: canvas,
  }
}

function noOutputImage(): NodeData {
  const canvas = document.createElement("canvas");
  canvas.width = 100;
  canvas.height = 100;
  const ctx = canvas.getContext("2d");
  if (ctx === null) {
    throw new Error("Could not get context.");
  }

  ctx.fillStyle = "#FF00FF";
  ctx.fillRect(0, 0, 100, 100);
  
  // Write "no output image"
  ctx.fillStyle = "#000000";
  ctx.font = "20px Arial";
  ctx.fillText("no output image", 10, 50);

  return {
    type: NodeDataType.Image,
    image: canvas,
  }
}
