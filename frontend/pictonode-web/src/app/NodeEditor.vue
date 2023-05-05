<template>
  <div>
    <RenderedView :img="img" :pipeline="pipeline" :setPipeline="setPipeline" />
  </div>
  <div class="b">
      <v-btn
              rounded="pill"
              color="#474545"
              @click="prettify()"
              style="color: white"
              >Prettify</v-btn
            >
    <v-btn
      rounded="pill"
      color="#474545"
      @click="saveToFile"
      style="color: white"
      >Save to File</v-btn
    >
    <v-btn
      rounded="pill"
      color="#474545"
      @click="saveToServer"
      style="color: white"
      >Save to Server</v-btn
    >
    <v-btn
      rounded="pill"
      color="#474545"
      @click="loadFromFile"
      style="color: white"
      >Load from File</v-btn
    >
    <baklava-editor :plugin="viewPlugin" />
  </div>
</template>

<script lang="ts">
import { ViewPlugin } from "@baklavajs/plugin-renderer-vue3";
import { Editor } from "@baklavajs/core";
import { OptionPlugin } from "@baklavajs/plugin-options-vue3";
import { Engine } from "@baklavajs/plugin-engine";
import { defineComponent } from "vue";
import { setForceUpdate } from "../forceUpdate";

import {
  ImageNode,
  RenderedNode,
  InvertNode,
  CompositeNode,
  BriCon,
  GaussBlur,
} from "../components/nodes/BaklavaNodes";
import InputNode from "../components/nodes/NodeData/InputNode.vue";
import getPipeline, { installPipeline } from "../components/nodes/getPipeline";
import { processPipeline } from "../api";
import ValueTracker from "../components/nodes/ValueTracker";
import { savePipeline, loadPipeline, uploadProject } from "../api";
import * as download from "downloadjs";

import RenderedView from "./RenderedView.vue";

export default defineComponent({
  components: { RenderedView, InputNode },
  data: () => ({
    img: undefined as HTMLCanvasElement | undefined,
    editor: new Editor() as Editor,
    viewPlugin: new ViewPlugin() as ViewPlugin,
    engine: new Engine(true) as Engine,
  }),
  computed: {
    pipeline() {
      // @ts-ignore
      return getPipeline(this.editor);
    },
  },
  created() {
    this.editor.use(this.viewPlugin);
    this.editor.use(new OptionPlugin());
    this.editor.use(this.engine);

    this.viewPlugin.enableMinimap = true;

    // @ts-ignore
    this.viewPlugin.registerOption("UploadOption", InputNode);

    this.editor.registerNodeType("ImageNode", ImageNode);
    this.editor.registerNodeType("RenderedNode", RenderedNode);
    this.editor.registerNodeType("InvertNode", InvertNode);
    this.editor.registerNodeType("Composite", CompositeNode);
    this.editor.registerNodeType("Brightness/Contrast", BriCon);
    this.editor.registerNodeType("Gauss Blur", GaussBlur);
    const node1 = this.addNodeWithCoordinates(ImageNode, 100, 140);
    const node2 = this.addNodeWithCoordinates(RenderedNode, 1000, 140);

    // Update the rendered view when the engine ticks.
    const pictosymbol = Symbol("Pictonode Event Listener");
    this.editor.events.addConnection.addListener(pictosymbol, () =>
      this.onUpdate()
    );
    this.editor.events.addNode.addListener(pictosymbol, () => this.onUpdate());
    this.editor.events.removeConnection.addListener(pictosymbol, () =>
      this.onUpdate()
    );
    this.editor.events.removeNode.addListener(pictosymbol, () =>
      this.onUpdate()
    );

    this.engine.calculate();
    setForceUpdate(this.onUpdate);
  },
  methods: {
    addNodeWithCoordinates(nodeType: any, x: any, y: any) {
      const n = new nodeType();
      this.editor.addNode(n);
      n.position.x = x;
      n.position.y = y;
      return n;
    },
    

    setPipeline(pipeline: any) {
      // @ts-ignore
      installPipeline(this.editor, pipeline);
      this.onUpdate();
    },

    onUpdate() {
      // Convert the pipeline to the pictonode format.
      // @ts-ignore
      const pipeline = getPipeline(this.editor);

      // Process the pipeline.
      processPipeline(pipeline)
        .then((img) => {
          // Cast the file into an image.
          const image = new Image();
          image.src = URL.createObjectURL(img);

          image.onload = () => {
            // Cast the image into a canvas.
            const canvas = document.createElement("canvas");
            canvas.width = image.width;
            canvas.height = image.height;
            const ctx = canvas.getContext("2d");
            if (ctx) {
              ctx.drawImage(image, 0, 0);
              this.img = canvas;
            }
          };
        })
        .catch((err) => {
          // Try to load the file at "/error_icon.png" and use that.
          const image = new Image();
          image.src = "/error_icon.png";

          image.onload = () => {
            // Cast the image into a canvas.
            const canvas = document.createElement("canvas");
            const actualWidth = 50;
            const actualHeight = (actualWidth / image.width) * image.height;
            canvas.width = actualWidth;
            canvas.height = actualHeight;
            const ctx = canvas.getContext("2d");
            if (ctx) {
              ctx.drawImage(image, 0, 0, actualWidth, actualHeight);
              this.img = canvas;
            }
          };

          image.onerror = () => {
            // Instead make a canvas that says "no image".
            const canvas = document.createElement("canvas");
            canvas.width = 800;
            canvas.height = 600;
            const ctx = canvas.getContext("2d");

            if (ctx) {
              // Draw a black background.
              ctx.fillStyle = "black";
              ctx.fillRect(0, 0, 800, 600);

              // Draw the text "NO IMAGE"
              ctx.font = "60px Arial";
              ctx.fillStyle = "white";
              ctx.fillText("NO IMAGE", 100, 50);

              // Draw a frowny face.
              ctx.strokeStyle = "white";
              ctx.beginPath();
              ctx.arc(400, 300, 100, 0, 2 * Math.PI);
              ctx.stroke();
              ctx.beginPath();
              ctx.arc(350, 250, 10, 0, 2 * Math.PI);
              ctx.stroke();
              ctx.beginPath();
              ctx.arc(450, 250, 10, 0, 2 * Math.PI);
              ctx.stroke();
              ctx.beginPath();
              ctx.moveTo(350, 350);
              ctx.lineTo(450, 350);
              ctx.stroke();

              this.img = canvas;
            }
          };
        });
    },
    saveToFile() {
      savePipeline(this.pipeline).then((res) => {
        download(res, "pipeline.zip", "application/zip");
      });
    },
    loadFromFile() {
      // Open a file dialog.
      const input = document.createElement("input");
      input.type = "file";
      input.accept = ".zip";

      input.onchange = (e) => {
        const file = (e.target as HTMLInputElement).files?.[0];
        if (file) {
          loadPipeline(file).then((res) => {
            this.setPipeline(res);
          });
        }
      };

      input.click();
    },
    saveToServer() {
      savePipeline(this.pipeline).then((res) => {
        uploadProject(
          `untitled_${Math.floor(Math.random() * 1000000)}`,
          "Untitled Project",
          res
        );
      });
    },

    prettify() {
     //position does exist you liar
     var nodes = this.editor.nodes
     var sortedNodes = []
     var i, j, temp;
     var swapped;

     for(i=0; i < nodes.length; i++) {
      swapped = false;
      for (j = 0; j < nodes.length - i - 1; j++) {
        if (nodes[j].position.x > nodes[j + 1].position.x)
                {
                    // swap arr[j] and arr[j+1]
                    temp = nodes[j];
                    sortedNodes[j] = nodes[j + 1];
                    sortedNodes[j + 1] = temp;
                    swapped = true;
                }
        else {
          sortedNodes[j] = nodes[j]
        }
      
      if (swapped == false) {
        break;
      }
     }}}
  },
});

</script>
<style>
.b {
  height: 90%;
  width: 100vw;
  position: relative;
  border-top: 10px solid black;
}
.hint {
    position: absolute;
    top: 1rem;
    left: 1rem;
    z-index: 5;
    padding: 1rem;
    background: transparent;
    color: white;
    pointer-events: none;
}
</style>
