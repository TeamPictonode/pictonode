<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { computed, defineComponent } from "vue";
import NodeView from "../components/nodes/Flow.vue";
import RenderedView from "./RenderedView.vue";
import Topbar from "./Topbar.vue";
import Widgets from "./Widgets.vue";

export default defineComponent({
  components: { NodeView, RenderedView, Topbar, Widgets },
  data: () => ({
    img: undefined as HTMLCanvasElement | undefined,
  }),
  methods: {
    onCanvasUpdate(canvas: HTMLCanvasElement) {
      console.log("updated img canvas");
      console.log(canvas);
      this.img = canvas;
    },
    addNode(template: string) {
      // Get the Flow component
      // You're not supposed to use internal methods, but the alternative is
      // horrifying.
      const flow = this.$refs.flow as any;

      // Add a node to the flow
      flow.addNode(template);
    } 
  }
});
</script>

<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col cols="6">
        <RenderedView :img="img" />
      </v-col>
      <v-col cols="6">
        <Widgets
          @input="addNode"
        />
      </v-col>
    </v-row>
  </v-container>
  <NodeView
    @canvas-update="onCanvasUpdate"
    ref="flow"
  />
</template>
