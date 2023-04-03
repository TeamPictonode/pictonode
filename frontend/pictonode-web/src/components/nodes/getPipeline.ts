// GNU AGPL v3 License
// This file was written by John Nunley.

import { Editor, Node, Connection } from "@baklavajs/core";
import ValueTracker from "./ValueTracker";

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

export default function getPipeline(
  editor: Editor,
  values: ValueTracker
): SerializedPipeline {
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
      values: values.get_value(node.id),
      metadata: {}, // TODO
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
      metadata: {},
    };

    links.push(result);
  });

  return {
    nodes,
    links,
    output,
  };
}

function getNodeId(node: INode): number {
  return parseInt(node.id.split("_")[1]);
}

interface INode {
  id: string;
}
