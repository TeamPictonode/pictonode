// GNU AGPL v3 License

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
  // Check both inputs.
  if (input.length != 2) {
    throw new Error("Composite node must have two inputs.");
  }

  const data1 = input[0].get();
  const data2 = input[1].get();

  // Convert both to images.
  const image1 = transformToImage(data1);
  const image2 = transformToImage(data2);

  // Get the minimum width and height.
  const width = Math.min(image1.width, image2.width);
  const height = Math.min(image1.height, image2.height);

  // Create a new canvas.
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;

  // Get the context.
  const ctx = canvas.getContext("2d")!;

  // Composite the images.
  ctx.drawImage(image2, 0, 0, width, height);
  ctx.drawImage(image1, 0, 0, width, height);

  // Return the new image.
  return [{ type: NodeDataType.Image, canvas }];
}

function transformToImage(data: NodeData): HTMLCanvasElement {
  switch (data.type) {
    case NodeDataType.Image:
      return data.canvas;
    case NodeDataType.Color:
      const width = 10000;
      const height = 10000;
      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d")!;
      ctx.fillStyle = data.color;
      ctx.fillRect(0, 0, width, height);
      return canvas;
    default:
      throw new Error("Unknown node data type.");
  }
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
  const ctx = canvas.getContext("2d")!;
  ctx.fillStyle = "#3344FF";
  ctx.fillRect(0, 0, 100, 100);
  return { type: NodeDataType.Image, canvas };
}

function noOutputImage(): NodeData {
  const canvas = document.createElement("canvas");
  canvas.width = 200;
  canvas.height = 100;
  const ctx = canvas.getContext("2d")!;

  // Black background.
  ctx.fillStyle = "#000000";
  ctx.fillRect(0, 0, 200, 100);

  // White text saying "no image selected".
  ctx.fillStyle = "#FFFFFF";
  ctx.font = "20px Arial";
  ctx.fillText("No image selected", 10, 50);

  return { type: NodeDataType.Image, canvas };
}
