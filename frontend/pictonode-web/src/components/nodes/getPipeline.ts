// GNU AGPL v3 License
// Written by John Nunley and Grace Meredith

export type SpecificData =
  | {
      type: SpecificDataType.None;
    }
  | {
      type: SpecificDataType.InputImage;
      imageId: number;
    }
  | {
      type: SpecificDataType.Output;
    };

export enum SpecificDataType {
  None = "none",
  InputImage = "input-image",
  Output = "output",
}

export type SerializedPipeline = {
  nodes: SerializedNode[];
  links: SerializedEdge[];
  output: number | null;
};

export type SerializedNode = {
  id: number;
  template: string;
  metadata: any;
  values: Record<string, any>;
};

export type SerializedEdge = {
  id: number;
  from: number;
  to: number;
  fromIndex: number;
  toIndex: number;
  metadata: any;
};

export function getPipeline(
  elements: any[],
  specificDataMap: Map<string, SpecificData>
): SerializedPipeline {
  // Construct the serialized pipeline from the nodes and edges.
  const vueFlowNodes = elements.filter((e) => !e.data.isEdge);
  const vueFlowEdges = elements.filter((e) => e.data.isEdge);

  let output = -1;
  const nodes = vueFlowNodes.map((vueFlowNode) => {
    const node = {
      id: vueFlowNode.data.realId,
      template: vueFlowNode.data.node.templateName,
      metadata: {},
      values: {} as Record<string, any>,
    };

    // Get the specific data for this item.
    const specificData = specificDataMap.get(vueFlowNode.id);
    if (specificData) {
      if (specificData.type == SpecificDataType.InputImage) {
        node.values["image"] = specificData.imageId;
      }
    }

    if (node.template == "ImgOut") {
      output = node.id;
    }

    return node;
  });

  const edges = vueFlowEdges.map((vueFlowEdge) => {
    const sourceHandle = parseInt(vueFlowEdge.sourceHandle?.split("-")[1]!);
    const targetHandle = parseInt(vueFlowEdge.targetHandle?.split("-")[1]!);

    const baseEdge = {
      id: vueFlowEdge.data.realId,
      from: parseInt(vueFlowEdge.source!),
      to: parseInt(vueFlowEdge.target!),
      fromIndex: sourceHandle,
      toIndex: targetHandle,
      metadata: {
        /* TODO: set metadata */
      },
    };

    return baseEdge;
  });

  return {
    nodes,
    links: edges,
    output,
  };
}

export function loadPipeline(
  pipeline: SerializedPipeline,
  specificDataMap: Map<string, SpecificData>,
  nodeTemplates: Record<string, any>
): any[] {
  const elements: any[] = [];

  let x = 0;
  let y = 0;

  for (const node of pipeline.nodes) {
    if (node.template === "ImgSrc" && "image" in node.values) {
      specificDataMap.set(node.id.toString(), {
        type: SpecificDataType.InputImage,
        imageId: node.values["image"],
      });
    }

    elements.push({
      id: node.id.toString(),
      type: "repr",
      data: {
        realId: node.id,
        isEdge: false,
        node: nodeTemplates[node.template]!,
      },
      position: { x, y },
    });

    x += 100;
    y += 100;
  }

  for (const edge of pipeline.links) {
    elements.push({
      id: edge.id.toString(),
      data: {
        realId: edge.id,
        isEdge: true,
      },
      source: edge.from.toString(),
      target: edge.to.toString(),
      sourceHandle: `output-${edge.fromIndex}`,
      targetHandle: `input-${edge.toIndex}`,
    });
  }

  return elements;
}
