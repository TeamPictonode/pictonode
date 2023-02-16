<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { defineComponent } from "vue";

function update(canvas: HTMLCanvasElement, img: HTMLCanvasElement | undefined) {
  const ctx = canvas.getContext("2d");
  if (ctx) {
    console.log(`got img: ${img}`);
    if (img) {
      console.log("drawing image");

      let widthScale = 1;
      let heightScale = 1;

      // If the width is greater than 500 px, scale down.
      if (img.width > 500) {
        widthScale = 500 / img.width;
      }

      // If the height is greater than 500 px, scale down.
      if (img.height > 500) {
        heightScale = 500 / img.height;
      }

      const scale = Math.min(widthScale, heightScale);

      // Scale down the image.
      canvas.width = img.width * scale;
      canvas.height = img.height * scale;

      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    } else {
      ctx.fillStyle = "red";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
  }
}

export default defineComponent({
  props: ["img", "ticks"],
  mounted() {
    // @ts-ignore
    update(this.$refs.inner, this.img);
  },
  watch: {
    img() {
      // @ts-ignore
      update(this.$refs.inner, this.img);
    },
    ticks() {
      // This is a bogus hack, please fix!

      // @ts-ignore
      update(this.$refs.inner, this.img);
    },
  },
});
</script>

<template>
  <v-card ref="toplevel" class="mx-auto" id="rendered-view" tile color="#e1e9d0">
    <canvas ref="inner" width="200" height="100">
      <v-tooltip activator="parent" location="top">Try Uploading an Image to the Image input</v-tooltip>
    </canvas>
  </v-card>
</template>

<style scoped lang="scss">
#rendered-view {
  padding: 1rem;
  margin: 1rem;
}
</style>
