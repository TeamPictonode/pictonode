// GNU AGPL v3 License

import { Node as RawNode, Pipeline as RawPipeline, ComputeFunctionTable } from "libnode";
import { getComputeTable } from "./ComputeFunctions";
import NodeRepr from "./NodeRepr.vue";

type Rgb = `rgb(${number}, ${number}, ${number})`;
type Rgba = `rgba(${number}, ${number}, ${number}, ${number})`;
type Hex = `#${string}`;
export type Color = Rgb | Rgba | Hex;

export type NodeMetadata = {
    x: number;
    y: number;
    title: string;
    color: Color;
};

// TODO: Add other types, for efficiency.
export type NodeData = {
    type: NodeDataType.Image;
    canvas: HTMLCanvasElement;
};

export enum NodeDataType {
    Image = "image",
};

export type Node = RawNode<NodeData, NodeMetadata>;
export type Pipeline = RawPipeline<NodeData, NodeMetadata>;

export function defaultPipeline(): Pipeline {
    const table = getComputeTable();
    const pipeline = new RawPipeline<NodeData, NodeMetadata>({
        x: 0,
        y: 0,
        title: "Pipeline",
        color: "#000000",
    });

    // Add the nodes.
    const inputNode = pipeline.addNode(new RawNode(
        [],
        [new Link()]
    )

    return pipeline;
}

export function pipelineToVueFlow(pipeline: Pipeline): Array<any> {
    const nodes: Array<any> = [];

    // Add the nodes.
    for (const node of pipeline.getNodes()) {
        nodes.push({
            id: node.getID().toString(),
            type: "node",
            data: {
                label: node.getMetadata().title,
                color: node.getMetadata().color,
                node,
            },
            position: {
                x: node.getMetadata().x,
                y: node.getMetadata().y,
            },
        });
    }

    // Add the links.
    for (const link of pipeline.getLinks()) {
        const sourceId = link.getFromNode().getID().toString();
        const targetId = link.getToNode().getID().toString();

        nodes.push({
            id: `e${sourceId}-${targetId}`,
            source: sourceId,
            target: targetId,
            animated: true,
        });
    }

    return nodes;
}
