// GNU AGPL v3 License
// This file was written by John Nunley.

import { Editor, Node, Connection } from "@baklavajs/core";
import ValueTracker, { TrackedValue, TrackedValueType } from "./ValueTracker";
import { NODES } from "./BaklavaNodes";

export interface SerializedPipeline {
  nodes: SerializedNode[];
  links: SerializedLink[];
  output: number;
}

export interface SerializedNode {
  id: number;
  template: string;
  values: { [key: string]: any };
  metadata: any;
}

export interface SerializedLink {
  from: number;
  fromIndex: number;
  to: number;
  toIndex: number;
  id: string;
  metadata: any;
}

export default function getPipeline(editor: Editor): SerializedPipeline {
  const nodes: SerializedNode[] = [];
  const links: SerializedLink[] = [];
  let output = -1;

  editor.nodes.forEach((node) => {
    // Take the integer part of node.id to get the id of the node.
    // This is because node.id is a string of the form "node_<id>".
    const node_id = getNodeId(node);

    const result: SerializedNode = {
      id: node_id,
      template: node.type,
      values: ValueTracker.get_instance().get_value(node.id),
      metadata: {
        // @ts-ignore
        x: node.position.x,
        // @ts-ignore
        y: node.position.y,
      },
    };

    // Set output.
    if (node.type === "ImgOut") {
      output = node_id;
    }

    nodes.push(result);
  });

  editor.connections.forEach((link) => {
    const result: SerializedLink = {
      from: getNodeId(link.from.parent),
      fromIndex: link.from.index,
      to: getNodeId(link.to.parent),
      toIndex: link.to.index,
      id: link.id,
      metadata: {}, // TODO
    };

    links.push(result);
  });

  return {
    nodes,
    links,
    output,
  };
}

export function installPipeline(
  editor: Editor,
  pipeline: SerializedPipeline
): void {
  const oldNodes = Array.from(editor.nodes);
  for (const node of oldNodes) {
    editor.removeNode(node);
  }

  // Add nodes.
  for (const node of pipeline.nodes) {
    // @ts-ignore
    const newNode = editor.addNode(new NODES[node.template]())!;

    // Set node id.
    newNode.id = `node_${node.id}`;

    // Set node values.
    if ("image" in node.values) {
      ValueTracker.get_instance().set_value({
        type: TrackedValueType.SrcImage,
        image: node.values.image,
        node_id: newNode.id,
      });
    }

    // @ts-ignore
    newNode.position.x = node.metadata.x;
    // @ts-ignore
    newNode.position.y = node.metadata.y;
  }

  // Add links.
  for (const link of pipeline.links) {
    const fromNode = editor.nodes.find(
      (node) => getNodeId(node) === link.from
    )!;
    const toNode = editor.nodes.find((node) => getNodeId(node) === link.to)!;

    // Iterate over values of interfaces and look for isInput()
    let from, to;
    for (const value of fromNode.interfaces.values()) {
      if (!value.isInput && value.index === link.fromIndex) {
        from = value;
        break;
      }
    }

    for (const value of toNode.interfaces.values()) {
      if (value.isInput && value.index === link.toIndex) {
        to = value;
        break;
      }
    }

    if (from && to) {
      editor.addConnection(from, to);
    }
  }
}

function getNodeId(node: INode): number {
  return parseInt(node.id.split("_")[1]);
}

interface INode {
  id: string;
}
