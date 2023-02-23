<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts" setup>
import { Position, VueFlow, Connection, Edge, useVueFlow } from "@vue-flow/core";
import { Controls } from "@vue-flow/additional-components";
import { defineComponent, defineProps, defineEmits, ref } from "vue";
import NodeRepr from "./NodeRepr.vue";
import { processPipeline } from "../../api";
import { nodeTemplates, SpecificData, SpecificDataType } from "./NodeTypes";

let id = 0;

const elements = [
  _templateToNode("input", 100, 100),
  _templateToNode("output", 100, 300),
  {
    id: "1000000",
    source: "0",
    target: "1",
    sourceHandle: "output-0",
    targetHandle: "input-0",
    data: {
      realId: 1000000,
      isEdge: true,
    }
  }
];

const onConnect = (edge: any) => {
  const newId = id++;
  const newEdge = {
    ...edge,
    id: newId.toString(),
    data: {
      realId: newId,
      isEdge: true,
    }
  }
  elements.push(newEdge);
  processCanvas();
};

const emits = defineEmits<{
  (event: "canvas-update", canvas: HTMLCanvasElement): void;
}>();

// Method for adding a new node with the given template.
// This method is called by the parent Canvas component.
const addNode = (template: string) => {
  const node = _templateToNode(template, 0, 0);
  elements.push(node);
  processCanvas();
};

function _templateToNode(template: string, x: number, y: number): any {
  const nodeTemplate = nodeTemplates[template]!;
  const newId = id++;
  console.log(`making node with id ${newId}`);
  const node = {
    id: newId.toString(), 
    position: { x, y },
    type: "repr",
    data: {
      realId: newId,
      node: nodeTemplate,
      isEdge: false,
    }
  };
  return node;
};

const processCanvas = () => {
  const pipeline = _getPipeline();

  // Process the pipeline.
  processPipeline(pipeline).then(imageFile => {
    // Create an image element and set its source to the image file.
    const image = new Image();
    image.src = URL.createObjectURL(imageFile);

    // Create a canvas element and draw the image on it.
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");

    if (!context) {
      throw new Error("Could not get canvas context");
    }

    image.onload = () => {
      canvas.width = image.width;
      canvas.height = image.height;
      context.drawImage(image, 0, 0);
      emits("canvas-update", canvas);
    };
  })
};

const specificDataMap = new Map<string, SpecificData>();

const nodeNeedsReprocess = (id: string, data: SpecificData) => {
  specificDataMap.set(id, data);
  processCanvas();
};

type SerializedPipeline = {
  nodes: SerializedNode[];
  edges: SerializedEdge[];
  output: number | null;
};

type SerializedNode = {
  id: number;
  template: string;
  metadata: any;
};

type SerializedEdge = {
  id: number;
  from: number;
  to: number;
  fromIndex: number;
  toIndex: number;
  defaultValue: any;
  metadata: any;
}

function _getPipeline(): SerializedPipeline {
  // Construct the serialized pipeline from the nodes and edges.
  const vueFlowNodes = elements.filter(e => !e.data.isEdge); 
  const vueFlowEdges = elements.filter(e => e.data.isEdge);

  const nodes = vueFlowNodes.map(vueFlowNode => ({
    id: vueFlowNode.data.realId,
    template: vueFlowNode.data.node.template,
    metadata: {}
  }));

  let output = -1;
  const edges = vueFlowEdges.map(vueFlowEdge => {
    const sourceHandle = parseInt(vueFlowEdge.sourceHandle?.split("-")[1]!);
    const targetHandle = parseInt(vueFlowEdge.targetHandle?.split("-")[1]!);

    const baseEdge = {
      id: vueFlowEdge.data.realId,
      from: parseInt(vueFlowEdge.source!),
      to: parseInt(vueFlowEdge.target!),
      fromIndex: sourceHandle,
      toIndex: targetHandle,
      defaultValue: undefined as any,
      metadata: {/* TODO: set metadata */}
    };
    
    // TODO: set DefaultValue in all possible cases
    // Get the specific data for this item.
    const specificData = specificDataMap.get(vueFlowEdge.source!);
    if (specificData) {
      if (specificData.type == SpecificDataType.InputImage) {
        baseEdge.defaultValue = specificData.imageId;
      }
    }

    return baseEdge;
  });

  return {
    nodes,
    edges,
    output
  };
}
</script>

<template>
  <div style="height: 50%;">
    <VueFlow id="nodeContainer" v-model="elements">
      <Controls />
      <template #node-repr="props">
        <NodeRepr v-bind="props" @needs-reprocess="
          // @ts-ignore
          data => nodeNeedsReprocess(props.id, data)
        " />
      </template>
    </VueFlow>
  </div>
</template>

<style scoped>
.vue-flow {
  border: 1px solid black;
  background-color: #03303f;
}
</style>
