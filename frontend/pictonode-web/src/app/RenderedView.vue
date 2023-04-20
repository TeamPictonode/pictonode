<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { defineComponent } from "vue";
import * as download from "downloadjs";
import { savePipeline } from "../api";

function update(canvas: HTMLCanvasElement, img: HTMLCanvasElement | undefined) {
  const ctx = canvas.getContext("2d");
  if (ctx) {
    console.log(img);
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
      ctx.fillStyle = "transparent";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
  }
}

export default defineComponent({
  props: ["img", "pipeline"],
  mounted() {
    // @ts-ignore
    update(this.$refs.inner, this.img);
  },
  watch: {
    img() {
      // @ts-ignore
      update(this.$refs.inner, this.img);
    },
  },
  methods: {
    save() {
      // @ts-ignore
      const inner: HTMLCanvasElement = this.$refs.inner;

      // Save to blob.
      inner.toBlob((blob) => {
        if (blob) {
          download(blob, "rendered.png", "image/png");
        }
      }, "image/png");
    },
    saveToFile() {
      savePipeline(this.pipeline).then(res => {
        download(res, "pipeline.zip", "application/zip");
      })
    },
  },
});
</script>

<template>
  <div class="rendered-view">
    <v-container>
      <v-row no-gutters>
        <v-col sm="8">
          <canvas
            id="imgview"
            ref="inner"
            width="400"
            height="400"
            margin-right="30rem"
            @click="save"
          >
            <v-tooltip activator="parent" location="top"
              >Try Uploading an Image to the Image input, click to save</v-tooltip
            >
          </canvas>
        </v-col>
        <v-col sm="4">
          <v-list>
            <v-list-item @click="saveToFile">
              Save Pipeline to File
            </v-list-item>
          </v-list>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<style scoped lang="scss">
.rendered-view {
  display: block;
  margin-left: auto;
  margin-right: auto;
  margin-bottom: 10%;
  width: 40%;
}
</style>
