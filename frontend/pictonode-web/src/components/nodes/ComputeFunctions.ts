// GNU AGPL v3 License

import { ComputeFunctionTable, Link } from "libnode";
import { NodeMetadata, NodeData, NodeDataType, NodeDataType } from "./NodeTree";

export function getComputeTable(): ComputeFunctionTable<NodeData, NodeMetadata> {
    let computeTable = new ComputeFunctionTable<NodeData, NodeMetadata>();

    // Output the input image.
    computeTable.add("output", outputNode);
    // Input the input image.
    computeTable.add("input", inputNode);
    // Composite two images.
    computeTable.add("composite", composite);
    // Create a solid color image.
    computeTable.add("solidColor", solidColor);

    return computeTable;
}

type Link2 = Link<NodeData, NodeMetadata>;

function outputNode(inputs: Array<Link2>): Array<NodeData> {
    // Marker node.
    return [];
}

function inputNode(inputs: Array<Link2>): Array<NodeData> {
    // Marker node.
    return [];
}

function composite(inputs: Array<Link2>): Array<NodeData> {
    // Check both inputs.
    if (inputs.length != 2) {
        throw new Error("Composite node must have two inputs.");
    }

    const data1 = inputs[0].get();
    const data2 = inputs[1].get();

    // Check that both inputs are images.
    if (data1.type != NodeDataType.Image || data2.type != NodeDataType.Image) {
        throw new Error("Composite node must have two image inputs.");
    }

    // Get the minimum width and height.
    const width = Math.min(data1.canvas.width, data2.canvas.width);
    const height = Math.min(data1.canvas.height, data2.canvas.height);

    // Create a new canvas.
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;

    // Get the context.
    const ctx = canvas.getContext("2d")!;

    // Composite the images.
    ctx.drawImage(data1.canvas, 0, 0, width, height);
    ctx.drawImage(data2.canvas, 0, 0, width, height);

    // Return the new image.
    return [{ type: NodeDataType.Image, canvas }];
}

function solidColor(inputs: Array<Link2>): Array<NodeData> {
    const canvas = document.createElement("canvas");
    canvas.width = 100;
    canvas.height = 100;

    const ctx = canvas.getContext("2d")!;
    ctx.fillStyle = "red";
    ctx.fillRect(0, 0, 100, 100);

    return [{ type: NodeDataType.Image, canvas }];
}

