<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { Handle, Position } from "@vue-flow/core";
import { defineComponent } from "vue";

import { NodeTemplate } from "./NodeTypes";

export default defineComponent({
  components: { Handle },
  data: () => ({
    Position,

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
  computed: {
    innerBlock() {
      // innerComponent is a defineComponent() object
      const component = this.data.node.innerComponent;
      return component;
    }
  },
  emits: ["needs-reprocess", "updateNodeInternals"],
  props: {
    data: {
      type: Object as () => { node: NodeTemplate },
      required: true,
    }
  },
  methods: {
    onNeedsReprocess() {
      console.log("needs reprocess");
      this.$emit("needs-reprocess");
    },
  },
});
</script>

<template>
  <Handle
    v-for="(inputLink, index) in data.node.inputs"
    type="target"
    :id="`input-${index}`"
    :position="Position.Left"
    :style="inputHandleStyle(index)"
  >
    {{ inputLink.title || `Input ${index}` }}
  </Handle>

  <div class="nodeStyle">
    <p>{{ data.node.displayName || `Unnamed Node` }}</p>
    <innerBlock node="node" />
  </div>

  <Handle
    v-for="(outputLink, index) in data.node.outputs"
    type="source"
    :id="`output-${index}`"
    :position="Position.Right"
    :style="outputHandleStyle(index)"
  >
    {{ outputLink.title|| `Output ${index}` }}
  </Handle>
</template>

<style lang="scss">
.nodeStyle {
  border-radius: 5px;
  color: black;
  background-color: #bddde9;
  padding: 10px;
  text-align: center;
  border: 1px solid #333;
}
</style>
