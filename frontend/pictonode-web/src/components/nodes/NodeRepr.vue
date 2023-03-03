<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts" setup>
import { Handle, Position } from "@vue-flow/core";
import { defineProps, defineEmits } from "vue";

import { NodeTemplate } from "./NodeTypes";
import { SpecificData } from "./getPipeline";

function inputHandleStyle(index: number) {
  return {
    top: `${index * 20 + 10}px`,
  };
}

function outputHandleStyle(index: number) {
  return {
    top: `${index * 20 + 10}px`,
  };
}

const props = defineProps<{
  data: { node: NodeTemplate };
}>();

const emits = defineEmits<{
  (event: "needs-reprocess", data: SpecificData): void;
}>();

function onNeedsReprocess(data: SpecificData): true {
  console.log("needs reprocess");
  emits("needs-reprocess", data);
  return true;
}

const innerBlock = props.data.node.innerComponent;
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
    <innerBlock node="node" @updated="onNeedsReprocess" />
  </div>

  <Handle
    v-for="(outputLink, index) in data.node.outputs"
    type="source"
    :id="`output-${index}`"
    :position="Position.Right"
    :style="outputHandleStyle(index)"
  >
    {{ outputLink.title || `Output ${index}` }}
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
