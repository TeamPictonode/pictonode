<!-- GNU AGPL v3 License -->
<script lang="ts">
  import { defineComponent } from 'vue';
  import NodeView from "./NodeView.vue";
  import RenderedView from "./RenderedView.vue";
  import Topbar from "./Topbar.vue";
  import Widgets from "./Widgets.vue";

  export default defineComponent({
    components: { NodeView, RenderedView, Topbar, Widgets },
    data: () => ({
      img: undefined as HTMLImageElement | undefined,
    }),
    methods: {
        onFileChange(event: Event) {
            // @ts-ignore
            const file = event.target.files[0];
            this.img = document.createElement("img");
            this.img.src = URL.createObjectURL(file);
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
        <Widgets />
      </v-col>
    </v-row>
  </v-container>
  <NodeView />
  <v-file-input @change="onFileChange" />
</template>
