<template>
  <div>
    <RenderedView :img="img"/>
  </div>
  <div class="b">
        <baklava-editor :plugin="viewPlugin" />
    </div>
</template>

<script lang="ts">
  import { ViewPlugin } from "@baklavajs/plugin-renderer-vue3";
  import { Editor } from "@baklavajs/core";
  import { OptionPlugin } from "@baklavajs/plugin-options-vue3";
  import { Engine } from "@baklavajs/plugin-engine";
  import { defineComponent } from "vue";

  import { DisplayNode } from "../components/nodes/DisplayNode";
  import { MathNode, ImageNode, RenderedNode } from "../components/nodes/BaklavaNodes";
  import  InputNode  from "../components/nodes/NodeData/InputNode.vue";

  import RenderedView from "./RenderedView.vue";

  export default defineComponent({
    components: { RenderedView, InputNode },
    data: () => ({
    img: undefined as HTMLCanvasElement | undefined,
    editor: new Editor(),
    viewPlugin: new ViewPlugin(),
    engine: new Engine(true),
  }),
  created () {
    this.editor.use(this.viewPlugin);
    this.editor.use(new OptionPlugin());
    this.editor.use(this.engine);
    this.viewPlugin.enableMinimap = true;

    this.viewPlugin.registerOption("ButtonOption", InputNode);

    this.editor.registerNodeType("DisplayNode", DisplayNode);
    this.editor.registerNodeType("MathNode", MathNode);
    this.editor.registerNodeType("ImageNode", ImageNode);
    this.editor.registerNodeType("RenderedNode", RenderedNode);
    const node1 = this.addNodeWithCoordinates(MathNode, 100, 140);
    const node2 = this.addNodeWithCoordinates(DisplayNode, 400, 140);
    const node3 = this.addNodeWithCoordinates(ImageNode, 300, 160);
    this.editor.addConnection(node1.getInterface("Result"), node2.getInterface("Value"));
    this.engine.calculate();

  },
  methods: {
        addNodeWithCoordinates(nodeType: any, x: any, y: any) {
            const n = new nodeType();
            this.editor.addNode(n);
            n.position.x = x;
            n.position.y = y;
            return n;
        }
  }
  });

</script>
<style>
  .b {
    height: 90%;
    width: 100vw;
    position: relative;
  }
</style>