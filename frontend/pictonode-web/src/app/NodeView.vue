<!-- GNU AGPL v3 License -->
<script lang="ts">
import { Position, VueFlow } from '@vue-flow/core';
import { Controls } from "@vue-flow/additional-components";
import { defineComponent, markRaw } from "vue";
import CompositeNode from "../components/nodes/Composite.vue";

const ELEMENTS = [
    { 
        id: '1', 
        type: 'input', 
        label: 'Input Image', 
        position: { x: 250, y: 5 },
        sourcePosition: Position.Right
    },
    {
        id: '2',
        type: 'input',
        label: 'Solid Color',
        position: { x: 250, y: 100 },
        sourcePosition: Position.Right,
    },
    {
        id: '3',
        type: 'composite',
        label: 'Composite Images',
        position: { x: 450, y: 50 },
    },
    {
        id: '4',
        type: 'output',
        label: 'Render Image',
        position: { x: 650, y: 50 },
        targetPosition: Position.Left,
    },
    {
        id: 'e1-3',
        source: '1',
        target: '3',
        targetHandle: 'top',
    },
    {
        id: 'e2-3',
        source: '2',
        target: '3',
        targetHandle: 'bottom',
    },
    {
        id: 'e3-4',
        source: '3',
        target: '4',
    }
];

export default defineComponent({
    components: { CompositeNode, Controls, VueFlow },
    data: () => ({
        elements: ELEMENTS,
    }),
});
</script>

<template>
  <VueFlow id="nodeContainer" v-model="elements">
    <template #node-composite="props">
      <CompositeNode v-bind="props" />
    </template>
    <Controls />
  </VueFlow>
</template>

<style scoped>
.vue-flow {
    border: 1px solid black;
    background-color: gray;
}
</style>