<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { Position, VueFlow, Connection, Edge, addEdge } from "@vue-flow/core";
import { Controls } from "@vue-flow/additional-components";
import { defineComponent } from "vue";
import NodeRepr from "./NodeRepr.vue";
import {
  defaultPipeline,
  pipelineToVueFlow,
  SpecialNodeType,
  MetadataType,
  NodeDataType,
  nodeToViewFlow,
} from "./NodeTree";
import getTemplates from "./Templates";

const pipeline = defaultPipeline();
const elements = pipelineToVueFlow(pipeline);

console.log(elements);

export default defineComponent({
  components: { NodeRepr, VueFlow, Controls },
  props: {
    pendingTemplates: {
      type: Array as () => string[],
      required: true,
    },
  },

  watch: {
    pendingTemplates: {
      handler: function (newVal, oldVal) {
        console.log("pendingTemplates changed", newVal, oldVal);
        if (newVal.length > oldVal.length) {
          const templateName = newVal[newVal.length - 1];
          this.addNode(templateName);
        }
      },
      deep: true,
    },
  },

  data: () => ({
    elements,
    pipeline,
  }),

  emits: ["canvas-update", "updateNodeInternals"],

  methods: {
    // Add a new node to the graph.
    addNode(templateName: string) {
      // Get the title of the node template.
      const template = getTemplates().getTemplate(templateName);
      const metadata = template.getMetadata();

      if (metadata.metatype !== MetadataType.NodeTemplate) {
        throw new Error("Template is not a node template");
      }

      const title = metadata.name;

      const newNode = this.pipeline.createNode(templateName, {
        metatype: MetadataType.Node,
        x: 0,
        y: 0,
        title,
      });

      // Add a new node to the graph.
      this.elements.push(nodeToViewFlow(newNode));
      this.reprocess();
    },

    processCanvas() {
      console.log(this.pipeline);
      // Get the "output" node for the pipeline.
      let outputNode;

      for (const node of this.pipeline.getNodes()) {
        const template = node.getTemplate();

        if (template === "output") {
          outputNode = node;
          break;
        }
      }

      let canvas;
      if (!outputNode) {
        // Draw a canvas with the text "no output node".
        canvas = document.createElement("canvas");
        canvas.width = 200;
        canvas.height = 100;
        const ctx = canvas.getContext("2d");

        if (!ctx) {
          throw new Error("Could not get 2d context");
        }

        // Blue background.
        ctx.fillStyle = "#00FF00";
        ctx.fillRect(0, 0, 200, 100);

        // White text.
        ctx.fillStyle = "#FFFFFF";
        ctx.font = "30px Arial";
        ctx.fillText("No output node", 10, 50);
      } else {
        // Get the first input link and get the canvas from it.
        const inputLink = outputNode.getInputs()[0];
        const data = inputLink.get();
        if (data.type !== NodeDataType.Image) {
          throw new Error("Output node does not have an image input");
        }
        canvas = data.canvas;
      }

      this.$emit("canvas-update", canvas);
    },

    onConnect(connection: Connection | Edge) {
      //this.elements = addEdge(connection, this.elements);

      // Get the source and target nodes.
      const sourceId = parseInt(connection.source);
      const sourceNode = this.pipeline.getNode(sourceId);
      const sourceHandle = connection.sourceHandle!;
      const targetId = parseInt(connection.target);
      const targetNode = this.pipeline.getNode(targetId);
      const targetHandle = connection.targetHandle!;

      if (!sourceNode || !targetNode) {
        throw new Error("Could not get source or target node");
      }

      // Determine the values; source should have "output-" at the front, and
      // target should have "input-" at the front.
      const sourceValue = parseInt(sourceHandle.substring(7));
      const targetValue = parseInt(targetHandle.substring(6));

      console.log(
        `Linking ${sourceId} ${sourceValue} to ${targetId} ${targetValue}`
      );

      // If the target node already has an input link, unlink it.
      if (targetNode.isInputOccupied(targetValue)) {
        // Get the node that is currently linked to the target node.
        const oldSourceNode = targetNode.getInputs()[targetValue].getFrom();

        if (oldSourceNode) {
          console.log(oldSourceNode);
          const oldSourceId = oldSourceNode.getId();
          const oldSourceValue = oldSourceNode
            .getOutputs()
            .indexOf(targetNode.getInputs()[targetValue]);

          this.pipeline.unlink(
            oldSourceId,
            oldSourceValue,
            targetId,
            targetValue 
          );
        }
      }

      // Link the nodes.
      this.pipeline.link(sourceId, sourceValue, targetId, targetValue, {
        metatype: MetadataType.Link
      });

      // Update the graph.
      this.reprocess();
    },

    reprocess() {
      // @ts-ignore
      this.elements = pipelineToVueFlow(this.pipeline);
      this.processCanvas();
    },
  },

  mounted() {
    this.processCanvas();
  },
});
</script>

<template>
  <VueFlow id="nodeContainer" v-model="elements" @connect="onConnect">
    <Controls />
    <template #node-repr="props">
      <NodeRepr v-bind="props" @needs-reprocess="processCanvas" />
    </template>
  </VueFlow>
</template>

<style scoped>
.vue-flow {
  border: 1px solid black;
  background-color: gray;
}
</style>
