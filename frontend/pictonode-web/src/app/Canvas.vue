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
    addDirective: null as string | null,
  }),
  methods: {
    onCanvasUpdate(canvas: HTMLCanvasElement) {
      console.log("updated img canvas");
      console.log(canvas);
      this.img = canvas;
    },
    addNode(template: string) {
      this.addDirective = `add:${template}`;
    },
    savePipeline() {
      this.addDirective = "save";
    },
    loadPipeline() {
      this.addDirective = "load";
    },
  },
});
</script>

<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col cols="4">
        <RenderedView :img="img" />
      </v-col>
      <v-col cols="4">
        <Widgets @input="addNode" />
      </v-col>
      <v-col cols="4">
        <v-list>
          <v-list-item>
            <v-list-item-content>
              <v-button @click="savePipeline">Save Pipeline</v-button>
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>
              <v-button @click="loadPipeline">Load Pipeline</v-button>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-col>
    </v-row>
  </v-container>
  <NodeView
    @canvas-update="onCanvasUpdate"
    ref="flow"
    :addDirective="addDirective"
  />
</template>
