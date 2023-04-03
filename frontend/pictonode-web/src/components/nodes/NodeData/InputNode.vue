<!-- GNU AGPL v3 License -->
<!-- Written by John Nunley -->

<script lang="ts">
import { defineComponent } from "vue";
import { uploadImage } from "../../../api";

import { srcImgs } from "../CalculateNodes";

export default defineComponent({
  data: () => ({
    imgName: "image",
    fileExists: false,
  }),
  methods: {
    onFileChange(e: any) {
      console.log("made it to on file change");
      const file = e.target.files[0];
      this.imgName = file.name;
      this.fileExists = true;

      uploadImage(file).then((id) => {
        srcImgs.push(id);
      });
    },
  },
});
</script>

<template>
  <label htmlFor="image">
    {{ imgName }}
    <input
      v-if="!fileExists"
      type="file"
      id="file"
      name="file"
      placeholder="Upload an Image"
      required
      v-on:change="onFileChange"
    />
  </label>
</template>
