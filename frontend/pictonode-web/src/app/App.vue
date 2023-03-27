<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { defineComponent } from "vue";
import RenderedView from "./RenderedView.vue";
import Topbar from "./Topbar.vue";
import Widgets from "./Widgets.vue";

export default defineComponent({
  components: { RenderedView, Topbar, Widgets },
});
</script>

<template>
  <v-app :id="'pictonode'">
    <Topbar />
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<style>
#pictonode {
  background-image: linear-gradient(45deg, #cfcaca 25%, transparent 25%), linear-gradient(-45deg, #cfcaca 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #cfcaca 75%), linear-gradient(-45deg, transparent 75%, #cfcaca 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
}
</style>
