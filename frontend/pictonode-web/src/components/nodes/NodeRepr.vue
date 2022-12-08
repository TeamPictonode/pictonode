<!-- GNU AGPL v3 License -->

<script lang="ts">
import { Handle, Position } from "@vue-flow/core";
import { defineComponent } from "vue";

import { Node as GraphNode } from "./NodeTree";

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
    props: {
        node: {
            type: Object as () => GraphNode,
            required: true,
        },
    }
});
</script>

<template>
  <Handle
      v-for="(inputLink, index) in node.getInputs()"
      type="target"
      :id="`input-${index}`"
      :position="Position.Left"
      :style="inputHandleStyle(index)"
      >
    {{ inputLink.getMetadata().title || `Input ${index}` }}
  </Handle>

  <div class="nodeStyle">
    <p>{{ node.getMetadata().title || `Unnamed Node` }}</p>
  </div>

  <Handle
        v-for="(outputLink, index) in node.getOutputs()"
        type="source"
        :id="`output-${index}`"
        :position="Position.Right"
        :style="outputHandleStyle(index)"
      >
    {{ outputLink.getMetadata().title || `Output ${index}` }}
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