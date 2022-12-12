<!-- GNU AGPL v3 License -->

<script lang="ts">
import { Handle, Position, NodeEventsOn, NodeDragEvent } from "@vue-flow/core";
import { defineComponent } from "vue";

import {
  Node as GraphNode,
  metadataTitle,
  MetadataType,
} from "../nodes/NodeTree";
import InnerSwitch from "./InnerSwitch.vue";

export default defineComponent({
  components: { Handle, InnerSwitch },
  data: () => ({
    Position,
    metadataTitle,

    dragStart: {
      x: 0,
      y: 0,
    },

    inputHandleStyle(index: number) {
      return {
        top: `${index * 20 + 10}px`,
      };
    },

    outputHandleStyle(index: number) {
      return {
        top: `${index * 20 + 10}px`,
      };
    },
  }),
  emits: ["needs-reprocess", "updateNodeInternals"],
  props: {
    data: {
      type: Object as () => { node: GraphNode },
      required: true,
    },

    events: {
      type: Object as () => {
        dragStart: NodeEventsOn["dragStart"];
        dragStop: NodeEventsOn["dragStop"];
      },
      required: true,
    },
  },
  methods: {
    onNeedsReprocess() {
      console.log("needs reprocess");
      this.$emit("needs-reprocess");
    },

    onDragStart(event: NodeDragEvent) {
      this.dragStart.x = event.event.pageX;
      this.dragStart.y = event.event.pageY;
    },

    onDragStop(event: NodeDragEvent) {
      const metadata = this.data.node.getMetadata();

      if (metadata.metatype !== MetadataType.Node) {
        throw new Error("Node is not a node");
      }

      const offsetX = event.event.pageX - this.dragStart.x;
      const offsetY = event.event.pageY - this.dragStart.y;

      console.log(`offsets: ${offsetX}, ${offsetY}`);

      metadata.x += offsetX;
      metadata.y += offsetY;

      this.data.node.setMetadata(metadata);
      this.onNeedsReprocess();
    },
  },
  mounted() {
    this.events.dragStart(this.onDragStart);
    this.events.dragStop(this.onDragStop);
  },
});
</script>

<template>
  <Handle
    v-for="(inputLink, index) in data.node.getInputs()"
    type="target"
    :id="`input-${index}`"
    :position="Position.Left"
    :style="inputHandleStyle(index)"
  >
  </Handle>

  <div class="nodeStyle">
    <p>{{ metadataTitle(data.node.getMetadata()) || `Unnamed Node` }}</p>
    <InnerSwitch :node="data.node" @input-update="onNeedsReprocess" />
  </div>

  <Handle
    v-for="(outputLink, index) in data.node.getOutputs()"
    type="source"
    :id="`output-${index}`"
    :position="Position.Right"
    :style="outputHandleStyle(index)"
  >
    {{ metadataTitle(outputLink.getMetadata()) || `Output ${index}` }}
    <div v-if="!outputLink.getFrom()">
      {{ metadataTitle(outputLink.getMetadata()) }}
    </div>
  </Handle>
</template>

<style lang="scss">
.nodeStyle {
  border-radius: 5px;
  color: #fff;
  background-color: #555;
  padding: 10px;
  text-align: center;
  border: 1px solid #333;
}
</style>
