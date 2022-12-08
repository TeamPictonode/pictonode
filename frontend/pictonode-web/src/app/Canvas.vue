<!-- GNU AGPL v3 License -->
<script lang="ts">
import { defineComponent } from "vue";
import NodeView from "../components/nodes/Flow.vue";
import RenderedView from "./RenderedView.vue";
import Topbar from "./Topbar.vue";
import Widgets from "./Widgets.vue";

export default defineComponent({
  components: { NodeView, RenderedView, Topbar, Widgets },
  data: () => ({
    img: undefined as HTMLCanvasElement | undefined,
    ticks: 0,
    pendingTemplates: [] as string[],
  }),
  methods: {
    onCanvasUpdate(canvas: HTMLCanvasElement) {
      console.log("updated img canvas");
      this.img = canvas;
      this.ticks += 1;
    },
    updatePendingTemplates(pt: string[]) {
      this.pendingTemplates = pt;
    },
  },
});
</script>

<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col cols="6">
        <RenderedView :img="img" :ticks="ticks" />
      </v-col>
      <v-col cols="6">
        <Widgets
          :pendingTemplates="pendingTemplates"
          @input="updatePendingTemplates"
        />
      </v-col>
    </v-row>
  </v-container>
  <NodeView
    @canvas-update="onCanvasUpdate"
    :pendingTemplates="pendingTemplates"
  />
</template>
