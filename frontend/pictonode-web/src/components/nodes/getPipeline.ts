// GNU AGPL v3 License
// This file was written by John Nunley.


import { Editor, Node, Connection } from "@baklavajs/core";

export interface SerializedPipeline {
  nodes: SerializedNode[];
  links: SerializedLink[];
  output: number;
};

export interface SerializedNode {
  id: number;
  template: string;
  values: { [key: string]: any };
  metadata: any;
};

export interface SerializedLink {
  from: number;
  fromIndex: number;
  to: number;
  toIndex: number;
  id: number;
  metadata: any;
};

export default function getPipeline(
  bcNodes: ReadonlyArray<any>,
  bcConnections: ReadonlyArray<any>
): SerializedPipeline {
  const nodes: SerializedNode[] = [];
  const links: SerializedLink[] = [];
  let output = -1;

  // TODO

  return {
    nodes,
    links,
    output,
  };
}
