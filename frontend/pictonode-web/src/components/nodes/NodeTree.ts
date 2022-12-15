// GNU AGPL v3 License

// This file in its entirety was written by John Nunley and Grace Meredith.

import { Node as RawNode, Pipeline as RawPipeline } from "libnode";
import NodeRepr from "./NodeRepr.vue";
import getTemplates from "./Templates";

type Rgb = `rgb(${number}, ${number}, ${number})`;
type Rgba = `rgba(${number}, ${number}, ${number}, ${number})`;
type Hex = `#${string}`;
export type Color = Rgb | Rgba | Hex;

export type NodeMetadata =
  | {
      metatype: MetadataType.LinkTemplate;
      title: string;
      type: NodeDataType;
    }
  | {
      metatype: MetadataType.NodeTemplate;
      name: string;
      category: string;
      special: SpecialNodeType;
    }
  | {
      metatype: MetadataType.Node;
      x: number;
      y: number;
      title?: string;
    };

export enum MetadataType {
  LinkTemplate,
  NodeTemplate,
  Node,
}

export enum SpecialNodeType {
  PureFunction,
  OutputNode,
  ImageInput,
  ColorInput,
}

// TODO: Add other types, for efficiency.
export type NodeData =
  | {
      type: NodeDataType.Image;
      canvas: HTMLCanvasElement;
    }
  | {
      type: NodeDataType.Color;
      color: Color;
    }
  | {
      type: NodeDataType.Invalid;
    };

export enum NodeDataType {
  Image = "image",
  Color = "color",
  Invalid = "invalid",
}

export function metadataTitle(metadata: NodeMetadata): string {
  switch (metadata.metatype) {
    case MetadataType.LinkTemplate:
      return metadata.title;
    case MetadataType.NodeTemplate:
      return metadata.name;
    case MetadataType.Node:
      return metadata.title ?? "UNKNOWN NODE";
  }
}

export type Node = RawNode<NodeData, NodeMetadata>;
export type Pipeline = RawPipeline<NodeData, NodeMetadata>;

export function defaultPipeline(): Pipeline {
  const table = getTemplates();
  const pipeline = new RawPipeline<NodeData, NodeMetadata>(table);

  // Add a basic in/out node.
  const input = pipeline.createNode("input", {
    metatype: MetadataType.Node,
    x: 200,
    y: 200,
    title: "Image Input",
  });
  const output = pipeline.createNode("output", {
    metatype: MetadataType.Node,
    x: 800,
    y: 200,
    title: "Image Output",
  });
  pipeline.link(input.getId(), 0, output.getId(), 0);

  return pipeline;
}

export function nodeToViewFlow(node: Node): any {
  const metadata = node.getMetadata();
  if (metadata.metatype !== MetadataType.Node) {
    throw new Error("Invalid metadata type for node");
  }

  const x = metadata.x;
  const y = metadata.y;

  return {
    id: node.getId().toString(),
    type: "repr",
    data: { node },
    position: {
      x,
      y,
    },
  };
}

export function pipelineToVueFlow(pipeline: Pipeline): Array<any> {
  const nodes: Array<any> = [];

  // Add the nodes.
  for (const node of pipeline.getNodes()) {
    nodes.push(nodeToViewFlow(node));
  }

  // Add the links.
  for (const link of pipeline.getLinks()) {
    const [sourceId, sourceHandle] = (() => {
      const source = link.getFrom();
      if (source) {
        return [source.getId().toString(), link.getFromIndex()];
      } else {
        return ["X_", -1];
      }
    })();
    const [targetId, targetHandle] = (() => {
      const target = link.getTo();
      if (target) {
        return [target.getId().toString(), link.getToIndex()];
      } else {
        return ["X_", -1];
      }
    })();

    nodes.push({
      id: `e${sourceId}-${targetId}`,
      source: sourceId,
      target: targetId,
      sourceHandle: `output-${sourceHandle}`,
      targetHandle: `input-${targetHandle}`,
      animated: true,
    });
  }

  return nodes;
}
