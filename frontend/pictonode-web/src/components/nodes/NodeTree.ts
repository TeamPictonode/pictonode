// GNU AGPL v3 License

import { Node as RawNode, Pipeline as RawPipeline } from "libnode";
import NodeRepr from "./NodeRepr.vue";
import getTemplates from "./Templates";

type Rgb = `rgb(${number}, ${number}, ${number})`;
type Rgba = `rgba(${number}, ${number}, ${number}, ${number})`;
type Hex = `#${string}`;
export type Color = Rgb | Rgba | Hex;

export type NodeMetadata = {
    metatype: MetadataType.LinkTemplate;
    title: string;
    type: NodeDataType;
} | {
    metatype: MetadataType.NodeTemplate;
    name: string;
    special: SpecialNodeType;
} | {
    metatype: MetadataType.Node;
    x: number;
    y: number;
    title?: string;
};

export enum MetadataType {
    LinkTemplate,
    NodeTemplate,
    Node,
};

export enum SpecialNodeType {
    PureFunction,
    OutputNode,
    ImageInput,
    ColorInput,
};

// TODO: Add other types, for efficiency.
export type NodeData = {
    type: NodeDataType.Image;
    canvas: HTMLCanvasElement;
} | {
    type: NodeDataType.Color;
    color: Color;
} | {
    type: NodeDataType.Invalid;
}

export enum NodeDataType {
    Image = "image",
    Color = "color",
    Invalid = "invalid",
};

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

export function pipelineToVueFlow(pipeline: Pipeline): Array<any> {
    const nodes: Array<any> = [];

    // Add the nodes.
    for (const node of pipeline.getNodes()) {
        const metadata = node.getMetadata();
        if (metadata.metatype !== MetadataType.Node) {
            throw new Error("Invalid metadata type for node");
        }

        const x = metadata.x;
        const y = metadata.y;

        nodes.push({
            id: node.getId().toString(),
            type: "repr",
            data: { node },
            position: {
                x,
                y,
            },
        });
    }

    // Add the links.
    for (const link of pipeline.getLinks()) {
        const sourceId = (() => {
            const source = link.getFrom();
            if (source) {
                return source.getId().toString();
            } else {
                return "X_";
            }
        })();
        const targetId = (() => {
            const target = link.getTo();
            if (target) {
                return target.getId().toString();
            } else {
                return "X_";
            }
        })();

        nodes.push({
            id: `e${sourceId}-${targetId}`,
            source: sourceId,
            target: targetId,
            animated: true,
        });
    }

    return nodes;
}
