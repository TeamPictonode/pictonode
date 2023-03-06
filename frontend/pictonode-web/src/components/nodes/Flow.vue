<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts" setup>
import {
  Position,
  VueFlow,
  Connection,
  Edge,
  useVueFlow,
} from "@vue-flow/core";
import { Controls } from "@vue-flow/additional-components";
import { defineComponent, defineProps, defineEmits, watch, ref } from "vue";
import NodeRepr from "./NodeRepr.vue";
import { processPipeline, savePipeline as apiSavePipeline, loadPipeline as apiLoadPipeline } from "../../api";
import { nodeTemplates } from "./NodeTypes";
import { getPipeline, SpecificData, SpecificDataType, loadPipeline as gLoadPipeline } from "./getPipeline";
//import download from "downloadjs";

let id = 0;

const elements = ref([
  _templateToNode("input", 100, 100),
  _templateToNode("output", 300, 100),
  {
    id: "1000000",
    source: "0",
    target: "1",
    sourceHandle: "output-0",
    targetHandle: "input-0",
    data: {
      realId: 1000000,
      isEdge: true,
    },
  },
]);

const onConnect = (edge: any) => {
  // Remove an existing connection that the output nodes have.
  // This is a hack to prevent the user from connecting multiple
  // nodes to the same output.
  const outputNode = edge.target;
  const outputHandle = edge.targetHandle;

  const newEdges = elements.value.filter((e) => {
    if (e.data.isEdge) {
      return e.target !== outputNode || e.targetHandle !== outputHandle;
    }
    return true;
  });

  const newId = id++;
  const newEdge = {
    ...edge,
    id: newId.toString(),
    data: {
      realId: newId,
      isEdge: true,
    },
  };
  newEdges.push(newEdge);
  elements.value = newEdges;
  processCanvas();
};

const props = defineProps({
  addDirective: String as () => string | null,
});

// Watch for changes to the addTemplate prop.
// If it is not null, add a new node with the given template.
watch(
  () => props.addDirective,
  (directive) => {
    if (directive) {
      // If it starts with "add", add a new node.
      if (directive.startsWith("add:")) {
        const template = directive.substring(4);
        addNode(template);
      } else if (directive == "save") {
        savePipeline();
      } else if (directive == "load") {
        loadPipeline();
      }
    }
  }
);

const emits = defineEmits<{
  (event: "canvas-update", canvas: HTMLCanvasElement): void;
}>();

// Method for adding a new node with the given template.
// This method is called by the parent Canvas component.
const addNode = (template: string) => {
  const node = _templateToNode(template, 0, 0);
  elements.value.push(node);
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
    },
  };
  return node;
}

const specificDataMap = new Map<string, SpecificData>();

const processCanvas = () => {
  console.log("processing canvas");
  const pipeline = getPipeline(elements.value, specificDataMap);

  // Process the pipeline.
  processPipeline(pipeline).then((imageFile) => {
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
  });
};

const nodeNeedsReprocess = (id: string, data: SpecificData) => {
  specificDataMap.set(id, data);
  processCanvas();
};

const savePipeline = () => {
  const pipeline = getPipeline(elements.value, specificDataMap);
  apiSavePipeline(pipeline).then(file => {
    // Download the file.

  })
}; 

const loadPipeline = () => {
  const fileElement = document.createElement("input");
  fileElement.type = "file";

  fileElement.onchange = (event) => {
    const file = (event.target as HTMLInputElement).files![0];
    apiLoadPipeline(file).then(pipeline => {
      specificDataMap.clear();
      elements.value = gLoadPipeline(
        pipeline as any,
        specificDataMap
      );

      processCanvas();
    })
  };

  fileElement.click();
}
</script>

<template>
  <div style="height: 50%">
    <VueFlow id="nodeContainer" v-model="elements" @connect="onConnect">
      <Controls />
      <template #node-repr="props">
        <NodeRepr
          v-bind="props"
          @needs-reprocess="
            (data) => {
              nodeNeedsReprocess(props.id, data);
            }
          "
        />
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
