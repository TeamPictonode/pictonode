<!-- GNU AGPL v3 License -->

<script lang="ts">
import { Position, VueFlow } from '@vue-flow/core';
import { Controls } from '@vue-flow/additional-components';
import { defineComponent } from 'vue';
import NodeRepr from './NodeRepr.vue';
import { defaultPipeline, pipelineToVueFlow, SpecialNodeType, MetadataType, NodeDataType } from './NodeTree';

const pipeline = defaultPipeline();
const elements = pipelineToVueFlow(pipeline);

console.log(elements);

export default defineComponent({
    components: { NodeRepr, VueFlow, Controls },
    data: () => ({
        elements,
        pipeline
    }),
    emits: ['canvas-update', 'updateNodeInternals'],
    methods: {
        processCanvas() {
            console.log("processing canvas");
            // Get the "output" node for the pipeline.
            let outputNode;

            for (const node of this.pipeline.getNodes()) {
                const template = node.getTemplate();

                if (template === "output") {
                    outputNode = node;
                    break;
                }
            }

            if (!outputNode) {
                throw new Error('No output node found');
            }

            // Get the first input link and get the canvas from it.
            const inputLink = outputNode.getInputs()[0];
            const data = inputLink.get();
            console.log(data);
            if (data.type !== NodeDataType.Image) {
                throw new Error('Output node does not have an image input');
            }

            this.$emit('canvas-update', data.canvas);
        }
    },
    mounted() {
        this.processCanvas();
    },
});
</script>

<template>
  <VueFlow id="nodeContainer" v-model="elements">
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
